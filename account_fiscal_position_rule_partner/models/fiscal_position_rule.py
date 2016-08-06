# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, _


class AccountFiscalPositionRule(models.Model):
    _inherit = 'account.fiscal.position.rule'

    number_protocol = fields.Integer('Exemption declaration protocol Number')
    partner_id = fields.Many2one('res.partner', 'Partner')
    date_issue = fields.Date('Exemption declaration Issue Date')
    date_reception = fields.Date('Exemption declaratione Reception Date')
    exemption_type = fields.Selection([
        ('S', 'Single Operation'),
        ('P', 'Period'),
        ('I', 'Import')
    ], 'Exemption Type')
    amount_max = fields.Float('Max Amount')
    inactive = fields.Boolean('Inactive')
    exemption_proof = fields.Binary(
        'Exemption proof of posting',)
    company_id = fields.Many2one(
        'res.company', 'Company', required=True,
        default=lambda self: self.env['res.company']._company_default_get(
            'account.fiscal.position.rule'))

    def _map_domain(self, partner, addrs, company, **kwargs):
        domain = super(AccountFiscalPositionRule, self)._map_domain(
            partner, addrs, company, **kwargs)
        domain += [('partner_id', '=', partner.id)]
        return domain

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
        elif partner.property_account_position:
            result['fiscal_position'] = partner.property_account_position.id
        return result


class ResPartner(models.Model):
    _inherit = "res.partner"

    account_fiscal_position_rule_ids = fields.One2many(
        comodel_name='account.fiscal.position.rule',
        inverse_name='partner_id',
        string="Vat exemption declarations",
    )
