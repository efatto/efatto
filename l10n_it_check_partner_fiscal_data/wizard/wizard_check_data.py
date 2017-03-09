# -*- coding: utf-8 -*-
from openerp import fields, models, api, _


class WizardCheckData(models.TransientModel):
    _name = "wizard.check.data"
    
    # vat = fields.Boolean('Controlla P.IVA', default=True)
    # fiscalcode = fields.Boolean('Controlla C.Fiscale', default=True)
    fy = fields.Many2one('account.fiscalyear', string='Fiscal year')

    @api.multi
    def check_data(self):
        self.ensure_one()
        partners_obj = self.env['res.partner']
        periods = self.env['account.period'].search(
            [('fiscalyear_id', '=', self.fy.id)])
        partners = partners_obj.search([
            ('vat', '=', False),
            ('fiscalcode', '=', False),
        ])
        invoices = self.env['account.invoice'].search([
            ('period_id', 'in', periods.ids),
            ('partner_id', 'in', partners.ids)
        ])

        missing_data_partner_ids = invoices.mapped('partner_id')

        return {
                'name': _("Partner missing data"),
                'view_mode': 'tree,form',
                'view_id': False,
                'view_type': 'form',
                'res_model': 'res.partner',
                'type': 'ir.actions.act_window',
                'domain': [('id', 'in', missing_data_partner_ids.ids)],
                'context': self._context,
            }
