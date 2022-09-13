# Copyright 2022 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    enable_reserve_date_check = fields.Boolean(
        help="Forbid reservation on not possible date",
        default=True, copy=False)

    @api.multi
    def action_confirm(self):
        # Add variable in context to enable check
        for order in self:
            if order.enable_reserve_date_check:
                for line in order.order_line.filtered('product_id'):
                    commitment_date = line.commitment_date and\
                        line.commitment_date.date() \
                        or line.order_id.commitment_date and \
                        line.order_id.commitment_date.date() or \
                        line.order_id.date_order and line.order_id.date_order.date()
                    avail_date, avail_date_info = line.get_available_date(
                        line.product_id,
                        line.product_uom_qty,
                        commitment_date)
                    if avail_date > commitment_date:
                        dates_info = avail_date_info.split('\n')
                        commitment_date_str = commitment_date.strftime('%d/%m/%Y')
                        dates_info_clean = [
                            x for x in dates_info if commitment_date_str not in x
                            and x != '']
                        dates_info_clean.reverse()
                        raise UserError(_(
                            "Reservation of product [[%s] %s] not possible for date %s!"
                            "\nAvailable date: %s %s\n"
                            "Exception availability info:\n%s") % (
                                line.product_id.default_code,
                                line.product_id.name,
                                avail_date.strftime('%d/%m/%Y'),
                                commitment_date.strftime('%d/%m/%Y'),
                                '(Produce delay: %.0f days)' % int(
                                    line.product_id.produce_delay)
                                if line.product_id.produce_delay else '',
                                '\n'.join([x for x in dates_info_clean])
                            ))
        super().action_confirm()
        return True
