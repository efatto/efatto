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
        ('blocked', 'Blocked'),
        ('to_produce', 'Waiting material'),
        ('to_assembly', 'To assembly'),
        ('to_submanufacture', 'To submanufacture'),
        ('to_test', 'To test'),
    ], string="Additional state", copy=False)
    blocked_note = fields.Char()

    @api.multi
    def button_mark_done(self):
        res = super(MrpProduction, self).button_mark_done()
        for mo in self.filtered(lambda x: x.sale_id):
            mo.sale_id.update_forecast_state()
            mo.additional_state = False
        return res

    @api.multi
    def button_mark_to_produce(self):
        for mo in self:
            mo.additional_state = 'to_produce'

    @api.multi
    def button_mark_to_submanufacture(self):
        for mo in self:
            mo.additional_state = 'to_submanufacture'

    @api.multi
    def button_mark_to_test(self):
        for mo in self:
            mo.additional_state = 'to_test'

    @api.multi
    def button_mark_not_blocked(self):
        for mo in self:
            mo.write({
                'additional_state': False,
                'blocked_note': False,
            })

    @api.multi
    def post_inventory(self):
        res = super().post_inventory()
        for mo in self:
            mo.additional_state = 'to_assembly'
        return res
