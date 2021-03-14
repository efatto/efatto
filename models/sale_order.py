# Copyright 2020 Tecnativa - Ernesto Tejeda
# Copyright 2021 Sergio Corato <https://github.com/sergiocorato>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from collections import defaultdict
from datetime import timedelta

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.depends('product_id', 'customer_lead', 'product_uom_qty',
                 'order_id.warehouse_id', 'order_id.commitment_date',
                 'product_id.produce_delay', 'product_id.purchase_delay',
                 'product_id.sale_delay')
    def _compute_qty_at_date(self):
        """ Based on _compute_free_qty method of sale.order.line
            model in Odoo v13 'sale_stock' module.
        """
        super()._compute_qty_at_date()
        qty_processed_per_product = defaultdict(lambda: 0)
        grouped_lines = defaultdict(lambda: self.env['sale.order.line'])
        now = fields.Datetime.now()
        for line in self.sorted(key=lambda r: r.sequence):
            if not line.display_qty_widget:
                continue
            line.warehouse_id = line.order_id.warehouse_id
            # REMOVE use of commitment_date as scheduled date shown in popup
            if line.order_id.state in ['sale', 'done']:
                confirm_date = line.order_id.confirmation_date
            else:
                confirm_date = now
            # add produce_delay to customer_lead (equal to line.product_id.sale_delay)
            date = confirm_date + timedelta(
                days=(
                    (line.customer_lead or 0.0) +
                    (line.product_id.produce_delay or 0.0) +
                    (line.product_id.purchase_delay or 0.0)
                )
            )
            grouped_lines[(line.warehouse_id.id, date)] |= line
        treated = self.browse()
        for (warehouse, scheduled_date), lines in grouped_lines.items():
            for line in lines:
                product = line.product_id.with_context(
                    to_date=(line.commitment_date + timedelta(
                        days=-line.product_id.sale_delay)
                    ), warehouse=warehouse)
                qty_available = product.qty_available
                free_qty = product.free_qty
                virtual_available = product.virtual_available
                qty_processed = qty_processed_per_product[product.id]
                line.scheduled_date = scheduled_date
                line.qty_available_today = qty_available - qty_processed
                line.free_qty_today = free_qty - qty_processed
                virtual_available_at_date = virtual_available - qty_processed
                line.virtual_available_at_date = virtual_available_at_date
                qty_processed_per_product[product.id] += line.product_uom_qty
            treated |= lines
        remaining = (self - treated)
        remaining.write({
            "virtual_available_at_date": False,
            "scheduled_date": False,
            "free_qty_today": False,
            "qty_available_today": False,
            "warehouse_id": False,
        })


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def _get_customer_lead(self, product_tmpl_id):
        super()._get_customer_lead(product_tmpl_id)
        return (
            product_tmpl_id.sale_delay +
            product_tmpl_id.produce_delay +
            product_tmpl_id.purchase_delay
        )

    @api.depends('picking_policy')
    def _compute_expected_date(self):
        super()._compute_expected_date()
        for order in self:
            dates_list = []
            confirm_date = fields.Datetime.from_string(
                (order.confirmation_date or order.write_date
                 ) if order.state == 'sale' else fields.Datetime.now())
            for line in order.order_line.filtered(
                    lambda x: x.state != 'cancel' and not x._is_delivery()):
                dt = confirm_date + timedelta(
                    days=(
                        (line.customer_lead or 0.0) +
                        (line.product_id.produce_delay or 0.0) +
                        (line.product_id.purchase_delay or 0.0)
                    )
                )
                dates_list.append(dt)
            if dates_list:
                expected_date = min(dates_list) if order.picking_policy == 'direct' \
                    else max(dates_list)
                order.expected_date = fields.Datetime.to_string(expected_date)
