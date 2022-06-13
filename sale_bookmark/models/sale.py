# Copyright 2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    bookmarked = fields.Boolean(
        string='Computed bookmarked',
        compute='_compute_bookmarked', store=True)
    bookmarked_manual = fields.Boolean(
        readonly=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})

    @api.multi
    @api.depends('state', 'bookmarked_manual')
    def _compute_bookmarked(self):
        bookmark_state = self.env['ir.config_parameter'].sudo().get_param(
            'sale.order.bookmark.state', default=False)
        for order in self:
            if bookmark_state:
                order.bookmarked = (
                    bool(order.state == bookmark_state) or order.bookmarked_manual)
            else:
                order.bookmarked = order.bookmarked_manual
