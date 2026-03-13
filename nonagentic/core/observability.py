from __future__ import annotations

import os
import time
import functools
from datetime import datetime, timezone
from typing import Callable

# Evaluated lazily at send time so load_dotenv() in the caller takes effect
def _langfuse_enabled() -> bool:
    return bool(os.getenv("LANGFUSE_SECRET_KEY"))

_EVENT_LOG: list[dict] = []

# Thread-local token accumulator — agents write here during their node execution
_token_accumulator: dict[str, int] = {}


def record_tokens(request_id: str, tokens: int) -> None:
    """
    Called by get_llm_with_tracking() after each LLM invocation.
    Accumulates tokens per request_id so node_trace can read the total.
    """
    _token_accumulator[request_id] = _token_accumulator.get(request_id, 0) + tokens


def _emit(event: dict) -> None:
    _EVENT_LOG.append(event)
    if os.getenv("OBSERVABILITY_VERBOSE"):
        import json
        print(json.dumps(event))


def node_trace(node_name: str) -> Callable:
    """
    Decorator that wraps a LangGraph node function with observability hooks.
    Emits node_start and node_end events with duration_ms, tokens_used, and errors.
    """
    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        def wrapper(state: dict) -> dict:
            request_id = state.get("request_id", "unknown")
            start_ts = time.monotonic()

            _emit({
                "event": "node_start",
                "node": node_name,
                "request_id": request_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })

            error_msg = None
            result: dict = {}
            try:
                result = fn(state)
            except Exception as exc:
                error_msg = str(exc)
                result = {"error": error_msg}
            finally:
                duration_ms = int((time.monotonic() - start_ts) * 1000)
                tokens_used = _token_accumulator.pop(request_id, 0)

                _emit({
                    "event": "node_end",
                    "node": node_name,
                    "request_id": request_id,
                    "duration_ms": duration_ms,
                    "tool_calls": len(result.get("tool_calls", [])),
                    "tokens_used": tokens_used,
                    "error": error_msg,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })

                if _langfuse_enabled():
                    _send_to_langfuse(node_name, request_id, duration_ms, tokens_used, error_msg)

            return result
        return wrapper
    return decorator


def _send_to_langfuse(
    node: str, request_id: str, duration_ms: int, tokens_used: int, error: str | None
) -> None:
    try:
        from langfuse import Langfuse
        from langfuse.types import TraceContext
        lf = Langfuse(
            public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
            secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
            host=os.getenv("LANGFUSE_HOST", "http://localhost:3000"),
        )
        ctx = TraceContext(trace_id=request_id.replace("-", ""), name=node)
        with lf.start_as_current_observation(
            trace_context=ctx,
            name=node,
            as_type="agent",
            metadata={"duration_ms": duration_ms, "tokens_used": tokens_used},
            level="ERROR" if error else "DEFAULT",
            status_message=error,
            usage_details={"total_tokens": tokens_used} if tokens_used else None,
        ):
            pass
        lf.flush()
    except Exception as exc:
        if os.getenv("OBSERVABILITY_VERBOSE"):
            print(f"[langfuse error] {exc}")


def get_event_log() -> list[dict]:
    return list(_EVENT_LOG)


def clear_event_log() -> None:
    _EVENT_LOG.clear()
