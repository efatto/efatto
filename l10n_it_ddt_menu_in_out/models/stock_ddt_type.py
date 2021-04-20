# Copyright 2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields, api
from odoo.exceptions import Warning as UserError


class StockDdtType(models.Model):
    _inherit = 'stock.ddt.type'
    _order = 'sequence, id'

    @api.multi
    @api.depends('stock_location_ids')
    def _compute_usage(self):
        for stock_ddt_type in self:
            usage = list(set(stock_ddt_type.stock_location_ids.mapped('usage')))
            if len(usage) > 1:
                raise UserError('Usage must be only one!')
            stock_ddt_type.usage = usage and usage[0] or False

    sequence = fields.Integer('Priority', default=10)
    stock_location_ids = fields.Many2many(
        comodel_name='stock.location',
        string='Stock locations',
    )
    usage = fields.Selection([
        ('supplier', 'Vendor Location'),
        ('view', 'View'),
        ('internal', 'Internal Location'),
        ('customer', 'Customer Location'),
        ('inventory', 'Inventory Loss'),
        ('procurement', 'Procurement'),
        ('production', 'Production'),
        ('transit', 'Transit Location')],
        string='Location Type',
        readonly=True,
        compute=_compute_usage,
        store=True,
    )
