# Copyright 2020 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestSaleOrderCalendarState(TransactionCase):

    def _create_sale_order_line(self, order, product, qty):
        line = self.env['sale.order.line'].create({
            'order_id': order.id,
            'product_id': product.id,
            'product_uom_qty': qty,
            'price_unit': 100,
            })
        line.product_id_change()
        line._convert_to_write(line._cache)
        return line

    def setUp(self):
        super(TestSaleOrderCalendarState, self).setUp()
        self.partner = self.env.ref('base.res_partner_2')
        # Acoustic Bloc Screens, 16 on hand
        self.product1 = self.env.ref('product.product_product_25')
        # Cabinet with Doors, 8 on hand
        self.product2 = self.env.ref('product.product_product_10')
        # Large Cabinet, 250 on hand
        self.product3 = self.env.ref('product.product_product_6')
        # Drawer Black, 0 on hand
        self.product4 = self.env.ref('product.product_product_16')
        self.product1.invoice_policy = 'order'
        self.product2.invoice_policy = 'order'

    def test_complete_picking_from_sale(self):
        order1 = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            })
        self._create_sale_order_line(order1, self.product1, 5)
        order1.action_confirm()
        self.assertEqual(order1.state, 'sale')
        self.assertEqual(order1.calendar_state, 'to_pack')
        picking = order1.picking_ids[0]
        picking.action_assign()
        for sml in picking.move_lines.mapped('move_line_ids'):
            sml.qty_done = sml.product_qty
        picking.action_done()
        self.assertEqual(picking.state, 'done')
        self.assertEqual(order1.calendar_state, 'delivery_done')
        # create invoice
        inv_id = order1.action_invoice_create()
        self.assertEqual(order1.calendar_state, 'invoiced')
        invoice = self.env['account.invoice'].browse(inv_id)
        invoice.carrier_tracking_ref = 'TRACKING - 5555'
        self.assertEqual(order1.calendar_state, 'shipped')
