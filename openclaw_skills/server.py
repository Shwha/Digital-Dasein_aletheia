"""HTTP server mode — exposes the skill pipeline as a local REST API.

This is the bridge between OpenClaw (Node.js) and the Python pipeline.
The agent calls these endpoints before/after tool execution, and the
pipeline returns approve/reject/escalate decisions.

Endpoints:
  POST /validate    — Validate pending tool calls (pre-execution)
  POST /report      — Report completed tool calls (post-execution)
  POST /plan        — Submit or check a change plan
  GET  /state       — Get current session state summary
  GET  /health      — Health check
  GET  /skills      — List available skills

Security:
  - Binds to 127.0.0.1 ONLY — never exposed to network
  - No authentication needed (localhost only)
  - All requests logged to audit trail
"""

from __future__ import annotations

import asyncio
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from threading import Thread
from typing import Any

from openclaw_skills.config import load_pipeline_config
from openclaw_skills.logging import configure_logging, get_logger
from openclaw_skills.models import (
    PipelinePhase,
    SkillContext,
    StateVector,
    ToolCallRecord,
    ToolCallRequest,
)
from openclaw_skills.pipeline import SkillPipeline
from openclaw_skills.registry import SkillRegistry
from openclaw_skills.security import AuditWriter, sanitize_text

logger = get_logger(__name__)

# Module-level references set by start_server()
_pipeline: SkillPipeline | None = None
_registry: SkillRegistry | None = None
_audit: AuditWriter | None = None
_loop: asyncio.AbstractEventLoop | None = None


class PipelineHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the pipeline API."""

    def do_GET(self) -> None:
        if self.path == "/health":
            self._json_response({"status": "ok", "version": "0.1.0"})
        elif self.path == "/skills":
            self._handle_list_skills()
        elif self.path.startswith("/state"):
            self._handle_get_state()
        else:
            self._json_response({"error": "Not found"}, status=404)

    def do_POST(self) -> None:
        if self.path == "/validate":
            self._handle_validate()
        elif self.path == "/report":
            self._handle_report()
        elif self.path == "/plan":
            self._handle_plan()
        else:
            self._json_response({"error": "Not found"}, status=404)

    def _handle_validate(self) -> None:
        """Validate pending tool calls through the pipeline.

        Request body:
        {
            "session_id": "...",
            "tool_calls": [
                {"tool_name": "...", "parameters": {...}}
            ],
            "prompt": "...",          // optional: current prompt
            "state": {                // optional: StateVector overrides
                "urgency": 0.5,
                "confidence": 0.7
            }
        }

        Response:
        {
            "approved": true/false,
            "escalation_required": true/false,
            "escalation_reason": "...",
            "rejected_calls": [...],
            "warnings": [...],
            "convergence_score": 0.0,
            "uci": 0.0,
            "state_summary": "..."
        }
        """
        body = self._read_body()
        if body is None:
            return

        # Build context
        tool_calls = [
            ToolCallRequest(
                tool_name=tc.get("tool_name", ""),
                parameters=tc.get("parameters", {}),
            )
            for tc in body.get("tool_calls", [])
        ]

        state_overrides = body.get("state", {})
        state = StateVector(**{
            k: v for k, v in state_overrides.items()
            if k in StateVector.model_fields
        })

        context = SkillContext(
            session_id=body.get("session_id", "default"),
            phase=PipelinePhase.PRE_TOOL,
            original_prompt=sanitize_text(body.get("prompt", "")),
            pending_tool_calls=tool_calls,
            state_vector=state,
        )

        # Run pipeline
        assert _pipeline is not None and _loop is not None
        future = asyncio.run_coroutine_threadsafe(
            _pipeline.execute(context), _loop
        )
        result_ctx = future.result(timeout=30)

        # Build response
        rejected = [
            {"tool_name": tc.tool_name, "error": tc.error}
            for tc in result_ctx.completed_tool_calls
            if not tc.success
        ]

        warnings = []
        for sr in result_ctx.skill_results:
            warnings.extend(sr.warnings)

        self._json_response({
            "approved": not result_ctx.escalation_required and len(rejected) == 0,
            "escalation_required": result_ctx.escalation_required,
            "escalation_reason": result_ctx.escalation_reason,
            "rejected_calls": rejected,
            "approved_calls": [
                {"tool_name": tc.tool_name, "parameters": tc.parameters}
                for tc in result_ctx.pending_tool_calls
            ],
            "warnings": warnings,
            "convergence_score": result_ctx.convergence_score,
            "uci": result_ctx.current_uci,
            "state_summary": result_ctx.metadata.get("state_summary", ""),
        })

    def _handle_report(self) -> None:
        """Report completed tool calls for post-execution tracking.

        Request body:
        {
            "session_id": "...",
            "completed_calls": [
                {"tool_name": "...", "parameters": {...}, "success": true, "result_summary": "..."}
            ]
        }
        """
        body = self._read_body()
        if body is None:
            return

        completed = [
            ToolCallRecord(
                id=f"ext-{i}",
                tool_name=tc.get("tool_name", ""),
                parameters=tc.get("parameters", {}),
                success=tc.get("success", True),
                result_summary=sanitize_text(tc.get("result_summary", "")),
                error=tc.get("error", ""),
            )
            for i, tc in enumerate(body.get("completed_calls", []))
        ]

        context = SkillContext(
            session_id=body.get("session_id", "default"),
            phase=PipelinePhase.POST_TOOL,
            completed_tool_calls=completed,
            modified_files=body.get("modified_files", []),
        )

        assert _pipeline is not None and _loop is not None
        future = asyncio.run_coroutine_threadsafe(
            _pipeline.execute(context), _loop
        )
        result_ctx = future.result(timeout=30)

        self._json_response({
            "acknowledged": True,
            "warnings": [
                w for sr in result_ctx.skill_results for w in sr.warnings
            ],
            "uci": result_ctx.current_uci,
            "drift_score": result_ctx.state_vector.drift_score,
        })

    def _handle_plan(self) -> None:
        """Submit or query a change plan.

        Request body:
        {
            "session_id": "...",
            "action": "create" | "approve" | "status",
            "description": "...",
            "steps": ["step 1", "step 2"]
        }
        """
        body = self._read_body()
        if body is None:
            return

        # For now, acknowledge plan submissions
        # Full integration requires ChangePlanner wiring
        self._json_response({
            "acknowledged": True,
            "action": body.get("action", "status"),
            "message": "Plan management available — full workflow in next release",
        })

    def _handle_list_skills(self) -> None:
        """List all available skills."""
        assert _registry is not None
        self._json_response({
            "skills": _registry.list_available(),
        })

    def _handle_get_state(self) -> None:
        """Get session state summary."""
        # Parse session_id from query string
        session_id = "default"
        if "?" in self.path:
            params = dict(
                p.split("=", 1)
                for p in self.path.split("?", 1)[1].split("&")
                if "=" in p
            )
            session_id = params.get("session_id", "default")

        self._json_response({
            "session_id": session_id,
            "message": "Session state tracking active",
        })

    def _read_body(self) -> dict[str, Any] | None:
        """Read and parse JSON request body."""
        try:
            length = int(self.headers.get("Content-Length", 0))
            if length == 0:
                self._json_response({"error": "Empty request body"}, status=400)
                return None
            raw = self.rfile.read(length).decode("utf-8")
            return json.loads(raw)
        except (json.JSONDecodeError, ValueError) as e:
            self._json_response({"error": f"Invalid JSON: {e}"}, status=400)
            return None

    def _json_response(self, data: dict[str, Any], status: int = 200) -> None:
        """Send a JSON response."""
        body = json.dumps(data, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: Any) -> None:
        """Route HTTP logs through structlog instead of stderr."""
        logger.debug("http_request", message=format % args)


async def _init_pipeline(config_path: Path) -> tuple[SkillPipeline, SkillRegistry]:
    """Initialize the skill pipeline from config."""
    registry = SkillRegistry()
    registry.discover_entry_points()

    audit = AuditWriter(".openclaw/audit")

    pipeline = await SkillPipeline.from_config(
        config_path, registry, audit_writer=audit
    )

    return pipeline, registry


def start_server(
    host: str = "127.0.0.1",
    port: int = 8901,
    config_path: str = "configs/default.yaml",
) -> None:
    """Start the HTTP server.

    Binds to localhost ONLY — never exposed to network.
    """
    global _pipeline, _registry, _audit, _loop

    configure_logging(log_format="console")

    # Initialize async pipeline in a dedicated event loop
    _loop = asyncio.new_event_loop()

    def run_loop() -> None:
        assert _loop is not None
        asyncio.set_event_loop(_loop)
        _loop.run_forever()

    loop_thread = Thread(target=run_loop, daemon=True)
    loop_thread.start()

    # Initialize pipeline
    future = asyncio.run_coroutine_threadsafe(
        _init_pipeline(Path(config_path)), _loop
    )
    _pipeline, _registry = future.result(timeout=30)

    # Start HTTP server
    server = HTTPServer((host, port), PipelineHandler)
    logger.info(
        "server_started",
        host=host,
        port=port,
        config=config_path,
        url=f"http://{host}:{port}",
    )

    print(f"OpenClawSkills pipeline server running at http://{host}:{port}")
    print(f"Config: {config_path}")
    print("Press Ctrl+C to stop.")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()
        if _loop:
            _loop.call_soon_threadsafe(_loop.stop)
