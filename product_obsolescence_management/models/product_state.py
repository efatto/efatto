from odoo import fields, models


class ProductState(models.Model):
    _inherit = "product.state"

    is_end_of_life = fields.Boolean(
        help="If the product is put in this state, it will be marked as obsolete."
    )
