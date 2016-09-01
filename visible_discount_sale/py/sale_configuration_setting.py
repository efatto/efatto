from openerp import models, fields, api
from openerp.exceptions import except_orm

class sale_config_settings(models.TransientModel):
    _inherit = 'sale.config.settings'
    
    group_visible_discount = fields.Boolean('Visible Discount in Sale Order', 
                        implied_group='sale.group_sale_visible_discount',                                     
                        help = 'You can allow user to visible discount in sale order line.')

    @api.onchange( 'group_visible_discount', 'group_sale_pricelist', 'group_discount_per_so_line' )
    def onchange_visible_discount( self ):
        if self.group_visible_discount:
            if not self.group_sale_pricelist:
                self.group_visible_discount = False
                raise except_orm( ( 'Unable to proceed' ), ( 'Either first activate \"Use pricelists to adapt your price per customers\" or Deactivate \"Visible Discount in Sale Order\". !!!' ) )

            if not self.group_discount_per_so_line:
                self.group_visible_discount = False
                raise except_orm( ( 'Unable to proceed' ), ( 'Either first activate \"Allow setting a discount on the sales order lines\" or Deactivate \"Visible Discount in Sale Order\". !!!' ) )
