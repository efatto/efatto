from odoo import api, models


class SupplierInfo(models.Model):
    _inherit = "product.supplierinfo"

    @api.depends(
        "partner_id",
        "product_id",
        "product_tmpl_id",
        "product_id.variant_bom_ids.type",
        "product_id.variant_bom_ids.subcontractor_ids",
        "product_tmpl_id.bom_ids.type",
        "product_tmpl_id.bom_ids.subcontractor_ids",
    )
    def _compute_is_subcontractor(self):
        # Only add BOM-related dependencies; keep the standard v18 logic
        # (which filters template BOMs by product variant).
        return super()._compute_is_subcontractor()
