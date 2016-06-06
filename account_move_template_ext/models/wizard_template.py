# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api


class WizardSelectMoveTemplate(models.TransientModel):
    _inherit = "wizard.select.move.template"

    @api.model
    def _make_move(self, ref, period_id, journal_id, partner_id):
        res = super(WizardSelectMoveTemplate, self)._make_move(
            ref, period_id, journal_id, partner_id)
        self.env['account.move'].browse(res).write({
            'template_id': self.template_id.id,
        })
        return res
