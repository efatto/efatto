# Copyright 2026 Sergio Corato
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
"""Reading and adjusting the confidence level declared by the model."""

import re

LEVELS = ["low", "medium", "high"]

# English and Italian names of the levels
_ALIASES = {
    "high": "high",
    "alto": "high",
    "alta": "high",
    "medium": "medium",
    "medio": "medium",
    "media": "medium",
    "low": "low",
    "basso": "low",
    "bassa": "low",
}

# "CONFIDENCE: HIGH" or "AFFIDABILITA: ALTO", optionally in bold
_LEVEL_LINE_RE = re.compile(
    r"^[ \t]*\**(?:CONFIDENCE|AFFIDABILIT(?:A|À|A'))\**[ \t]*:[ \t]*\**"
    r"([A-Za-zÀ-ÿ]+)\**[ \t]*$",
    re.IGNORECASE | re.MULTILINE,
)
# "REASON: ..." or "MOTIVO: ..."
_REASON_LINE_RE = re.compile(
    r"^[ \t]*\**(?:REASON|MOTIVO)\**[ \t]*:[ \t]*(.+?)[ \t]*$",
    re.IGNORECASE | re.MULTILINE,
)


def parse_level(value):
    """'HIGH', 'Alto', 'medium'... -> 'high' | 'medium' | 'low' | False."""
    if not value or not isinstance(value, str):
        return False
    return _ALIASES.get(value.strip().casefold(), False)


def extract_level_lines(answer):
    """Remove the confidence and reason lines from the text and return them.

    Returns (clean_text, level, reason).
    """
    answer = answer or ""
    level = False
    reason = False
    level_match = _LEVEL_LINE_RE.search(answer)
    if level_match:
        level = parse_level(level_match.group(1))
    reason_match = _REASON_LINE_RE.search(answer)
    if reason_match:
        reason = reason_match.group(1).strip()
    cleaned = _LEVEL_LINE_RE.sub("", answer)
    cleaned = _REASON_LINE_RE.sub("", cleaned)
    return cleaned.strip(), level, reason


def downgrade(level, steps=1):
    if level not in LEVELS:
        return level
    return LEVELS[max(LEVELS.index(level) - steps, 0)]


def adjust_level(level, citations_verified=None, retrieval_score=None, min_score=0.0):
    """Final level: the system can only lower the declared one.

    - citations not verified (explicit False): low;
    - retrieval score below the threshold: one level lower;
    - no declared level: low.
    """
    if not level:
        return "low"
    if citations_verified is False:
        return "low"
    try:
        score = float(retrieval_score) if retrieval_score is not None else None
    except (TypeError, ValueError):
        score = None
    if score is not None and min_score and score < min_score:
        level = downgrade(level)
    return level


def is_abstention(answer, abstention_text):
    if not abstention_text:
        return False
    return (answer or "").strip().casefold().startswith(abstention_text.strip().casefold())
