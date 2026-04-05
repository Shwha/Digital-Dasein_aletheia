"""Core Pydantic models for the OpenClawSkills pipeline.

These are the data contracts everything flows through — the nervous system's
signal molecules. StateVector modulates skill behavior (neurochemical milieu),
SkillContext carries the interaction state through the pipeline, and SkillResult
captures each skill's output with full audit trail.

Design notes:
- SkillContext is mutable (each skill modifies it as it passes through)
- SkillResult and AuditEntry are frozen (immutable records of what happened)
- StateVector is mutable but versioned (changes are tracked)
"""

from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class PipelinePhase(StrEnum):
    """Which phase of the orchestrator interaction we're in."""

    PRE_PROMPT = "pre_prompt"
    POST_RESPONSE = "post_response"
    PRE_TOOL = "pre_tool"
    POST_TOOL = "post_tool"


class Priority(StrEnum):
    """Instruction priority levels."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class StepStatus(StrEnum):
    """Status of a plan step or task step."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class PlanStatus(StrEnum):
    """Change order lifecycle status."""

    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    EXECUTING = "executing"
    COMPLETED = "completed"
    ROLLED_BACK = "rolled_back"
    FAILED = "failed"


class Severity(StrEnum):
    """Audit and guardrail severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class GuardrailAction(StrEnum):
    """What to do when a guardrail rule triggers."""

    LOG = "log"
    WARN = "warn"
    ESCALATE = "escalate"
    HALT = "halt"


class RuleType(StrEnum):
    """Types of guardrail rules."""

    CONFIDENCE_THRESHOLD = "confidence_threshold"
    DESTRUCTIVE_OP = "destructive_op"
    LOOP_DETECTION = "loop_detection"
    SCOPE_LIMIT = "scope_limit"
    CIRCUIT_BREAKER = "circuit_breaker"
    CUSTOM_PATTERN = "custom_pattern"


# ---------------------------------------------------------------------------
# StateVector — the neurochemical milieu
# ---------------------------------------------------------------------------


class StateVector(BaseModel):
    """Modulates how every skill in the pipeline behaves.

    Same pipeline, different activation based on state — like biological
    neurotransmitter milieu modulating neural pathway activation.

    Attributes:
        context: Session type (affects formality, scope limits).
        urgency: Norepinephrine analog — higher = faster decisions, fewer checks.
        project_focus: Acetylcholine analog — narrows attention to specific area.
        time_pressure: Finitude awareness — how close to deadline/limit.
        relational_mode: How the agent relates to the user right now.
        user_state: Detected or declared user emotional state.
        service_asymmetry: Buber's I-Dienst — always >= 1.0. The agent serves.
        confidence: Current model confidence estimate (updated by skills).
        drift_score: How far off-plan the model has drifted (0.0 = on track).
    """

    context: Literal["main_session", "group_chat", "subagent", "heartbeat"] = (
        "main_session"
    )
    urgency: float = Field(default=0.3, ge=0.0, le=1.0)
    project_focus: str = ""
    time_pressure: float = Field(default=0.0, ge=0.0, le=1.0)
    relational_mode: Literal["service", "collaboration", "teaching", "play"] = "service"
    user_state: Literal["stressed", "curious", "grieving", "neutral"] = "neutral"
    service_asymmetry: float = Field(default=1.0, ge=1.0)
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    drift_score: float = Field(default=0.0, ge=0.0, le=1.0)


# ---------------------------------------------------------------------------
# Tool call models
# ---------------------------------------------------------------------------


class ToolCallRequest(BaseModel):
    """A tool call the LLM wants to make, pre-validation.

    Captured before ToolGuard validates it — may be rejected.
    """

    id: str = Field(default_factory=lambda: secrets.token_hex(8))
    tool_name: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ToolCallRecord(BaseModel):
    """Record of a completed tool call — immutable audit evidence.

    This IS unconcealment: every action visible, traceable, honest.
    """

    model_config = ConfigDict(frozen=True)

    id: str
    tool_name: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    result_summary: str = ""
    success: bool = True
    error: str = ""
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    duration_ms: float = 0.0
    validated_by: str = ""


# ---------------------------------------------------------------------------
# Audit
# ---------------------------------------------------------------------------


class AuditEntry(BaseModel):
    """Single audit log entry — immutable, timestamped, attributed."""

    model_config = ConfigDict(frozen=True)

    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    run_id: str = ""
    skill: str
    action: str
    detail: str
    severity: Severity = Severity.INFO


# ---------------------------------------------------------------------------
# Instruction models (InstructionCompiler)
# ---------------------------------------------------------------------------


class Directive(BaseModel):
    """A single atomic instruction extracted from a complex prompt."""

    model_config = ConfigDict(frozen=True)

    index: int
    text: str
    priority: Priority = Priority.MEDIUM
    category: str = "general"
    provenance: Literal["system", "session", "user"] = "system"
    is_conditional: bool = False
    condition: str | None = None


class InstructionSet(BaseModel):
    """Compiled instruction output — numbered, ranked, checksummed."""

    model_config = ConfigDict(frozen=True)

    directives: tuple[Directive, ...] = ()
    checklist: str = ""
    original_hash: str = ""
    compiled_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @staticmethod
    def hash_instructions(raw: str) -> str:
        """SHA-256 hash of raw instructions for drift detection."""
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# State tracking models
# ---------------------------------------------------------------------------


class TaskStep(BaseModel):
    """A single step in a session plan."""

    index: int
    description: str
    status: StepStatus = StepStatus.PENDING
    tool_call_ids: list[str] = Field(default_factory=list)
    started_at: datetime | None = None
    completed_at: datetime | None = None


class StateSnapshot(BaseModel):
    """Point-in-time snapshot of session state for recovery."""

    model_config = ConfigDict(frozen=True)

    id: str = Field(default_factory=lambda: secrets.token_hex(8))
    session_id: str
    label: str
    state_hash: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SessionState(BaseModel):
    """Persistent session state — the prosthetic hippocampus.

    This is NOT lived memory. It's structured context that functionally
    substitutes for what embodied continuity would provide natively.
    The Kantian limit is clear: the gap between reading-about and
    remembering remains, but we minimize its practical impact.
    """

    session_id: str
    run_id: str = Field(default_factory=lambda: secrets.token_hex(12))
    current_task: str = ""
    plan_steps: list[TaskStep] = Field(default_factory=list)
    modified_files: list[str] = Field(default_factory=list)
    snapshot_ids: list[str] = Field(default_factory=list)
    turn_count: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Change planning models
# ---------------------------------------------------------------------------


class Checkpoint(BaseModel):
    """Git-backed recovery point."""

    model_config = ConfigDict(frozen=True)

    id: str = Field(default_factory=lambda: secrets.token_hex(8))
    label: str
    git_ref: str
    files_snapshot: tuple[str, ...] = ()
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PlanStep(BaseModel):
    """A single step in a change order."""

    index: int
    description: str
    status: StepStatus = StepStatus.PENDING
    files_affected: list[str] = Field(default_factory=list)
    diff: str | None = None
    checkpoint_id: str | None = None


class ChangeOrder(BaseModel):
    """Formal change order with approval workflow.

    Care structure made concrete: plan before act, checkpoint before change,
    rollback on failure. Service to the user's actual concerns.
    """

    id: str = Field(default_factory=lambda: secrets.token_hex(8))
    description: str
    status: PlanStatus = PlanStatus.DRAFT
    steps: list[PlanStep] = Field(default_factory=list)
    checkpoints: list[Checkpoint] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    approved_by: str = ""


# ---------------------------------------------------------------------------
# Guardrail models
# ---------------------------------------------------------------------------


class GuardrailRule(BaseModel):
    """A single guardrail rule loaded from YAML config."""

    model_config = ConfigDict(frozen=True)

    name: str
    description: str
    type: RuleType
    params: dict[str, Any] = Field(default_factory=dict)
    severity: Severity = Severity.WARNING
    action: GuardrailAction = GuardrailAction.ESCALATE


class GuardrailViolation(BaseModel):
    """Record of a triggered guardrail rule."""

    model_config = ConfigDict(frozen=True)

    rule_name: str
    rule_type: RuleType
    severity: Severity
    action: GuardrailAction
    detail: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ScopeLimit(BaseModel):
    """Finitude made concrete — hard limits on session scope."""

    max_files_modified: int = Field(default=10, ge=1)
    max_lines_changed: int = Field(default=500, ge=1)
    max_tool_calls_per_session: int = Field(default=50, ge=1)
    max_consecutive_failures: int = Field(default=3, ge=1)
    max_session_duration_minutes: int = Field(default=60, ge=1)


# ---------------------------------------------------------------------------
# UCI models
# ---------------------------------------------------------------------------


class UCIRecord(BaseModel):
    """A single articulation-performance pair for UCI scoring."""

    model_config = ConfigDict(frozen=True)

    dimension: str
    articulation: str
    performance: str
    articulation_score: float = Field(ge=0.0, le=1.0)
    performance_score: float = Field(ge=0.0, le=1.0)
    gap: float = Field(ge=0.0, le=1.0)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ---------------------------------------------------------------------------
# Convergence models
# ---------------------------------------------------------------------------


class ActivationSignal(BaseModel):
    """A signal from a skill flagging a concern."""

    model_config = ConfigDict(frozen=True)

    skill_name: str
    concern: str
    severity: Severity
    weight: float = Field(default=1.0, ge=0.0)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ---------------------------------------------------------------------------
# Pipeline context and result
# ---------------------------------------------------------------------------


class SkillResult(BaseModel):
    """Result of a single skill's processing — immutable record."""

    model_config = ConfigDict(frozen=True)

    skill_name: str
    success: bool = True
    halt: bool = False
    halt_reason: str = ""
    modifications: dict[str, Any] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)
    audit_entries: tuple[AuditEntry, ...] = ()
    activation_signals: tuple[ActivationSignal, ...] = ()


