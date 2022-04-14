# Copyright 2022 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime
from odoo.tests import common


class TestStockRulePartner(common.TransactionCase):

    def test_00_dropship_vendor(self):
        vendor = self.env['res.partner'].create(dict(name="vendor"))
        product = self.env['product.product'].create(dict(
            name='Product to return',
            categ_id=self.env.ref('product.product_category_1').id,
        ))
        vendor_location = self.env['stock.location'].create(dict(
            name="Conto lavoro fornitori",
            location_id=self.env.ref('stock.stock_location_locations_partner').id,
            usage='customer',
        ))
        picking_type_to_vendor = self.env['stock.picking.type'].create(dict(
            name="Consegna a fornitori in c/lavoro",
            code='incoming',
            warehouse_id=self.env.ref('stock.warehouse0').id,
            sequence=10,
            sequence_id=self.env.ref('stock_dropshipping.seq_picking_type_dropship').id,
            default_location_src_id=self.env.ref('stock.stock_location_stock').id,
            default_location_dest_id=vendor_location.id,
        ))
        picking_type_from_vendor = self.env['stock.picking.type'].create(dict(
            name="Rientro da fornitori in c/lavoro",
            code='incoming',
            warehouse_id=self.env.ref('stock.warehouse0').id,
            sequence=10,
            sequence_id=self.env.ref('stock_dropshipping.seq_picking_type_dropship').id,
            return_picking_type_id=picking_type_to_vendor.id,
            default_location_src_id=vendor_location.id,
            default_location_dest_id=self.env.ref('stock.stock_location_stock').id,
        ))
        picking_type_to_vendor.return_picking_type_id = picking_type_from_vendor
        # Create routing to send and receive from vendor in dropshipping
        routing_to_vendor = self.env['stock.location.route'].create(dict(
            name="Consegna a c/lavoro fornitori",
            sequence=10,
            warehouse_selectable=True,
            product_selectable=True,
            product_categ_selectable=False,
            warehouse_ids=[(6, 0, self.env.ref('stock.warehouse0').ids)],
            rule_ids=[(0, 0, dict(
                name="sposta da stock a c/lavoro fornitori",
                action='pull',
                warehouse_id=self.env.ref('stock.warehouse0').id,
                propagate_partner=True,
                propagate=True,
                location_src_id=self.env.ref('stock.stock_location_stock').id,
                location_id=vendor_location.id,
                picking_type_id=picking_type_to_vendor.id,
            ))]
        ))
        routing_from_vendor = self.env['stock.location.route'].create(dict(
            name="Rientro da c/lavoro fornitori",
            sequence=10,
            warehouse_selectable=True,
            product_selectable=True,
            product_categ_selectable=False,
            warehouse_ids=[(6, 0, self.env.ref('stock.warehouse0').ids)],
            rule_ids=[(0, 0, dict(
                name="sposta da c/lavoro fornitori a stock",
                action='push',
                warehouse_id=self.env.ref('stock.warehouse0').id,
                propagate_partner=True,
                propagate=True,
                location_src_id=vendor_location.id,
                location_id=self.env.ref('stock.stock_location_stock').id,
                picking_type_id=picking_type_from_vendor.id,
            ))]
        ))

        purchase = self.env['purchase.order'].create(dict(
            partner_id=vendor.id,
            picking_type_id=picking_type_to_vendor.id,
            dest_address_id=vendor.id,
            order_line=[(0, 0, dict(
                name=product.name,
                product_id=product.id,
                product_qty=1.0,
                product_uom=product.uom_id.id,
                price_unit=10,
                date_planned=datetime.now(),
            ))]
        ))
        purchase.button_confirm()
        self.assertEqual(purchase.state, 'purchase',
                         'Purchase order is not in \'purchase\' state!')
        # Send the products
        purchase.picking_ids.move_lines.quantity_done = \
            purchase.picking_ids.move_lines.product_qty
        purchase.picking_ids.button_validate()

        return_picking_from_vendor = self.env['stock.picking'].search([
            ('origin', '=', purchase.name),
            ('picking_type_id', '=', picking_type_from_vendor.id),
        ])
        self.assertEqual(len(return_picking_from_vendor), 1)
        self.assertEqual(return_picking_from_vendor.move_lines[0].product_id, product)
