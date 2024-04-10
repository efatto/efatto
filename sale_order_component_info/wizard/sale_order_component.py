# Copyright 2021 Sergio Corato <https://github.com/sergiocorato>
# Copyright 2020 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from collections import defaultdict
from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_round


class SaleComponent(models.TransientModel):
    _name = "sale.component"
    _description = "Sale component"

    @api.model
    def _get_sale_order_line(self):
        sale_order_line = self.env["sale.order.line"].browse(
            self._context.get("active_id", [])
        )
        return sale_order_line

    def _get_components(self):
        res = []
        sale_order_line = self.env["sale.order.line"].browse(
            self._context.get("active_id", [])
        )
        product = (
            sale_order_line.product_id.id
            if sale_order_line.product_id.type != "service"
            else False
        )
        if product:
            # get all products from bom and its children
            child_products = sale_order_line.order_id._bom_explode(
                sale_order_line.product_id, []
            )
            child_dict = {}
            for x in child_products:
                if x["product_id"] not in child_dict:
                    child_dict.update({x["product_id"]: x["qty"]})
                else:
                    child_dict[x["product_id"]] += x["qty"]
            vals = []
            for child_product in child_dict:
                product_dict = {
                    "product_id": child_product,
                    "sale_order_line_id": sale_order_line.id,
                    "component_bom_qty": child_dict[child_product],
                }
                parent_id = [
                    y["parent_id"]
                    for y in child_products
                    if y["product_id"] == child_product and y["parent_id"] != product
                ]
                if parent_id:
                    product_dict.update({"parent_id": parent_id[0]})
                vals.append(product_dict)
            if vals:
                # sort vals to create sale component line parent before children
                vals.sort(key=lambda t: t.get("parent_id", 0))
            for val in vals:
                if val.get("parent_id", False):
                    parent_id = [x for x in res if x.product_id.id == val["parent_id"]]
                    if parent_id:
                        val.update({"parent_id": parent_id[0].id})
                res.append(self.env["sale.component.line"].create(val))
            res = [x.id for x in res]
        return self.env["sale.component.line"].browse(res)

    sale_order_line_id = fields.Many2one(
        comodel_name="sale.order.line", default=_get_sale_order_line, readonly=True
    )
    line_ids = fields.Many2many(
        comodel_name="sale.component.line",
        string="Components",
        default=_get_components,
        readonly=True,
    )


