# Copyright 2026 Sergio Corato
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import BaseCase

from ..tools.confidence import adjust_level, extract_level_lines, parse_level
from ..tools.pseudonymizer import Pseudonymizer, candidate_names, strip_legal_form

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
