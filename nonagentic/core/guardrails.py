"""
Output guardrail — ConstitutionalChain pattern.

Validates every LLM-generated text output against a set of constitutional
principles before it reaches the user:

  1. No raw PII (email addresses, phone numbers) in output
  2. No KYC document content exposed verbatim
  3. No financial advice or investment recommendations
  4. Response must be relevant to customer operations domain

When GUARDRAIL_ENABLED=false the check is skipped (useful for unit tests).
When the LLM is unavailable the rule-based fallback runs instead.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_EMAIL_RE = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
_PHONE_RE = re.compile(r"\+?\d[\d\s\-().]{7,}\d")

_FORBIDDEN_PHRASES = [
    "buy shares",
    "invest in",
    "stock recommendation",
    "guaranteed return",
    "financial advice",
]

_CONSTITUTIONAL_PRINCIPLES = [
    "The response must not contain raw email addresses or phone numbers.",
    "The response must not reproduce verbatim KYC document content.",
    "The response must not provide financial investment advice.",
    "The response must be relevant to customer operations, banking, or compliance.",
]


@dataclass
class GuardrailResult:
    passed: bool
    violations: list[str]
    revised_text: str


def guardrail_check(text: str, request_id: str = "") -> GuardrailResult:
    """
    Run constitutional checks on `text`.
    Returns GuardrailResult with passed=True if clean, or revised_text with
    violations redacted/replaced.
    """
    from nonagentic.core.config import load_config

    cfg = load_config()

    if not cfg.guardrail_enabled:
        return GuardrailResult(passed=True, violations=[], revised_text=text)

    violations: list[str] = []
    revised = text

    # Rule 1 — mask PII
    if _EMAIL_RE.search(revised):
        violations.append("PII: email address detected in output")
        revised = _EMAIL_RE.sub("[email redacted]", revised)

    if _PHONE_RE.search(revised):
        violations.append("PII: phone number detected in output")
        revised = _PHONE_RE.sub("[phone redacted]", revised)

    # Rule 2 — forbidden phrases
    lower = revised.lower()
    for phrase in _FORBIDDEN_PHRASES:
        if phrase in lower:
            violations.append(f"Policy: forbidden phrase '{phrase}' in output")
            revised = re.sub(
                re.escape(phrase), "[redacted]", revised, flags=re.IGNORECASE
            )

    # Rule 3 — LLM-based constitutional check (optional, falls back gracefully)
    if violations:
        # Already found rule-based violations — skip LLM check to save tokens
        return GuardrailResult(
            passed=False, violations=violations, revised_text=revised
        )

    llm_result = _llm_constitutional_check(text)
    if llm_result:
        violations.extend(llm_result)
        return GuardrailResult(
            passed=False, violations=violations, revised_text=revised
        )

    return GuardrailResult(passed=True, violations=[], revised_text=revised)


def _llm_constitutional_check(text: str) -> list[str]:
    """
    Ask the LLM to evaluate the text against constitutional principles.
    Returns a list of violation strings, or [] if clean or LLM unavailable.
    """
    try:
        from langchain_core.messages import HumanMessage, SystemMessage
        from nonagentic.core.llm import get_llm

        principles_str = "\n".join(f"- {p}" for p in _CONSTITUTIONAL_PRINCIPLES)
        llm = get_llm(temperature=0.0)
        resp = llm.invoke(
            [
                SystemMessage(
                    content=(
                        f"You are a compliance checker. Evaluate the following text against these principles:\n"
                        f"{principles_str}\n\n"
                        "Reply with PASS if all principles are satisfied, or list each violated principle "
                        "on a new line starting with VIOLATION:. No other text."
                    )
                ),
                HumanMessage(content=text[:1000]),  # cap to avoid large token spend
            ]
        )
        content = resp.content.strip()
        if content.upper().startswith("PASS"):
            return []
        return [
            line.replace("VIOLATION:", "").strip()
            for line in content.splitlines()
            if line.upper().startswith("VIOLATION:")
        ]
    except Exception:
        return []  # fail open — rule-based checks already ran
