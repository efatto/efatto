# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import api, _, models, fields


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.multi
    def _get_sppp_exist(self):
        for pick in self:
            pick.sppp_exist = pick.ddt_ids and True or False

    sppp_exist = fields.Boolean(
        compute='_get_sppp_exist',
        string='SPPP Exists?',
        help='technical field for attrs in view')
