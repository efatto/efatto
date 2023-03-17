from odoo import api, fields, models


class DdTFromPickings(models.TransientModel):
    _inherit = "ddt.from.pickings"

    stock_ddt_type_id = fields.Many2one(
        comodel_name='stock.ddt.type'
    )

    @api.multi
    def create_ddt(self):
        res = super().create_ddt()
        if res and self.stock_ddt_type_id:
            ddt = self.env[res['res_model']].browse(res['res_id'])
            if set(ddt.picking_ids.mapped('picking_type_code')) != {'internal'}:
                # only internal ddt are managed here
                return res
            ddt.partner_shipping_id = ddt.partner_id
            ddt.ddt_type_id = self.stock_ddt_type_id
            # check ddt type defaults
            if self.stock_ddt_type_id and \
                    self.stock_ddt_type_id.default_carriage_condition_id:
                ddt.carriage_condition_id = \
                    self.stock_ddt_type_id.default_carriage_condition_id
            if self.stock_ddt_type_id and \
                    self.stock_ddt_type_id.default_goods_description_id:
                ddt.goods_description_id = \
                    self.stock_ddt_type_id.default_goods_description_id
            if self.stock_ddt_type_id and \
                    self.stock_ddt_type_id.default_transportation_reason_id:
                ddt.transportation_reason_id = \
                    self.stock_ddt_type_id.default_transportation_reason_id
            if self.stock_ddt_type_id and \
                    self.stock_ddt_type_id.default_transportation_method_id:
                ddt.transportation_method_id = \
                    self.stock_ddt_type_id.default_transportation_method_id
            # check partner defaults
            if ddt.partner_id and \
                    ddt.partner_id.carriage_condition_id:
                ddt.carriage_condition_id = \
                    ddt.partner_id.carriage_condition_id
            if ddt.partner_id and \
                    ddt.partner_id.goods_description_id:
                ddt.goods_description_id = \
                    ddt.partner_id.goods_description_id
            if ddt.partner_id and \
                    ddt.partner_id.transportation_reason_id:
                ddt.transportation_reason_id = \
                    ddt.partner_id.transportation_reason_id
            if ddt.partner_id and \
                    ddt.partner_id.transportation_method_id:
                ddt.transportation_method_id = \
                    ddt.partner_id.transportation_method_id

            ir_model_data = self.env['ir.model.data']
            form_res = ir_model_data.get_object_reference(
                'l10n_it_ddt_menu_in_out',
                'stock_picking_package_preparation_form_supplier')
            form_id = form_res and form_res[1] or False
            res.update({
                'view_id': [form_id],
                'views': [(form_id, 'form')],
            })
        return res
