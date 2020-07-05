from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class ResPartnerHistory(models.Model):
    _name = 'res.partner.history'
    _description = 'Partner history'

    name = fields.Char(required=True)
    date_from = fields.Date()
    date_to = fields.Date()
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

            overlap = self.search(date_domain + [('id', '!=', self.id)])

            if overlap:
                raise ValidationError(
                    _('Overdue Term %s overlaps with %s') %
                    (rec.name, overlap[0].name))
