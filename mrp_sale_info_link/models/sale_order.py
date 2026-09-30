from odoo import _, fields, models
from odoo.osv import expression


class SaleOrder(models.Model):
    _inherit = "sale.order"

    mrp_production_ids = fields.Many2many(
        search="_search_mrp_production_ids",
    )

    def _search_mrp_production_ids(self, operator, value):
        """Search the same three links used by the standard field's compute."""
        if operator == "=?":
            if not value:
                return []
            operator = "="
        if operator in ("any", "not any"):
            value = self.env["mrp.production"]._search(value)
            operator = "in" if operator == "any" else "not in"
        if operator not in (
            "=",
            "!=",
            "in",
            "not in",
            "like",
            "not like",
            "ilike",
            "not ilike",
            "=like",
            "=ilike",
        ):
            raise ValueError(
                _("Unsupported operator for mrp_production_ids: %(op)s", op=operator)
            )

        # Negate the union of matching sales, rather than each individual link:
        # a sale can have both a matching production and other productions.
        negate = operator in expression.NEGATIVE_TERM_OPERATORS
        if negate:
            operator = expression.TERM_OPERATORS_NEGATION[operator]
        if value is False:
            operator = "!="
            negate = not negate
        elif isinstance(value, (list | tuple | set)):
            # Stored one2many links do not discard empty IDs as many2many does.
            value = [production_id for production_id in value if production_id]

        procurement_groups = self.env["procurement.group"].search(
            [
                ("sale_id", "!=", False),
                "|",
                ("mrp_production_ids", operator, value),
                (
                    "stock_move_ids.created_production_id.procurement_group_id."
                    "mrp_production_ids",
                    operator,
                    value,
                ),
            ]
        )
        sale_lines = self.env["sale.order.line"].search(
            [
                ("mrp_production_ids", operator, value),
            ]
        )
        sales = procurement_groups.sale_id | sale_lines.order_id
        return [("id", "not in" if negate else "in", sales.ids)]
