# Copyright 2020-2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from datetime import timedelta
from odoo import models, fields, api
from odoo.exceptions import AccessError


class SupplierInfo(models.Model):
    _inherit = "product.supplierinfo"

    purchase_order_id = fields.Many2one(
        comodel_name='purchase.order',
        string='Purchase Order',
        help='Purchase order generator of this line, if exists.'
    )


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def _approved_order_add_supplier_to_product(self):
        # _add_supplier_to_product is called later so it will found already this
        # partner and won't do something
        for line in self.order_line.filtered(
            lambda x: x.price_unit != 0.0
        ):
            partner = self.partner_id if not self.partner_id.parent_id else\
                self.partner_id.parent_id
            # Convert the price in the right currency.
            currency = partner.property_purchase_currency_id\
                or self.env.user.company_id.currency_id
            price = self.currency_id._convert(
                line.price_unit, currency, line.company_id,
                line.date_order or fields.Date.today(), round=False)
            # Compute the price for the template's UoM, because the supplier's UoM is
            # related to that UoM.
            if line.product_id.product_tmpl_id.uom_po_id != line.product_uom:
                default_uom = line.product_id.product_tmpl_id.uom_po_id
                price = line.product_uom._compute_price(price, default_uom)

            supplierinfo = {
                'name': partner.id,
                'sequence': max(line.product_id.seller_ids.mapped(
                    'sequence')) + 1 if line.product_id.seller_ids else 1,
                'min_qty': 0.0,
                'price': price,
                'currency_id': currency.id,
                'delay': 0,
                'discount': line.discount,
                'date_start': fields.Date.today(),
                'date_end': False,
                'purchase_order_id': line.order_id.id,
            }
            updated = False
            # MAINTAIN all seller lines with min_qty
            # get sellers with min_qty > 1 and with different price and discount
            # from current line: FIXME if there is a seller with same price-discount it
            #                     will be ignored!!!
            # - if not found do nothing*
            # - if found:
            #   - if line qty >= min_qty, update or duplicate this line, then continue
            #   - else, do nothing*
            # it will be created a seller without min_qty finally
            min_qty_sellers = line.product_id.seller_ids.filtered(
                lambda x: x.name == partner and x.min_qty > 1 and (
                    x.price != price or x.discount != line.discount
                ))
            for min_qty_seller in min_qty_sellers:
                # todo if there are more sellers with same min_qty, maintains only one
                #  foreach, instead maintains all
                if line.quantity >= min_qty_seller.min_qty:
                    # todo update or duplicate this line to save current price
                    continue
            # get sellers without min_qty and with different price and discount
            # from current line:
            # - if not found create a seller
            # - if found update or duplicate this line
            sellers = line.product_id.seller_ids.filtered(
                lambda x: x.name == partner and x.min_qty in [0, 1] and (
                    x.price != price or x.discount != line.discount
                ))
            for seller in sellers:
                if seller.price != price \
                        or seller.discount != line.discount:
                    # Set invalid all other supplierinfo line for this supplier
                    # todo excluding those with min_qty > 1 if this order is < min_qty
                    seller.date_end = fields.Date.today() - timedelta(days=1)
                    supplierinfo.update({
                        'delay': seller.delay,
                        'min_qty': seller.min_qty,
                        'product_name': seller.product_name,
                        'product_code': seller.product_code,
                    })
                else:
                    # reuse this record as equal
                    pass
                vals = {
                    'seller_ids': [(0, 0, supplierinfo)],
                }
                if seller.purchase_order_id == self:
                    try:
                        line.product_id.write(vals)
                        updated = True
                    except AccessError:  # no write access rights -> just ignore
                        break
            if not updated:
                # supplierinfo_obj.create(vals)
                pass

    @api.multi
    def button_approve(self, force=False):
        # update supplierinfo when order is approved from vendor, before purchase state
        res = super().button_approve()
        for order in self:
            order._approved_order_add_supplier_to_product()
        return res
