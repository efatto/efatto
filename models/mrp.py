# Copyright 2020 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    @api.multi
    def write(self, vals):
        res = super(MrpProduction, self).write(vals)
        for mo in self.filtered(lambda x: x.procurement_group_id.sale_id):
            mo.procurement_group_id.sale_id.update_forecast_state()
        return res
