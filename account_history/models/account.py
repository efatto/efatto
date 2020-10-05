# -*- coding: utf-8 -*-

from openerp import fields, models, api, _
from openerp.exceptions import ValidationError


class AccountAccount(models.Model):
    _inherit = 'account.account'

    account_history_ids = fields.One2many(
        comodel_name='account.account.history',
        inverse_name='account_id',
        string='Account history'
    )


class AccountAccountHistory(models.Model):
    _name = 'account.account.history'
    _description = 'Account history'

    name = fields.Char(required=True)
    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)
    account_id = fields.Many2one(
        comodel_name='account.account', string='Account', ondelete='cascade'
    )

    @api.multi
    @api.constrains('date_from', 'date_to')
    def check_overlap(self):
        for rec in self:
            date_domain = [
                ('account_id', '=', rec.account_id.id),
                ('id', '!=', rec.id),
                ('date_from', '<=', rec.date_to),
                ('date_to', '>=', rec.date_from)]

            overlap = self.search(date_domain)

            if overlap:
                raise ValidationError(
                    _('Overdue Term %s overlaps with %s') %
                    (rec.name, overlap[0].name))
