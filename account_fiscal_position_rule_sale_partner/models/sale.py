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

    @api.multi
    def onchange_address_id(self, partner_invoice_id, partner_shipping_id,
                            partner_id, company_id):
        result = {'value': {}}
        if not company_id or not partner_invoice_id or \
                partner_id == partner_invoice_id == partner_shipping_id:
            return result

        kwargs = {
            'company_id': company_id,
            'partner_id': partner_id,
            'partner_invoice_id': partner_invoice_id,
            'partner_shipping_id': partner_shipping_id,
        }
        return self._fiscal_position_map(result, **kwargs)


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    @api.model
    def _create_invoices(self, inv_values, sale_id):
        for sale in self.env['sale.order'].browse(sale_id):
            if sale.account_fiscal_position_rule_id:
                inv_values['account_fiscal_position_rule_id'] = \
                    sale.account_fiscal_position_rule_id.id
            else:
                # check if a valid rule exists and apply
                result = self.env['account.fiscal.position.rule'].\
                        fiscal_position_map(partner_id=sale.partner_id.id,
                                            company_id=sale.company_id.id,
                                            partner_invoice_id=sale.
                                            partner_invoice_id.id)
                if result:
                    inv_values['account_fiscal_position_rule_id'] = \
                        result['account_fiscal_position_rule_id']
        return super(SaleAdvancePaymentInv, self)._create_invoices(
            inv_values, sale_id)