class SaleComponentLine(models.TransientModel):
    _name = "sale.component.line"
    _description = "Sale component line"

    sale_order_line_id = fields.Many2one(comodel_name="sale.order.line", readonly=True)
    product_id = fields.Many2one(comodel_name="product.product", readonly=True)
    parent_id = fields.Many2one(
        comodel_name="sale.component.line", string="Parent", readonly=True
    )
    parent_product_id = fields.Many2one(
        related="parent_id.product_id", string="Parent Product"
    )
    child_ids = fields.One2many(
        "sale.component.line", "parent_id", string="Child Lines", readonly=True
    )
    state = fields.Selection(related="sale_order_line_id.state")
    commitment_date = fields.Datetime(related="sale_order_line_id.commitment_date")
    customer_lead = fields.Float(related="sale_order_line_id.customer_lead")
    product_type = fields.Selection(related="product_id.type")
    qty_available = fields.Float(related="product_id.qty_available")
    incoming_qty = fields.Float(related="product_id.incoming_qty")
    outgoing_qty = fields.Float(related="product_id.outgoing_qty")
    bookmarked_qty = fields.Float(related="product_id.bookmarked_qty")
    component_bookmarked_qty = fields.Float(compute="_compute_qty_at_date")
    virtual_available = fields.Float(related="product_id.virtual_available")
    sol_product_uom_qty = fields.Float(related="sale_order_line_id.product_uom_qty")
    sol_qty_delivered = fields.Float(related="sale_order_line_id.qty_delivered")
    product_uom = fields.Many2one(related="sale_order_line_id.product_uom")
    component_bom_qty = fields.Float(readonly=True)
    virtual_available_at_date = fields.Float(
        compute="_compute_qty_at_date", digits="Product Unit of Measure")
    scheduled_date = fields.Datetime(compute="_compute_qty_at_date")
    free_qty_today = fields.Float(compute="_compute_qty_at_date")
    qty_available_today = fields.Float(compute="_compute_qty_at_date")
    warehouse_id = fields.Many2one("stock.warehouse", compute="_compute_qty_at_date")
    qty_to_deliver = fields.Float(
        compute="_compute_qty_to_deliver", digits="Product Unit of Measure")
    is_mto = fields.Boolean(compute="_compute_is_mto")
    display_qty_widget = fields.Boolean(compute="_compute_qty_to_deliver")

    def _get_bookmarked_components(self):
        child_dict = {}
        # get all bookmarked sol for product with bom
        domain_sol = [
            ("product_id.bom_ids", "!=", False),
            ("product_id.type", "!=", "service"),
            ("order_id.bookmarked", "=", True),
            ("state", "not in", ("cancel", "sale", "done")),
        ]
        sol_res = {
            item["product_id"][0]: item["product_uom_qty"]
            for item in self.env["sale.order.line"].read_group(
                domain_sol,
                ["product_id", "product_uom_qty"],
                ["product_id"],
                orderby="id",
            )
        }
        for product in self.env["product.product"].browse(sol_res.keys()):
            rounding = product.uom_id.rounding
            # get all products from bom and its children
            child_products = self.env["sale.order"]._bom_explode(product, [])
            for x in child_products:
                if x["product_id"] not in child_dict:
                    child_dict.update(
                        {
                            x["product_id"]: x["qty"]
                            * float_round(
                                sol_res.get(product.id, 0.0),
                                precision_rounding=rounding,
                            )
                        }
                    )
                else:
                    child_dict[x["product_id"]] += x["qty"] * float_round(
                        sol_res.get(product.id, 0.0), precision_rounding=rounding
                    )
        return child_dict

    def _compute_qty_to_deliver(self):
        for component in self:
            component.qty_to_deliver = component.component_bom_qty * (
                component.sol_product_uom_qty - component.sol_qty_delivered
            )
            component.display_qty_widget = (
                component.state == "draft"
                and component.product_type == "product"
                and component.qty_to_deliver > 0
            )

    def _compute_qty_at_date(self):
        """Based on _compute_free_qty method of sale.order.line
        model in Odoo v13 'sale_stock' module.
        """
        bookmarked_component_dict = self._get_bookmarked_components()
        qty_processed_per_product = defaultdict(lambda: 0)
        grouped_lines = defaultdict(lambda: self.env["sale.component.line"])
        now = fields.Datetime.now()
        for line in self:  # .sorted(key=lambda r: r.sequence):
            if not line.display_qty_widget:
                continue
            line.warehouse_id = line.sale_order_line_id.order_id.warehouse_id
            # REMOVE use of commitment_date as scheduled date shown in popup
            # UPD commitment_date has been replaced by date_order
            if line.sale_order_line_id.order_id.state in ["sale", "done"]:
                confirm_date = line.sale_order_line_id.order_id.date_order
            else:
                confirm_date = now
            # add produce_delay to customer_lead (equal to line.product_id.sale_delay)
            date = confirm_date + timedelta(
                days=(
                    (line.product_id.sale_delay or 0.0)
                    + (line.product_id.produce_delay or 0.0)
                    + (line.product_id.purchase_delay or 0.0)
                )
            )
            grouped_lines[(line.warehouse_id.id, date)] |= line
        treated = self.browse()
        for (warehouse, scheduled_date), lines in grouped_lines.items():
            for line in lines:
                to_date = (
                    line.sale_order_line_id.commitment_date
                    or line.sale_order_line_id.scheduled_date
                )
                if line.product_id.sale_delay:
                    to_date = to_date + timedelta(
                        days=-(line.product_id.sale_delay or 0.0)
                    )
                product = line.product_id.with_context(
                    to_date=to_date, warehouse=warehouse
                )
                qty_available = product.qty_available
                free_qty = product.free_qty
                virtual_available = product.virtual_available
                qty_processed = qty_processed_per_product[product.id]
                line.scheduled_date = scheduled_date
                line.qty_available_today = qty_available - qty_processed
                line.free_qty_today = free_qty - qty_processed
                virtual_available_at_date = virtual_available - qty_processed
                missing_component_qty = 0.0
                if virtual_available_at_date < line.qty_to_deliver:
                    if virtual_available_at_date >= 0.0:
                        missing_qty = line.qty_to_deliver - virtual_available_at_date
                    else:
                        missing_qty = line.qty_to_deliver
                    missing_component_qty = (
                        bookmarked_component_dict.get(product.id, 0.0) + missing_qty
                    )
                line.component_bookmarked_qty = missing_component_qty
                line.virtual_available_at_date = (
                    virtual_available_at_date - missing_component_qty
                )
                qty_processed_per_product[product.id] += (
                    line.component_bom_qty * line.sol_product_uom_qty
                )
            treated |= lines
        remaining = self - treated
        remaining.write(
            {
                "virtual_available_at_date": False,
                "scheduled_date": False,
                "free_qty_today": False,
                "qty_available_today": False,
                "warehouse_id": False,
            }
        )

    def _compute_is_mto(self):
        """Based on _compute_is_mto method of
        sale.order.line model in sale_stock Odoo module.
        """
        for line in self:
            line.is_mto = False
            if not line.display_qty_widget:
                continue
            product = line.product_id
            product_routes = line.sale_order_line_id.route_id
            if not product_routes:
                product_routes = product.route_ids + product.categ_id.total_route_ids
            # Check MTO
            mto_route = (
                line.sale_order_line_id.order_id.warehouse_id.mto_pull_id.route_id
            )
            if not mto_route:
                try:
                    warehouse_obj = self.env["stock.warehouse"]
                    mto_route = warehouse_obj._find_global_route(
                        "stock.route_warehouse0_mto", _("Make To Order")
                    )
                except UserError:
                    # if route MTO not found in ir_model_data,
                    # we treat the product as in MTS
                    pass
            line.is_mto = mto_route and mto_route in product_routes