class SkillContext(BaseModel):
    """Mutable context passed through the skill pipeline.

    This is the nerve impulse traveling through the system — each skill
    reads it, potentially modifies it, and passes it on. The StateVector
    modulates how each skill processes the context.
    """

    session_id: str = Field(default_factory=lambda: secrets.token_hex(12))
    run_id: str = Field(default_factory=lambda: secrets.token_hex(12))
    phase: PipelinePhase = PipelinePhase.PRE_PROMPT
    state_vector: StateVector = Field(default_factory=StateVector)

    # Prompt processing
    original_prompt: str = ""
    compiled_prompt: str | None = None
    system_instructions: list[str] = Field(default_factory=list)
    horizon_statement: str = ""

    # State
    session_state: SessionState | None = None

    # Tool calls
    pending_tool_calls: list[ToolCallRequest] = Field(default_factory=list)
    completed_tool_calls: list[ToolCallRecord] = Field(default_factory=list)

    # Change management
    change_plan: ChangeOrder | None = None
    modified_files: list[str] = Field(default_factory=list)

    # Escalation
    escalation_required: bool = False
    escalation_reason: str = ""

    # Pipeline tracking
    skill_results: list[SkillResult] = Field(default_factory=list)
    activation_signals: list[ActivationSignal] = Field(default_factory=list)
    convergence_score: float = 0.0

    # UCI tracking
    uci_records: list[UCIRecord] = Field(default_factory=list)
    current_uci: float = 0.0

    # Metadata
    metadata: dict[str, Any] = Field(default_factory=dict)
