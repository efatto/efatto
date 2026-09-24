from odoo import models
from odoo.osv.expression import AND, OR


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    def _bom_find_domain(
        self, products, picking_type=None, company_id=False, bom_type=False
    ):
        """
        Get inactive phantom bom if an inactive product with phantom bom is in
        the current bom.
        Else it will duplicate the product requested and delivered.
        """
        inactive_products = products.filtered(lambda p: not p.active)
        if inactive_products:
            products = products - inactive_products
            domain = [
                "&",
                "|",
                ("product_id", "in", inactive_products.ids),
                "&",
                ("product_id", "=", False),
                ("product_tmpl_id", "in", inactive_products.product_tmpl_id.ids),
                ("active", "=", False),
            ]
            if products:
                domain = OR(
                    [
                        domain,
                        [
                            "&",
                            "|",
                            ("product_id", "in", products.ids),
                            "&",
                            ("product_id", "=", False),
                            ("product_tmpl_id", "in", products.product_tmpl_id.ids),
                            ("active", "=", True),
                        ],
                    ]
                )
            if company_id or self.env.context.get("company_id"):
                domain = AND(
                    [
                        domain,
                        [
                            "|",
                            ("company_id", "=", False),
                            (
                                "company_id",
                                "=",
                                company_id or self.env.context.get("company_id"),
                            ),
                        ],
                    ]
                )
            if picking_type:
                domain = AND(
                    [
                        domain,
                        [
                            "|",
                            ("picking_type_id", "=", picking_type.id),
                            ("picking_type_id", "=", False),
                        ],
                    ]
                )
            if bom_type:
                domain = AND([domain, [("type", "=", bom_type)]])
            return domain
        return super()._bom_find_domain(products, picking_type, company_id, bom_type)
