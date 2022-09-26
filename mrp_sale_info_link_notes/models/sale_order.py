from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    production_notes = fields.Text()
    production_notes_calendar = fields.Text(
        compute='_compute_production_notes_calendar', store=True)
    is_prototype = fields.Boolean()
    is_prototype_calendar = fields.Text(
        compute='_compute_is_prototype_calendar', store=True)

    @api.multi
    @api.depends('production_notes')
    def _compute_production_notes_calendar(self):
        for order in self:
            order.production_notes_calendar = _('MO Notes: %s') % \
                order.production_notes if order.production_notes else ''

    @api.multi
    @api.depends('is_prototype')
    def _compute_is_prototype_calendar(self):
        for order in self:
            order.is_prototype_calendar = _('PROTOTYPE') \
                if order.is_prototype else ''
