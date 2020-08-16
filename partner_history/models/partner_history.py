# Copyright 2020 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class ResPartnerHistory(models.Model):
    _name = 'res.partner.history'
    _description = 'Partner history'

    name = fields.Char(required=True)
    date_from = fields.Date(
        required=True,
        default=lambda x: fields.Date.from_string('1900-01-01'))
    date_to = fields.Date(required=True)
    partner_id = fields.Many2one(
        comodel_name='res.partner', string='Partner', ondelete='cascade'
    )

    @api.multi
    @api.constrains('date_from', 'date_to')
    def check_overlap(self):
        for rec in self:
            date_domain = [
                ('date_from', '<=', rec.date_to),
                ('date_to', '>=', rec.date_from)]

            overlap = self.search(date_domain + [('id', '!=', rec.id)])

            if overlap:
                raise ValidationError(
                    _('Partner history term %s overlaps with %s') %
                    (rec.name, overlap[0].name))
