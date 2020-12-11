# Copyright 2020 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    tag_id = fields.Many2one('account.analytic.tag', string="Tag", copy=True)

    @api.model
    def create(self, values):
        if self._context.get('invoice'):
            invoice = self._context['invoice']
            if invoice.type in ['out_invoice', 'out_refund']:
                tag_id = self._get_tag(_('Sales'))
            else:
                tag_id = self._get_tag(_('Purchases'))
        else:
            tag_id = self._get_tag(_('Timesheets'))
        # tag_id = self._get_tags('Materials')
        # tag_id = self._get_tags('Generic')
        values.update({
            'tag_id': tag_id.id
        })
        res = super(AccountAnalyticLine, self).create(values)
        return res

    @api.multi
    def _get_tag(self, name):
        tag_id = self.env['account.analytic.tag'].search([
            ('name', '=', name)
        ], limit=1)
        if not tag_id:
            tag_id = self.env['account.analytic.tag'].create({
                'name': name
            })
        return tag_id
