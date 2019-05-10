# -*- coding: utf-8 -*-
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from openerp import models


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
