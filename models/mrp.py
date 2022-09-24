# Copyright 2020 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class MrpProductProduce(models.TransientModel):
    _inherit = "mrp.product.produce"

    @api.multi
    def do_produce(self):
        res = super(MrpProductProduce, self).do_produce()
        for mo in self.production_id.filtered(lambda x: x.sale_id):
            mo.sale_id.update_forecast_state()
        return res


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    additional_state = fields.Selection([
        ('submanufacture_started', 'Submanufacture started'),
        ('submanufacture_done', 'Submanufacture done'),
        ('test_check', 'Test check'),
    ], string="Additional state")

    @api.multi
    def button_mark_done(self):
        res = super(MrpProduction, self).button_mark_done()
        for mo in self.filtered(lambda x: x.sale_id):
            mo.sale_id.update_forecast_state()
        return res
