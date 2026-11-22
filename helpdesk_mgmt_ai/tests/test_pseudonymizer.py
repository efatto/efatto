# Copyright 2026 Sergio Corato
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import BaseCase

from ..tools.confidence import (
    adjust_level,
    extract_level_lines,
    normalize_flag,
    parse_level,
)
from ..tools.pseudonymizer import (
    PLACEHOLDER_RE,
    Pseudonymizer,
    candidate_names,
    strip_legal_form,
)

TEXT = (
    "Buongiorno, sono Mario Rossi di Rossi Impianti Srl "
    "(P.IVA IT01234567890, CF RSSMRA80A01H501U).\n"
    "La fattura FT/2026/00145 è stata scartata dallo SdI.\n"
    "Codice destinatario: M5UXCR1. Scrivete a mario.rossi@rossi-impianti.it "
    "o chiamate il 347 123 4567.\n"
    "IBAN IT60 X054 2811 1010 0000 0123 456. Totale 1.220,00 euro del 15/03/2026."
)
KNOWN = [
    ("PERSON", "Mario Rossi"),
    ("PERSON", "Rossi"),
    ("COMPANY", "Rossi Impianti Srl"),
]


class TestPseudonymizer(BaseCase):
    def test_pseudonymize_and_restore(self):
        pseudonymizer = Pseudonymizer()
        clean = pseudonymizer.pseudonymize(TEXT, KNOWN)
        for value in (
            "Mario",
            "Rossi",
            "IT01234567890",
            "RSSMRA80A01H501U",
            "M5UXCR1",
            "mario.rossi@",
            "347 123 4567",
            "IT60 X054",
            "FT/2026/00145",
        ):
            self.assertNotIn(value, clean)
        # Amounts and dates stay: the answer needs them
        self.assertIn("1.220,00", clean)
        self.assertIn("15/03/2026", clean)
        self.assertIn("[EMAIL_1]", clean)
        self.assertIn("[VAT_1]", clean)
        self.assertEqual(pseudonymizer.residue(clean, KNOWN), [])
        self.assertEqual(pseudonymizer.restore(clean), TEXT)

    def test_same_value_same_placeholder(self):
        pseudonymizer = Pseudonymizer()
        first = pseudonymizer.pseudonymize("Chiamare il 3471234567", [])
        second = Pseudonymizer(pseudonymizer.mapping).pseudonymize(
            "Numero 347 123 4567", []
        )
        self.assertIn("[PHONE_1]", first)
        self.assertIn("[PHONE_1]", second)

    def test_residue_detects_manual_edit(self):
        pseudonymizer = Pseudonymizer()
        residue = pseudonymizer.residue("Contattare luigi@example.com", [])
        self.assertEqual(residue, [("EMAIL", "luigi@example.com")])

    def test_helpers(self):
        self.assertEqual(strip_legal_form("Rossi Impianti S.r.l."), "Rossi Impianti")
        self.assertEqual(strip_legal_form("Rossi"), "")
        self.assertIn("Mario Rossi", candidate_names(TEXT))

    def test_confidence(self):
        text, level, reason = extract_level_lines(
            "Step 1 [F1]\nCONFIDENCE: MEDIUM\nREASON: depends on the accounts"
        )
        self.assertEqual(
            (text, level, reason), ("Step 1 [F1]", "medium", "depends on the accounts")
        )
        text, level, reason = extract_level_lines(
            "Passo 1 [F1]\nAFFIDABILITA: ALTO\nMOTIVO: procedura standard"
        )
        self.assertEqual((level, reason), ("high", "procedura standard"))
        self.assertEqual(parse_level("Basso"), "low")
        self.assertEqual(adjust_level("high", citations_verified=False), "low")
        self.assertEqual(
            adjust_level("high", retrieval_score=0.3, min_score=0.5), "medium"
        )
        self.assertEqual(adjust_level(False), "low")

    def test_format_bypasses(self):
        """Every format a customer uses must be masked, in any case."""
        pseudonymizer = Pseudonymizer()
        cases = {
            "chiamare 0039 347 123 4567 ora": "347",
            "iban it60x0542811101000000123456": "it60x",
            "cf omocodia RSSMRA80A01H50LU": "RSSMRA",
            "fattura ft-2026-145": "ft-2026",
            "link https://x.it/web?access_token=abc123": "access_token",
        }
        for text, leaked in cases.items():
            clean = pseudonymizer.pseudonymize(text)
            self.assertNotIn(leaked, clean, text)
            self.assertIsNone(
                PLACEHOLDER_RE.search(text) and None
            )  # the source text has no placeholder
        self.assertTrue(
            PLACEHOLDER_RE.search(
                pseudonymizer.restore(
                    pseudonymizer.pseudonymize("chiamare 0039 347 123 4567 ora")
                )
            )
            is None
        )

    def test_generic_word_is_not_replaced(self):
        """A partner called 'Data Srl' must not turn 'data' into a placeholder."""
        pseudonymizer = Pseudonymizer()
        clean = pseudonymizer.pseudonymize(
            "il campo data non si salva",
            [("COMPANY", "Data Srl"), ("COMPANY", "Data")],
        )
        self.assertEqual(clean, "il campo data non si salva")

    def test_candidate_names_are_not_swallowed(self):
        self.assertIn(
            "Mario Rossi",
            candidate_names("Buongiorno, Sono Mario Rossi di Rossi Impianti Srl."),
        )
        self.assertIn("Mario Rossi", candidate_names("Mario Rossi\nRossi Impianti"))
        self.assertIn(
            "Luigi Verdi", candidate_names("Srl. Il Sig. Luigi Verdi chiede aiuto")
        )

    def test_strict_residue_reports_what_the_patterns_miss(self):
        pseudonymizer = Pseudonymizer()
        self.assertEqual(pseudonymizer.residue("nessun dato", [], strict=True), [])
        found = pseudonymizer.residue("ordine 1234567890", [], strict=True)
        self.assertEqual(found, [("DIGITS", "1234567890")])

    def test_flags_are_normalized(self):
        """'false' as a string must not become True."""
        self.assertFalse(normalize_flag("false"))
        self.assertFalse(normalize_flag("0"))
        self.assertFalse(normalize_flag(0))
        self.assertTrue(normalize_flag("true"))
        self.assertTrue(normalize_flag(True))
        self.assertIsNone(normalize_flag(None))
        self.assertIsNone(normalize_flag("boh"))
        self.assertEqual(adjust_level("high", citations_verified="false"), "low")
