"""Structured logging configuration via structlog.

All logs are JSON-formatted for machine parsing. Sensitive data
(API keys, tokens, response bodies) must NEVER appear in logs.
Log tool call names and parameter keys, but not parameter values
that may contain secrets.

This is the observability layer — the nervous system's sensory feedback.
"""

from __future__ import annotations

import logging
import sys

import structlog


def configure_logging(
    level: str = "INFO",
    log_format: str = "json",
) -> None:
    """Configure structlog for the application.

    Args:
        level: Log level string (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        log_format: "json" for machine-readable, "console" for human-readable.
    """
    # Shared processors for all output formats
    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        _secret_filter,
    ]

    if log_format == "json":
        renderer: structlog.types.Processor = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer()

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Configure stdlib logging to route through structlog
    formatter = structlog.stdlib.ProcessorFormatter(
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )

    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Suppress noisy third-party loggers
    for noisy in ("httpx", "httpcore", "litellm", "openai", "urllib3"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a bound logger for a module.

    Usage:
        logger = get_logger(__name__)
        logger.info("skill_executed", skill="tool_guard", result="pass")
    """
    return structlog.get_logger(name)


# ---------------------------------------------------------------------------
# Secret filtering processor
# ---------------------------------------------------------------------------

# Keys whose values must never appear in logs
_SENSITIVE_KEYS = frozenset({
    "api_key",
    "api_secret",
    "token",
    "password",
    "secret",
    "authorization",
    "bearer",
    "credential",
    "private_key",
    "secret_value",
})


def _secret_filter(
    logger: object,
    method_name: str,
    event_dict: dict[str, object],
) -> dict[str, object]:
    """Structlog processor that redacts sensitive values from log output.

    Any key containing a sensitive substring gets its value replaced
    with [REDACTED]. This is defense-in-depth — the primary defense
    is never passing secrets to the logger in the first place.
    """
    for key in list(event_dict.keys()):
        key_lower = key.lower()
        if any(s in key_lower for s in _SENSITIVE_KEYS):
            event_dict[key] = "[REDACTED]"
    return event_dict
