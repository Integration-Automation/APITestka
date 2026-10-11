"""Explicit canonical recording scopes shared with LoadDensity and WebRunner."""

try:
    from je_action_core.request_context import RunContext, get_run_context, use_run_context
except ModuleNotFoundError as error:
    if error.name != "je_action_core.request_context":
        raise
    raise RuntimeError(
        "Canonical recording requires ActionCore with request_context support; "
        "upgrade ActionCore or use its coordinated source checkout."
    ) from error

__all__ = ["RunContext", "get_run_context", "use_run_context"]
