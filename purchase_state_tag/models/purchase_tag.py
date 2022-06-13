# Copyright 2022 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models, _


class PurchaseOrderTag(models.Model):
    _name = 'purchase.order.tag'
    _description = 'Purchase order tag'

    name = fields.Char(string='Purchase Order Tag', index=True, required=True)
    active = fields.Boolean(
        default=True,
        help="Set active to false to hide the Purchase Order Tag without removing it.")
    color = fields.Integer()
    order_state = fields.Selection(selection='_get_order_state')
    company_id = fields.Many2one('res.company', string='Company')

    _sql_constraints = [(
        'purchase_tag_uniq',
        'unique(color, company_id)',
        _('A tag type for the same order state already exists for this company!')
    )]

    @api.model
    def _get_order_state(self):
        order_state = self.env['purchase.order']._fields['state'].selection
        return order_state
