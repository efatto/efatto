# Copyright 2026 Sergio Corato
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
"""Pseudonymization of ticket text, with no dependency on Odoo.

Personal data is replaced by consistent placeholders ([PERSON_1],
[EMAIL_1], ...). The placeholder -> value table stays in the Odoo database
and is used to put the real data back into the draft answer.

The patterns cover Italian identifiers (codice fiscale, partita IVA, SdI
recipient code) as well as generic ones (email, IBAN, phone numbers, URLs).
"""

import re

PLACEHOLDER_RE = re.compile(r"\[([A-Z]+)_(\d+)\]")

# Placeholder labels and patterns. Order matters: data with a precise
# format is searched before more generic data.
PATTERNS = [
    # URLs before e-mail: a link may contain an address or a token
    ("URL", re.compile(r"https?://[^\s<>\"']+", re.IGNORECASE)),
    ("EMAIL", re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")),
    # Italian VAT number, with or without the IT prefix
    ("VAT", re.compile(r"\b(?:IT ?)?\d{11}\b", re.IGNORECASE)),
    (
        "IBAN",
        re.compile(
            r"\b[A-Z]{2}\d{2}(?: ?[A-Z0-9]{4}){3,7}(?: ?[A-Z0-9]{1,4})?\b",
            re.IGNORECASE,
        ),
    ),
    # Italian fiscal code of a natural person, omocodia codes included (letters
    # LMNPQRSTUV in place of the digits)
    (
        "FISCALCODE",
        re.compile(
            r"\b[A-Z]{6}[0-9LMNPQRSTUV]{2}[A-EHLMPRST][0-9LMNPQRSTUV]{2}"
            r"[A-Z][0-9LMNPQRSTUV]{3}[A-Z]\b",
            re.IGNORECASE,
        ),
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
    # Italian landline and mobile numbers, with +39 or the 0039 prefix
    (
        "PHONE",
        re.compile(
            r"(?<![\w/])(?:(?:\+|00)\s?39[\s./-]?)?"
            r"(?:0\d{1,3}|3\d{2})[ ./-]?\d{3,4}[ ./-]?\d{3,4}"
            r"(?![\w/])"
        ),
    ),
    # Document numbers such as INV/2026/00145, FT-2026-145 or inv/2026/145
    (
        "DOCUMENT",
        re.compile(
            r"\b[A-Z]{1,6}(?:[/-][A-Z0-9]{1,6})?[/-]\d{4}[/-]\d{1,6}\b", re.IGNORECASE
        ),
    ),
]

# Labels whose comparison ignores spaces and separators.
_COMPACT_LABELS = {"IBAN", "VAT", "PHONE", "FISCALCODE", "SDICODE"}

# Values that must be masked in the strict check only: a leftover "@" or a long
# run of digits means the generic patterns missed something.
_STRICT_PATTERNS = [
    ("EMAIL", re.compile(r"@")),
    ("DIGITS", re.compile(r"(?<!\d)\d{9,}(?!\d)")),
    (
        "SECRET",
        re.compile(r"(?:access_token|token|password|api[_-]?key)=", re.IGNORECASE),
    ),
]

# Italian legal forms, removed to also match the short company name.
LEGAL_FORMS_RE = re.compile(
    r"[\s,]+(?:s\.?r\.?l\.?s?|s\.?p\.?a\.?|s\.?n\.?c\.?|s\.?a\.?s\.?|s\.?s\.?"
    r"|soc\.?\s*coop\.?(?:\s*a\s*r\.?l\.?)?)\s*$",
    re.IGNORECASE,
)

# One or more capitalized words, no digits.
_NAME_TOKEN_RE = re.compile(r"[A-ZÀ-Ý][a-zà-ÿ'’]*(?:[A-ZÀ-Ý][a-zà-ÿ'’]*)*")

# Fragments that cannot contain a name continued from the previous one.
_FRAGMENT_RE = re.compile(r"[.!?;:\n\r]+")

# Short words that are also partner names or name parts: replacing them
# everywhere would corrupt the technical text ("il campo data non si salva").
NAME_STOP_WORDS = {
    "acquisti",
    "agenzia",
    "alfa",
    "altro",
    "archivio",
    "assistenza",
    "beta",
    "casa",
    "cliente",
    "clienti",
    "comune",
    "contatti",
    "data",
    "demo",
    "diritto",
    "documento",
    "documenti",
    "dove",
    "fattura",
    "fatture",
    "gamma",
    "giorno",
    "gruppo",
    "help",
    "idea",
    "info",
    "magazzino",
    "mail",
    "mese",
    "nota",
    "notaio",
    "nuovo",
    "oggetto",
    "ordine",
    "ordini",
    "parte",
    "poste",
    "prima",
    "prova",
    "quando",
    "report",
    "sara",
    "sede",
    "servizi",
    "sistema",
    "societa",
    "sono",
    "stato",
    "studio",
    "supporto",
    "srl",
    "tempo",
    "test",
    "ufficio",
    "utente",
    "vendite",
    "verifica",
    "web",
}


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


def is_generic_word(value):
    """True for a single word that is too common to be replaced everywhere."""
    return " ".join((value or "").split()).casefold() in NAME_STOP_WORDS


def candidate_names(text, limit=40):
    """Sequences of 2-4 capitalized words: possible names.

    Odoo compares them with the contacts; on their own they are not enough
    to say that they are personal data. Every window of a fragment is tried,
    so "Sono Mario Rossi" also yields "Mario Rossi".
    """
    seen = []
    for fragment in _FRAGMENT_RE.split(text or ""):
        tokens = _NAME_TOKEN_RE.findall(fragment)
        for size in (2, 3, 4):
            for index in range(len(tokens) - size + 1):
                candidate = " ".join(tokens[index : index + size])
                if candidate not in seen:
                    seen.append(candidate)
                if len(seen) >= limit:
                    return seen
    return seen


def ilike_escape(value):
    """Escape a value used with the '=ilike' operator in Odoo."""
    return (value or "").replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def _dedupe(items):
    unique = []
    for item in items:
        if item not in unique:
            unique.append(item)
    return unique


class Pseudonymizer:
    """Replaces personal data with placeholders and can put it back."""

    def __init__(self, mapping=None):
        # placeholder -> original value
        self.mapping = dict(mapping or {})
        self._index = {}
        for placeholder, original in self.mapping.items():
            label = self._label_of(placeholder)
            if label:
                self._index[(label, _normalize(label, original))] = placeholder

    # --- placeholders -------------------------------------------------------

    @staticmethod
    def _label_of(placeholder):
        match = PLACEHOLDER_RE.fullmatch(placeholder)
        return match.group(1) if match else ""

    def _find_placeholder(self, label, value):
        return self._index.get((label, _normalize(label, value)))

    def placeholder_for(self, label, value):
        existing = self._find_placeholder(label, value)
        if existing:
            return existing
        numbers = [
            int(match.group(2))
            for match in (PLACEHOLDER_RE.fullmatch(p) for p in self.mapping)
            if match and match.group(1) == label
        ]
        placeholder = f"[{label}_{max(numbers, default=0) + 1}]"
        self.mapping[placeholder] = value
        self._index[(label, _normalize(label, value))] = placeholder
        return placeholder

    # --- pseudonymization ---------------------------------------------------

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
        # Longest values first, so that "Mario Rossi" wins over "Rossi", and by
        # value on equal length: the output must not depend on the hash seed.
        items = sorted(
            {
                (label, value.strip())
                for label, value in known_values
                if value and value.strip()
            },
            key=lambda item: (-len(item[1]), item[1]),
        )
        for label, value in items:
            if len(value) < 3 or is_generic_word(value):
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

    # --- checks and restore -------------------------------------------------

    def residue(self, text, known_values=(), strict=False):
        """Personal data still present in the text, as (label, value) pairs.

        With ``strict`` the check also reports what the generic patterns would
        have missed: a leftover "@", a long run of digits, a query string.
        """
        text = PLACEHOLDER_RE.sub(" ", text or "")
        found = []
        for label, value in known_values:
            value = (value or "").strip()
            if len(value) >= 3 and not is_generic_word(value):
                if self._value_regex(value).search(text):
                    found.append((label, value))
        for label, regex in PATTERNS:
            for match in regex.finditer(text):
                found.append(
                    (label, match.group(1) if match.groups() else match.group(0))
                )
        if strict:
            for label, regex in _STRICT_PATTERNS:
                for match in regex.finditer(text):
                    found.append((label, match.group(0)))
        return _dedupe(found)

    def restore(self, text):
        """Put the original values back in place of the known placeholders."""

        def _sub(match):
            return self.mapping.get(match.group(0), match.group(0))

        return PLACEHOLDER_RE.sub(_sub, text or "")
