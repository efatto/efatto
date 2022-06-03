# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, _


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.model
    def _get_invoice_vals(self, key, inv_type, journal_id, move):
        invoice_vals = super(StockPicking, self)._get_invoice_vals(
            key, inv_type, journal_id, move)
        sale = move.picking_id.sale_id
        if sale and inv_type in ('out_invoice', 'out_refund'):
            if sale.account_fiscal_position_rule_id:
                invoice_vals['account_fiscal_position_rule_id'] = \
                    sale.account_fiscal_position_rule_id.id
            else:
                # check if a valid rule exists and apply
                result = self.env['account.fiscal.position.rule'].\
                        fiscal_position_map(partner_id=sale.partner_id.id,
                                            company_id=sale.company_id.id,
                                            partner_invoice_id=sale.
                                            partner_invoice_id.id)
                if result:
                    invoice_vals['account_fiscal_position_rule_id'] = \
                        result['account_fiscal_position_rule_id']
        return invoice_vals
