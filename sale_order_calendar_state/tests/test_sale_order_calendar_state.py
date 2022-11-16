from odoo.addons.mrp_production_demo.tests.common_data import TestProductionData
from odoo.tests import Form
from odoo import fields
from datetime import timedelta


class TestSaleOrderCalendarState(TestProductionData):

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

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env.ref('base.res_partner_2')
        # Acoustic Bloc Screens, 16 on hand
        cls.product1 = cls.env.ref('product.product_product_25')
        # Cabinet with Doors, 8 on hand
        cls.product2 = cls.env.ref('product.product_product_10')
        # Large Cabinet, 250 on hand
        cls.product3 = cls.env.ref('product.product_product_6')
        # Drawer Black, 0 on hand
        cls.product4 = cls.env.ref('product.product_product_16')
        cls.product1.invoice_policy = 'order'
        cls.product2.invoice_policy = 'order'

    def test_01_sale(self):
        order1 = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            })
        self._create_sale_order_line(order1, self.product1, 5)
        order1.action_confirm()
        self.assertEqual(order1.state, 'sale')
        self.assertEqual(order1.calendar_state, 'to_process')
        picking = order1.picking_ids[0]
        picking.action_assign()
        self.assertEqual(order1.calendar_state, 'to_process')
        self.assertEqual(picking.state, 'waiting')
        picking.button_assign()
        self.assertEqual(order1.calendar_state, 'to_pack')
        self.assertEqual(picking.state, 'assigned')

        blocked_form = Form(
            self.env['wizard.mark.blocked'].with_context(
                active_id=order1.id,
                active_ids=order1.ids,
                active_model=order1._name,
            )
        )
        blocked_form.note = 'Blocked note text'
        wizard = blocked_form.save()
        wizard.mark_blocked()
        self.assertEqual(order1.calendar_state, 'blocked')
        # TODO possible improvement: block picking validation if so is blocked?
        order1.button_mark_not_blocked()
        self.assertFalse(order1.additional_state)
        self.assertEqual(order1.calendar_state, 'to_pack')

        for sml in picking.move_lines.mapped('move_line_ids'):
            sml.qty_done = sml.product_qty
        for whs_list in picking.move_lines.mapped('whs_list_ids'):
            whs_list.write({
                'stato': '4',
                'qtamov': whs_list.qta,
            })
        picking.action_done()
        self.assertEqual(picking.state, 'done')
        self.assertEqual(order1.calendar_state, 'delivery_done')
        # create invoice
        inv_id = order1.action_invoice_create()
        self.assertEqual(order1.calendar_state, 'invoiced')
        # REMOVED on request
        # invoice = self.env['account.invoice'].browse(inv_id)
        # invoice.carrier_tracking_ref = 'TRACKING - 5555'
        # self.assertEqual(order1.calendar_state, 'shipped')

    def test_02_mrp_from_sale(self):
        sale_order = self.env['sale.order'].create({
            'partner_id': self.env.ref('base.res_partner_12').id,
            'date_order': fields.Date.today(),
            'picking_policy': 'direct',
            'expected_date': fields.Date.today() + timedelta(days=20),
            'order_line': [
                (0, 0, {
                    'product_id': self.top_product.id,
                    'product_uom_qty': 20,
                    'product_uom': self.top_product.uom_po_id.id,
                    'price_unit': self.top_product.list_price,
                    'name': self.top_product.name,
                }),
            ]
        })
        sale_order.action_confirm()
        self.assertEqual(sale_order.calendar_state, 'to_produce')
        man_order = self.env['mrp.production'].search([
            ('origin', 'ilike', sale_order.name)
        ])
        self.assertTrue(man_order)
        man_order.action_assign()
        self.assertEqual(man_order.state, 'confirmed')

        blocked_form = Form(
            self.env['wizard.mark.blocked'].with_context(
                active_id=man_order.id,
                active_ids=man_order.ids,
                active_model=man_order._name,
            )
        )
        blocked_form.note = 'Blocked note text'
        wizard = blocked_form.save()
        wizard.mark_blocked()
        self.assertEqual(sale_order.calendar_state, 'blocked')
        # TODO possible improvement: block manufacture produce if so is blocked?
        man_order.button_mark_not_blocked()
        self.assertFalse(sale_order.additional_state)
        self.assertEqual(sale_order.calendar_state, 'to_produce')
