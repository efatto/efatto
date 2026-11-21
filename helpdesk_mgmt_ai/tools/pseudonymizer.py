# Copyright 2026 Sergio Corato
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
"""Pseudonymization of ticket text, with no dependency on Odoo.

Personal data is replaced by consistent placeholders ([PERSON_1],
[EMAIL_1], ...). The placeholder -> value table stays in the Odoo database
and is used to put the real data back into the draft answer.

The patterns cover Italian identifiers (codice fiscale, partita IVA, SdI
recipient code) as well as generic ones (email, IBAN, phone numbers).
"""

import re

PLACEHOLDER_RE = re.compile(r"\[([A-Z]+)_(\d+)\]")

# Placeholder labels and patterns. Order matters: data with a precise
# format is searched before more generic data.
PATTERNS = [
    ("EMAIL", re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")),
    # Italian VAT number, with or without the IT prefix
    ("VAT", re.compile(r"\b(?:IT ?)?\d{11}\b")),
    (
        "IBAN",
        re.compile(r"\b[A-Z]{2}\d{2}(?: ?[A-Z0-9]{4}){3,7}(?: ?[A-Z0-9]{1,4})?\b"),
    ),
    # Italian fiscal code of a natural person
    (
        "FISCALCODE",
        re.compile(r"\b[A-Z]{6}\d{2}[A-EHLMPRST]\d{2}[A-Z]\d{3}[A-Z]\b", re.IGNORECASE),
    ),
    # SdI recipient code, only when introduced by a keyword
    (
        "SDICODE",
        re.compile(
            r"\b(?:codice\s+destinatario|cod\.?\s*dest(?:inatario)?\.?"
            r"|codice\s+(?:univoco|sdi)|recipient\s+code|sdi\s+code)"
            r"\s*[:=]?\s*([A-Z0-9]{6,7})\b",
            re.IGNORECASE,
        ),
    ),
    # Italian landline and mobile numbers
    (
        "PHONE",
        re.compile(
            r"(?<![\w/])(?:\+39[ .]?)?(?:0\d{1,3}|3\d{2})[ ./-]?\d{3,4}[ ./-]?\d{3,4}"
            r"(?![\w/])"
        ),
    ),
    # Document numbers such as INV/2026/00145 or FT/2026/00145
    ("DOCUMENT", re.compile(r"\b[A-Z]{1,6}(?:/[A-Z0-9]{1,6})?/\d{4}/\d{1,6}\b")),
]

# Labels whose comparison ignores spaces and separators.
_COMPACT_LABELS = {"IBAN", "VAT", "PHONE", "FISCALCODE", "SDICODE"}

# Italian legal forms, removed to also match the short company name.
LEGAL_FORMS_RE = re.compile(
    r"[\s,]+(?:s\.?r\.?l\.?s?|s\.?p\.?a\.?|s\.?n\.?c\.?|s\.?a\.?s\.?|s\.?s\.?"
    r"|soc\.?\s*coop\.?(?:\s*a\s*r\.?l\.?)?)\s*$",
    re.IGNORECASE,
)

_NAME_CANDIDATE_RE = re.compile(
    r"\b[A-ZÀ-Ý][a-zà-ÿ'’]+(?:\s+(?:[A-ZÀ-Ý][\w'’.&-]*)){1,3}"
)


def _normalize(label, value):
    value = value or ""
    if label in _COMPACT_LABELS:
        compact = re.sub(r"[\s./-]", "", value).casefold()
        return compact.removeprefix("it") if label == "VAT" else compact
    return " ".join(value.split()).casefold()


def strip_legal_form(name):
    """'Rossi Srl' -> 'Rossi'. Returns '' when there is no legal form."""
    stripped = LEGAL_FORMS_RE.sub("", name or "").strip()
    return stripped if stripped and stripped != (name or "").strip() else ""


def candidate_names(text, limit=30):
    """Sequences of 2-4 capitalized words: possible names.

    Odoo compares them with the contacts; on their own they are not enough
    to say that they are personal data.
    """
    seen = []
    for match in _NAME_CANDIDATE_RE.finditer(text or ""):
        candidate = match.group(0).strip(" .,;:")
        if candidate not in seen:
            seen.append(candidate)
        if len(seen) >= limit:
            break
    return seen


class Pseudonymizer:
    """Replaces personal data with placeholders and can put it back."""

    def __init__(self, mapping=None):
        # placeholder -> original value
        self.mapping = dict(mapping or {})

    # --- placeholders -------------------------------------------------------

    def _label_of(self, placeholder):
        match = PLACEHOLDER_RE.fullmatch(placeholder)
        return match.group(1) if match else ""

    def _find_placeholder(self, label, value):
        key = _normalize(label, value)
        for placeholder, original in self.mapping.items():
            if self._label_of(placeholder) == label and _normalize(label, original) == key:
                return placeholder
        return None

    def placeholder_for(self, label, value):
        existing = self._find_placeholder(label, value)
        if existing:
            return existing
        numbers = [
            int(m.group(2))
            for m in (PLACEHOLDER_RE.fullmatch(p) for p in self.mapping)
            if m and m.group(1) == label
        ]
        placeholder = f"[{label}_{max(numbers, default=0) + 1}]"
        self.mapping[placeholder] = value
        return placeholder

    # --- pseudonymization ------------------------------------------------------

    @staticmethod
    def _value_regex(value):
        parts = [re.escape(part) for part in value.split()]
        body = r"\s+".join(parts)
        return re.compile(rf"(?<!\w){body}(?!\w)", re.IGNORECASE)

    @staticmethod
    def _outside_placeholders(text, func):
        """Apply func only to the pieces of text that are not placeholders."""
        pieces = []
        last = 0
        for match in PLACEHOLDER_RE.finditer(text):
            pieces.append(func(text[last : match.start()]))
            pieces.append(match.group(0))
            last = match.end()
        pieces.append(func(text[last:]))
        return "".join(pieces)

    def _replace_known(self, text, known_values):
        # Longest values first, so that "Mario Rossi" wins over "Rossi".
        items = sorted(
            {(label, value.strip()) for label, value in known_values if value and value.strip()},
            key=lambda item: len(item[1]),
            reverse=True,
        )
        for label, value in items:
            if len(value) < 3:
                continue
            regex = self._value_regex(value)
            if regex.search(PLACEHOLDER_RE.sub(" ", text)):
                placeholder = self.placeholder_for(label, value)
                text = self._outside_placeholders(
                    text, lambda piece, r=regex, p=placeholder: r.sub(p, piece)
                )
        return text

    def _replace_patterns(self, text):
        for label, regex in PATTERNS:

            def _sub(match, label=label):
                if match.groups():
                    value = match.group(1)
                    start, end = match.span(1)
                    whole_start = match.start()
                    placeholder = self.placeholder_for(label, value)
                    prefix = match.group(0)[: start - whole_start]
                    suffix = match.group(0)[end - whole_start :]
                    return f"{prefix}{placeholder}{suffix}"
                return self.placeholder_for(label, match.group(0))

            text = self._outside_placeholders(
                text, lambda piece, r=regex, f=_sub: r.sub(f, piece)
            )
        return text

    def pseudonymize(self, text, known_values=()):
        """known_values: (label, value) pairs known from Odoo."""
        text = text or ""
        # Data with a precise format first (email, IBAN...), then the values
        # known from Odoo: this way a name inside an email does not split it.
        text = self._replace_patterns(text)
        text = self._replace_known(text, known_values)
        return text

    # --- checks and restore ----------------------------------------------------

    def residue(self, text, known_values=()):
        """Personal data still present in the text, as (label, value) pairs."""
        text = PLACEHOLDER_RE.sub(" ", text or "")
        found = []
        for label, value in known_values:
            value = (value or "").strip()
            if len(value) >= 3 and self._value_regex(value).search(text):
                found.append((label, value))
        for label, regex in PATTERNS:
            for match in regex.finditer(text):
                found.append((label, match.group(1) if match.groups() else match.group(0)))
        unique = []
        for item in found:
            if item not in unique:
                unique.append(item)
        return unique

    def restore(self, text):
        """Put the original values back in place of the known placeholders."""

        def _sub(match):
            return self.mapping.get(match.group(0), match.group(0))

        return PLACEHOLDER_RE.sub(_sub, text or "")
