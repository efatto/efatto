# Copyright 2020 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.multi
    def write(self, vals):
        res = super(StockPicking, self).write(vals)
        for pick in self:
            if pick.sale_id:
                pick.sale_id.update_forecast_state()
        return res

    @api.multi
    def do_transfer(self):
        for pick in self:
            pick.sale_id.update_forecast_state()
        return super(StockPicking, self).do_transfer()
