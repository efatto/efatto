# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, _


class AccountFiscalPositionRule(models.Model):
    _inherit = 'account.fiscal.position.rule'

    number_protocol = fields.Integer(
        'VAT Exemption declaration protocol Number')
    partner_id = fields.Many2one('res.partner', 'Partner')
    date_issue = fields.Date('VAT Exemption declaration Issue Date')
    date_reception = fields.Date('VAT Exemption declaratione Reception Date')
    exemption_type = fields.Selection([
        ('S', 'Single Operation'),
        ('I', 'Import')
    ], 'VAT Exemption Type')
    amount_max = fields.Float('Max Amount')
    inactive = fields.Boolean('Inactive')
    exemption_proof = fields.Binary(
        'VAT Exemption proof of posting',)
    operation_type = fields.Selection([
        ('customer', 'Customer'),
        ('supplier', 'Supplier'),
    ], 'VAT Operation Type')
    company_id = fields.Many2one(
        'res.company', 'Company', required=True,
        default=lambda self: self.env['res.company']._company_default_get(
            'account.fiscal.position.rule'))

    def _get_amount_total(self):
        for rule in self:
            if rule.operation_type == 'supplier':
                inv_tax_ids = self.env['account.invoice.tax'].search([
                    ('invoice_id.account_fiscal_position_rule_id', '=', rule.id),
                    ('invoice_id.state', 'not in', ['cancel', 'draft']),
                    ('invoice_id.type', 'in', ['in_invoice', 'in_refund'])
                ])
                rule.amount_total = sum(
                    line.base for line in inv_tax_ids if line.amount == 0.0 and
                    line.invoice_id.type == 'in_invoice') - sum(
                    line.base for line in inv_tax_ids if line.amount == 0.0 and
                    line.invoice_id.type == 'in_refund')
            elif rule.operation_type == 'customer':
                inv_tax_ids = self.env['account.invoice.tax'].search([
                    ('invoice_id.account_fiscal_position_rule_id', '=', rule.id),
                    ('invoice_id.state', 'not in', ['cancel', 'draft']),
                    ('invoice_id.type', 'in', ['out_invoice', 'out_refund'])
                ])
                rule.amount_total = sum(
                    line.base for line in inv_tax_ids if line.amount == 0.0 and
                    line.invoice_id.type == 'out_invoice') - sum(
                    line.base for line in inv_tax_ids if line.amount == 0.0 and
                    line.invoice_id.type == 'out_refund')

    amount_total = fields.Float(
        compute=_get_amount_total, string='Total amount used')

    def _map_domain(self, partner, addrs, company, **kwargs):
        domain = super(AccountFiscalPositionRule, self)._map_domain(
            partner, addrs, company, **kwargs)
        domain += [('partner_id', '=', partner.id), ('inactive', '!=', True)]
        return domain

    def apply_fiscal_mapping(self, result, **kwargs):
        fp_id = result['value'].get('fiscal_position', False)
        result = super(AccountFiscalPositionRule, self).apply_fiscal_mapping(
            result, **kwargs)
        if not result['value'].get('fiscal_position', False) and fp_id:
            result['value'].update({'fiscal_position': fp_id})
        return result

    def fiscal_position_map(self, **kwargs):
        result = super(AccountFiscalPositionRule, self
                       ).fiscal_position_map(**kwargs)
        partner_id = kwargs.get('partner_id')
        company_id = kwargs.get('company_id')
        partner_invoice_id = kwargs.get('partner_invoice_id')
        partner = self.env['res.partner'].browse(partner_id)
        company = self.env['res.company'].browse(company_id)
        addrs = {}
        if partner_invoice_id:
            addrs['invoice'] = self.env['res.partner'].browse(
                partner_invoice_id)
        domain = self._map_domain(partner, addrs, company, **kwargs)
        fsc_pos = self.search(domain)
        if fsc_pos:
            result['fiscal_position'] = fsc_pos[0].fiscal_position_id.id
            result.update({'account_fiscal_position_rule_id': fsc_pos[0].id})
        elif partner.property_account_position:
            result['fiscal_position'] = partner.property_account_position.id
            result.update({'account_fiscal_position_rule_id': False})
        else:
            result.update({'account_fiscal_position_rule_id': False})
        return result


class ResPartner(models.Model):
    _inherit = "res.partner"

    account_fiscal_position_rule_ids = fields.One2many(
        comodel_name='account.fiscal.position.rule',
        inverse_name='partner_id',
        string="Vat exemption declarations",
    )


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    account_fiscal_position_rule_id = fields.Many2one(
        comodel_name='account.fiscal.position.rule',
        readonly=True, states={'draft': [('readonly', False)]},
        string='Fiscal Position Rule',
    )

    @api.onchange('fiscal_position')
    def onchange_fiscal_position(self):
        if self.account_fiscal_position_rule_id and self.fiscal_position:
            if self.fiscal_position != \
                    self.account_fiscal_position_rule_id.fiscal_position_id:
                self.account_fiscal_position_rule_id = False
