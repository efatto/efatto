from odoo import api, fields, models
from odoo.tools.date_utils import relativedelta


class SupplierInfo(models.Model):
    _inherit = "product.supplierinfo"

    overtime_purchase_delay = fields.Integer(
        compute="_compute_overtime_purchase_delay",
        store=True,
        help="Over the past x days (configured in parameter "
        "'purchase_stock.on_time_delivery_days', by default 365 days): the number "
        "of days over time of a minimum 3 days for this vendor to deliver this "
        "product.",
    )
    normal_purchase_delay = fields.Integer(
        compute="_compute_overtime_purchase_delay",
        store=True,
        help="Over the past x days (configured in parameter "
        "'purchase_stock.on_time_delivery_days', by default 365 days): the number "
        "of days for this vendor to deliver this product, computed on the first "
        "delivery date.",
    )
    overtime_move_ids = fields.Many2many(
        comodel_name="stock.move",
        compute="_compute_overtime_purchase_delay",
        store=True,
    )

    @api.depends("name.purchase_line_ids", "name.purchase_line_ids.move_ids")
    def _compute_overtime_purchase_delay(self):
        for seller in self:
            overtime_purchase_delay = 0
            normal_purchase_delay = 0
            overtime_move_ids = False
            if seller.name.purchase_line_ids:
                date_order_days_delta = int(
                    self.env["ir.config_parameter"]
                    .sudo()
                    .get_param("purchase_stock.on_time_delivery_days", default="365")
                )
                order_lines = seller.name.purchase_line_ids.filtered(
                    lambda l: l.date_order
                    > fields.Datetime.today()
                    - relativedelta(days=date_order_days_delta)
                    and l.order_id.state in ["done", "purchase"]
                    and (
                        l.product_id == seller.product_id
                        or l.product_id.product_tmpl_id == seller.product_tmpl_id
                    )
                )
                if not order_lines:
                    continue
                overtime_moves = order_lines.move_ids.filtered(
                    lambda m: m.state == "done"
                    and (
                        m.product_id == seller.product_id
                        or m.product_id.product_tmpl_id == seller.product_tmpl_id
                    )
                    and m.date
                    > (m.purchase_line_id.date_planned + relativedelta(days=3))
                )
                if overtime_moves:
                    overtime_purchase_delay = sum(
                        (m.date.date() - m.purchase_line_id.date_planned.date()).days
                        for m in overtime_moves
                    ) / len(overtime_moves)
                    overtime_move_ids = overtime_moves
                delivery_move_ids = order_lines.move_ids.filtered(
                    lambda m: m.state == "done"
                    and (
                        m.product_id == seller.product_id
                        or m.product_id.product_tmpl_id == seller.product_tmpl_id
                    )
                ).sorted(lambda m: m.date)
                first_delivery_move_ids = self.env["stock.move"]
                for order_line in order_lines:
                    first_delivery_move_ids |= delivery_move_ids.filtered(
                        lambda m, o=order_line: m.purchase_line_id == o
                    )[:1]
                if first_delivery_move_ids:
                    normal_purchase_delay = (
                        sum(
                            (
                                fdm_id.date.date()
                                - fdm_id.purchase_line_id.order_id.date_order.date()
                            ).days
                            for fdm_id in first_delivery_move_ids
                        )
                    ) / len(first_delivery_move_ids)
            seller.overtime_purchase_delay = overtime_purchase_delay
            seller.normal_purchase_delay = normal_purchase_delay
            seller.overtime_move_ids = overtime_move_ids

    def open_view_stock_move_overtime(self):
        domain = [
            ("id", "in", self.overtime_move_ids.ids),
        ]
        view = self.env.ref(
            "stock_move_available_date_expected.view_stock_reserved_tree"
        )
        return {
            "type": "ir.actions.act_window",
            "name": "Stock received overtime",
            "domain": domain,
            "views": [(view.id, "tree"), (False, "pivot")],
            "res_model": "stock.move",
            "context": {},
        }
