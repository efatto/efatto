# Copyright 2020-2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models, fields, api
from odoo.exceptions import AccessError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def _add_supplier_to_product(self):
        super()._add_supplier_to_product()
        # Changes of _add_supplier_to_product function marked with ###
        # Add the partner in the supplier list of the product if the supplier is not
        # registered for
        # this product. We limit to 10 the number of suppliers for a product to avoid
        # the mess that
        # could be caused for some generic products ("Miscellaneous").
        # ### esclude 0 prices
        for line in self.order_line.filtered(lambda x: x.price_unit != 0.0):
            # Do not add a contact as a supplier
            partner = self.partner_id if not self.partner_id.parent_id \
                else self.partner_id.parent_id
            if len(line.product_id.seller_ids) <= 20:
                # Convert the price in the right currency.
                currency = partner.property_purchase_currency_id \
                           or self.env.user.company_id.currency_id
                price = self.currency_id._convert(
                    line.price_unit, currency, line.company_id,
                    line.date_order or fields.Date.today(), round=False)
                # Compute the price for the template's UoM, because the supplier's
                # UoM is related to that UoM.
                if line.product_id.product_tmpl_id.uom_po_id != line.product_uom:
                    default_uom = line.product_id.product_tmpl_id.uom_po_id
                    price = line.product_uom._compute_price(price, default_uom)

                supplierinfo = {
                    'name': partner.id,
                    'sequence': max(line.product_id.seller_ids.mapped('sequence')) + 1
                    if line.product_id.seller_ids else 1,
                    'min_qty': 0.0,
                    'price': price,
                    'currency_id': currency.id,
                    'delay': 0,
                    'discount': line.discount,  ### add discount
                }
                if hasattr(line, 'discount2'):
                    supplierinfo.update({
                        'discount2': line.discount2,
                        'discount3': line.discount3,
                    })
                # In case the order partner is a contact address, a new supplierinfo
                # is created on
                # the parent company. In this case, we keep the product name and code.
                seller = line.product_id._select_seller(
                    partner_id=line.partner_id,
                    quantity=line.product_qty,
                    date=line.order_id.date_order and line.order_id.date_order.date(),
                    uom_id=line.product_uom)
                if seller:
                    supplierinfo['product_name'] = seller.product_name
                    supplierinfo['product_code'] = seller.product_code
                vals = {
                    'seller_ids': [(0, 0, supplierinfo)],
                }
                try:
                    if partner in line.product_id.seller_ids.mapped('name'):
                        seller = line.product_id.seller_ids.filtered(
                            lambda x: x.name == partner)
                        for key in ['name', 'sequence', 'min_qty', 'delay']:
                            supplierinfo.pop(key)
                        seller.write(supplierinfo)
                    else:
                        line.product_id.write(vals)
                except AccessError:  # no write access rights -> just ignore
                    break

    @api.multi
    def button_approve(self, force=False):
        # update supplierinfo when order is approved from vendor, before purchase state
        res = super().button_approve()
        for order in self:
            order._add_supplier_to_product()
        return res
