from odoo import models, api, _, exceptions


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _preparare_ddt_data(self):
        res = super()._preparare_ddt_data()
        ddt_type = self.warehouse_id.out_type_id.default_location_dest_id.type_ddt_id
        if ddt_type:
            if not res.get('carriage_condition_id', False):
                res['carriage_condition_id'] = \
                    ddt_type.default_carriage_condition_id.id
            if not res.get('goods_description_id', False):
                res['goods_description_id'] = \
                    ddt_type.default_goods_description_id.id
            if not res.get('transportation_reason_id', False):
                res['transportation_reason_id'] = \
                    ddt_type.default_transportation_reason_id.id
            if not res.get('transportation_method_id', False):
                res['transportation_method_id'] = \
                    ddt_type.default_transportation_method_id.id
        return res

    @api.multi
    def action_cancel(self):
        for order in self:
            for ddt in order.ddt_ids:
                if ddt.state in ['done', 'in_pack']:
                    raise exceptions.Warning(_(
                        'DDT is already done or in pack. Put in draft state to '
                        'remove this warning.'))
                if ddt.ddt_number:
                    sequence = ddt.ddt_type_id.sequence_id
                    prefix, suffix = sequence._get_prefix_suffix()
                    ddt_number = ddt.ddt_number.replace(prefix, '').replace(suffix, '')
                    number_next = sequence._get_current_sequence(
                        sequence_date=ddt.date).number_next_actual
                    ddt_number_int = int(ddt_number)
                    if ddt_number_int + 1 == number_next:
                        if sequence.use_date_range:
                            date_range_sequence = sequence.date_range_ids.filtered(
                                lambda x: x.date_from <= ddt.date <= x.date_to
                            )
                            if date_range_sequence:
                                date_range_sequence.number_next_actual = ddt_number_int
                        else:
                            sequence.number_next_actual = ddt_number_int
                ddt.unlink()
        return super(SaleOrder, self).action_cancel()
