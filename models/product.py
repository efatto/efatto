# Copyright 2021 Sergio Corato <https://github.com/sergiocorato>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models
from odoo.tools.date_utils import relativedelta


class ProductTemplate(models.Model):
    _inherit = "product.template"

    purchase_delay = fields.Float(
        'Purchase Lead Time', compute='_get_purchase_delay',
        store=True, default=0.0,
        help="Lead time in days to purchase this product. "
             "Computed from delay of first seller.")

    @api.depends('seller_ids', 'seller_ids.delay')
    def _get_purchase_delay(self):
        for product_tmpl in self:
            if product_tmpl.seller_ids and product_tmpl.purchase_ok:
                product_tmpl.purchase_delay = product_tmpl.seller_ids[:1].delay
            else:
                product_tmpl.purchase_delay = 0


class ProductProduct(models.Model):
    _inherit = "product.product"

    def get_available_date(self, qty, date_start):
        self.ensure_one()
        available_date = False
        available_dates_info = []
        domain_quant_loc, domain_move_in_loc, domain_move_out_loc = \
            self._get_domain_locations()
        incoming_stock_moves = self.env['stock.move'].search([
            ('product_id', '=', self.id),
            ('product_uom_qty', '>', 0),
            ('state', 'not in', ['done', 'cancel']),
        ] + domain_move_in_loc)
        reserved_stock_moves = self.env['stock.move'].search([
            ('product_id', '=', self.id),
            ('product_uom_qty', '>', 0),
            ('state', 'not in', ['done', 'cancel']),
            # ('reserved_availability', '>', 0),
        ] + domain_move_out_loc)
        for reserve_date in (
                reserved_stock_moves.mapped('date_expected') +
                incoming_stock_moves.mapped('date_expected')
        ):
            available_dates_info.append({
                'date': reserve_date,
                'qty': self.with_context(
                    to_date=reserve_date
                ).virtual_available_at_date_expected
            })
        #todo remove all availability with a prior availability with qty <
        # requested qty
        # get the available date later of the far available date with qty <
        if available_dates_info:
            farther_unreservable_dates = [
                x['date'] for x in available_dates_info if x['qty'] < qty
            ]
            if not farther_unreservable_dates:
                # all dates have a sufficient qty
                farther_unreservable_dates = [min([
                    x['date'] for x in available_dates_info
                ])]
            if farther_unreservable_dates:
                available_date = min([
                    x['date'] for x in available_dates_info if x['date']
                    >= max(farther_unreservable_dates)
                ] or [False])
        if not available_date:
            # This product must be ordered
            available_date = date_start
            if self.bom_ids:
                # fixme need to filter boms?
                bom_id = self.bom_ids[0]
                available_date = max([x.product_id.get_available_date(
                    qty * x.product_qty, date_start)
                             for x in bom_id.bom_line_ids] or [0]
                )
                if bom_id.routing_id:
                    delay = sum(bom_id.mapped(
                        'routing_id.operation_ids.time_cycle_manual') or [0]) / 1440
                    available_date += relativedelta(days=int(delay))
            else:
                delay = self.purchase_delay
                available_date += relativedelta(days=int(delay))
        if not available_dates_info:
            available_dates_info = ''
        else:
            available_dates_info = str(available_dates_info)
        return available_date, available_dates_info
