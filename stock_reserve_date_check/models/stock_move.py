# Copyright 2022 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models, _
from odoo.tools.date_utils import relativedelta
from odoo.exceptions import ValidationError


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _action_assign(self):
        # do the check after reservation, as a product can be reserved from many moves
        # and we need to check values after all moves
        if self._context.get('params', False) and self._context.get('params').get(
                'model', '') == 'mrp.production':
            # for production do the check before super() because of mrp_subproduction
            # anyway this check will be done after reservation of production, as it is
            # no more a default check and the only way to activate it from production
            # is to unreserve and re-reserve the production
            self.check_reserve_date()
        res = super()._action_assign()
        self.check_reserve_date()
        return res

    def check_reserve_date(self):
        if self._context.get('enable_reserve_date_check', False):
            manufacture_route = self.env.ref('mrp.route_warehouse0_manufacture')
            product_ids = self.mapped('product_id')
            available_info = {}
            # dict of dict with:
            # {product_id: {move_date: virtual_available_at_date_expected}}
            today = fields.Date.today()
            for product_id in product_ids:
                available_info.update({product_id.id: {}})
                domain_quant_loc, domain_move_in_loc, domain_move_out_loc = \
                    product_id._get_domain_locations()
                incoming_stock_moves = self.env['stock.move'].search([
                    ('product_id', '=', product_id.id),
                    ('product_uom_qty', '>', 0),
                    ('state', 'not in', ['done', 'cancel']),
                    ('date', '>=', today),
                ] + domain_move_in_loc)
                reserved_stock_moves = self.env['stock.move'].search([
                    ('product_id', '=', product_id.id),
                    ('product_uom_qty', '>', 0),
                    ('state', 'not in', ['done', 'cancel']),
                    ('date', '>=', today),
                ] + domain_move_out_loc)
                for move_date in (
                    set(
                        [x.date() for x in reserved_stock_moves.mapped('date_expected')]
                        + [y.date() for y in incoming_stock_moves.mapped('date_expected')]
                    )
                ):
                    available_info[product_id.id].update({
                        move_date: product_id.with_context(
                            to_date=move_date
                        ).virtual_available_at_date_expected
                    })
            for move in self:
                if move.date_expected:
                    # limit check to date >= expected date
                    product_dict = available_info[move.product_id.id]
                    product_available_info = {
                        x: product_dict[x]
                        for x in product_dict
                        if x >= move.date_expected.date()}
                    # extend available_info with move.date_expected
                    product_available_info.update({
                        move.date_expected.date():
                            move.product_id.with_context(
                                to_date=move.date_expected
                        ).virtual_available_at_date_expected
                    })
                    # remove dates after purchasable date (n.b. a reorder rule must
                    # exits to cover the request)
                    if move.product_id.bom_ids and \
                            manufacture_route in move.product_id.route_ids:
                        delay = move.product_id.produce_delay
                    else:
                        delay = move.product_id.purchase_delay
                    available_date = today + relativedelta(days=delay)
                    date_not_available_info = {
                        x: product_available_info[x]
                        for x in product_available_info
                        if x < available_date
                        and (
                            product_available_info[x] < 0
                            or (
                               move.procure_method == 'make_to_order'
                               and
                               manufacture_route in move.product_id.route_ids
                            )
                        )}
                    if date_not_available_info:
                        raise ValidationError(_(
                            "Reservation of product [[%s] %s] not possible for date %s!"
                            "\nAvailable date: %s\n"
                            "Exception availability info:\n%s") % (
                                move.product_id.default_code,
                                move.product_id.name,
                                move.date_expected.strftime('%d/%m/%Y'),
                                available_date.strftime('%d/%m/%Y'),
                                ''.join([
                                    _('Date: %s qty: %s\n') % (
                                        x.strftime('%d/%m/%Y'),
                                        date_not_available_info[x])
                                    for x in sorted(date_not_available_info)
                                ]),
                            )
                        )
