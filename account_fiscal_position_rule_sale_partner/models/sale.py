# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    account_fiscal_position_rule_id = fields.Many2one(
        comodel_name='account.fiscal.position.rule',
        readonly=True, states={'draft': [('readonly', False)]},
        string='Fiscal Position Rule',
    )

    @api.onchange('fiscal_position')
    def _onchange_fiscal_position(self):
        if self.account_fiscal_position_rule_id and self.fiscal_position:
            if self.fiscal_position != \
                    self.account_fiscal_position_rule_id.fiscal_position_id:
                self.account_fiscal_position_rule_id = False
