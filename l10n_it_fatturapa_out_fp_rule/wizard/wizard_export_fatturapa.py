# -*- coding: utf-8 -*-
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from openerp import models
from openerp.addons.l10n_it_fatturapa.bindings.fatturapa import (
    DatiRiepilogoType,
    DettaglioLineeType,
    AltriDatiGestionaliType,
)


class WizardExportFatturapa(models.TransientModel):
    _inherit = "wizard.export.fatturapa"

    def setDatiGeneraliDocumento(self, invoice, body):
        res = super(WizardExportFatturapa, self).setDatiGeneraliDocumento(
            invoice, body)
        if invoice.account_fiscal_position_rule_id:
            causale = invoice.account_fiscal_position_rule_id.description
            causale_list_200 = \
                [causale[i:i + 200] for i in
                 range(0, len(causale), 200)]
            for causale200 in causale_list_200:
                # Remove non latin chars, but go back to unicode string
                # as expected by String200LatinType
                causale = causale200.encode(
                    'latin', 'ignore').decode('latin')
                body.DatiGenerali.DatiGeneraliDocumento.Causale \
                    .append(causale)
        return res

    def setDettaglioLinee(self, invoice, body):
        res = super(WizardExportFatturapa, self).setDettaglioLinee(invoice, body)
        if invoice.account_fiscal_position_rule_id:
            line_no = 1
            for line in invoice.invoice_line:
                line_no += 1
            dec = invoice.account_fiscal_position_rule_id
            DettaglioLinea = DettaglioLineeType(
                NumeroLinea=str(line_no),
                Descrizione="Altre lettere d'intento".encode(
                    'latin', 'ignore').decode('latin')[:1000],
                PrezzoUnitario="0.00",
                PrezzoTotale="0.00",
                AliquotaIVA="0.00",
                Natura="N1",
            )
            dati_gestionali = AltriDatiGestionaliType(
                TipoDato="INTENTO",
                RiferimentoTesto=dec.telematic_protocol.encode(
                    'latin', 'ignore').decode('latin')[:60],
                RiferimentoData=dec.date_issue
            )
            DettaglioLinea.AltriDatiGestionali.append(dati_gestionali)
            body.DatiBeniServizi.DettaglioLinee.append(DettaglioLinea)
        return res

    def setDatiRiepilogo(self, invoice, body):
        res = super(WizardExportFatturapa, self).setDatiRiepilogo(invoice, body)
        if invoice.account_fiscal_position_rule_id:
            riepilogo = DatiRiepilogoType(
                AliquotaIVA="0.00",
                ImponibileImporto="0.00",
                Imposta="0.00",
                Natura="N1",
                RiferimentoNormativo="Esclusa ex. Art. 15",
            )
            body.DatiBeniServizi.DatiRiepilogo.append(riepilogo)
        return res
