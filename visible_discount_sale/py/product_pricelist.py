from openerp import models, fields, api


class product_pricelist(models.Model):
    _inherit = 'product.pricelist'
    
    visible_discount = fields.Boolean( 'Visible Discount ?',
                        help='''By setting this option, Discount and Base price will be separated on Sale Order line so you can see actual discount applied on Pricelist.''' )

    
