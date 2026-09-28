# Copyright 2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_round

from odoo.addons.stock.models.product import OPERATORS


class ProductProduct(models.Model):
    _inherit = "product.product"

    sale_order_line_ids = fields.One2many(
        "sale.order.line", "product_id", help="Technical: used to compute quantities."
    )
    bookmarked_qty = fields.Float(
        compute="_compute_quantities",
        search="_search_bookmarked_qty",
        digits="Product Unit of Measure",
        help="Quantity of bookmarked outgoing products.\n"
        "In particular contexts, products in a quotation sent are bookmarked for "
        "the customer.\n"
        "This mark is only for informative purposes and do not have any effects.",
    )

    def _search_product_bookmarked_quantity(self, operator, value, field):
        # TDE FIXME: should probably clean the search methods
        # to prevent sql injections
        if field not in ("bookmarked_qty",):
            raise UserError(_("Invalid domain left operand %s") % field)
        if operator not in ("<", ">", "=", "!=", "<=", ">="):
            raise UserError(_("Invalid domain operator %s") % operator)
        if not isinstance(value, (float | int)):
            raise UserError(_("Invalid domain right operand %s") % value)

        # TODO: Still optimization possible when searching virtual quantities
        ids = []
        # Order the search on `id` to prevent the default order on the product name
        # which slows down the search because of the join on the translation table to
        # get the translated names.
        for product in self.with_context(prefetch_fields=False).search([], order="id"):
            if OPERATORS[operator](product[field], value):
                ids.append(product.id)
        return [("id", "in", ids)]

    def _search_bookmarked_qty(self, operator, value):
        # TDE FIXME: should probably clean the search methods
        return self._search_product_bookmarked_quantity(
            operator, value, "bookmarked_qty"
        )

    def _compute_bookmarked_quantities_dict(
        self, lot_id, owner_id, package_id, from_date=False, to_date=False
    ):
        res = super()._compute_quantities_dict(
            lot_id, owner_id, package_id, from_date, to_date
        )
        domain_sol = [
            ("product_id", "in", self.ids),
            ("order_id.bookmarked", "=", True),
            ("state", "not in", ("cancel", "sale")),
        ]
        SaleOrderLine = self.env["sale.order.line"]
        sol_res = {
            item[0]: item[1]
            for item in SaleOrderLine._read_group(
                domain=domain_sol,
                groupby=["product_id"],
                aggregates=["product_uom_qty:sum"],
            )
        }

        for product in self.with_context(prefetch_fields=False):
            res[product.id]["bookmarked_qty"] = float_round(
                sol_res.get(product, 0.0), precision_rounding=product.uom_id.rounding
            )

        return res

    @api.depends(
        "stock_move_ids.product_qty",
        "stock_move_ids.state",
        "sale_order_line_ids.product_uom_qty",
        "sale_order_line_ids.order_id.bookmarked",
    )
    def _compute_quantities(self):
        res = super()._compute_quantities()
        bookmarked_dict = self._compute_bookmarked_quantities_dict(
            self._context.get("lot_id"),
            self._context.get("owner_id"),
            self._context.get("package_id"),
            self._context.get("from_date"),
            self._context.get("to_date"),
        )
        for product in self:
            product.bookmarked_qty = bookmarked_dict[product.id]["bookmarked_qty"]
            product.virtual_available -= bookmarked_dict[product.id]["bookmarked_qty"]

        return res

    def _product_bookmarked_available(self):
        """Compatibility method"""
        return self._compute_bookmarked_quantities_dict(
            self._context.get("lot_id"),
            self._context.get("owner_id"),
            self._context.get("package_id"),
            self._context.get("from_date"),
            self._context.get("to_date"),
        )


class ProductTemplate(models.Model):
    _inherit = "product.template"

    bookmarked_qty = fields.Float(
        "bookmarked",
        compute="_compute_quantities",
        search="_search_bookmarked_qty",
        digits="Product Unit of Measure",
    )

    @api.depends(
        "product_variant_ids",
        "product_variant_ids.stock_move_ids.product_qty",
        "product_variant_ids.stock_move_ids.state",
        "product_variant_ids.sale_order_line_ids.product_uom_qty",
        "product_variant_ids.sale_order_line_ids.order_id.bookmarked",
    )
    def _compute_quantities(self):
        res = super()._compute_quantities()
        bookmarked_dict = self._compute_bookmarked_quantities_dict()
        for template in self:
            template.bookmarked_qty = bookmarked_dict[template.id]["bookmarked_qty"]
            template.virtual_available -= bookmarked_dict[template.id]["bookmarked_qty"]

        return res

    def _compute_bookmarked_quantities_dict(self):
        # TDE FIXME: why not using directly the function fields ?
        variants_available = self.mapped(
            "product_variant_ids"
        )._product_bookmarked_available()
        prod_available = super()._compute_quantities_dict()
        for template in self:
            bookmarked_qty = 0
            for p in template.product_variant_ids:
                bookmarked_qty += variants_available[p.id]["bookmarked_qty"]
            prod_available[template.id] = {
                "bookmarked_qty": bookmarked_qty,
                "virtual_available": template.virtual_available - bookmarked_qty,
            }
        return prod_available

    def _search_bookmarked_qty(self, operator, value):
        domain = [("bookmarked_qty", operator, value)]
        product_variant_ids = self.env["product.product"].search(domain)
        return [("product_variant_ids", "in", product_variant_ids.ids)]
