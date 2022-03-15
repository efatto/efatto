# Copyright 2018 Tecnativa - Pedro M. Baeza
# Copyright 2022 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import Form, common


def _execute_onchanges(records, field_name):
    """Helper methods that executes all onchanges associated to a field."""
    for onchange in records._onchange_methods.get(field_name, []):
        for record in records:
            onchange(record)


class TestDeliveryAutoRefreshProgressive(common.HttpCase):
    def setUp(self):
        super(TestDeliveryAutoRefreshProgressive, self).setUp()
        service = self.env['product.product'].create({
            'name': 'Service Test',
            'type': 'service',
        })
        self.carrier = self.env['delivery.carrier'].create({
            'name': 'Test carrier',
            'delivery_type': 'base_on_rule',
            'product_id': service.id,
            'price_rule_ids': [
                (0, 0, {
                    'variable': 'weight',
                    'operator': '<=',
                    'max_value': 20,
                    'list_base_price': 50,
                }),
                (0, 0, {
                    'variable': 'weight',
                    'operator': '<=',
                    'max_value': 40,
                    'list_base_price': 30,
                    'list_price': 1,
                    'variable_factor': 'weight',
                }),
                (0, 0, {
                    'variable': 'weight',
                    'operator': '>',
                    'max_value': 40,
                    'list_base_price': 20,
                    'list_price': 1.5,
                    'variable_factor': 'weight',
                }),
            ]
        })
        self.product = self.env['product.product'].create({
            'name': 'Test product',
            'weight': 10,
            'list_price': 20,
        })
        self.partner = self.env['res.partner'].create({
            'name': 'Test partner',
            'property_delivery_carrier_id': self.carrier.id,
        })
        self.param_name1 = 'delivery_auto_refresh.auto_add_delivery_line'
        self.param_name2 = 'delivery_auto_refresh.refresh_after_picking'
        self.param_name3 = 'delivery_auto_refresh.auto_void_delivery_line'
        order_obj = self.env['sale.order']
        order_vals = order_obj.default_get(order_obj._fields.keys())
        order_vals.update({
            'partner_id': self.partner.id,
            'partner_shipping_id': self.partner.id,
            'order_line': [
                (0, 0, {
                    'product_id': self.product.id,
                    'product_uom_qty': 20,
                })
            ]
        })
        order = order_obj.new(order_vals)
        _execute_onchanges(order, 'partner_shipping_id')
        _execute_onchanges(order.order_line, 'product_id')
        self.order = order.create(order._convert_to_write(order._cache))

    def test_auto_refresh_so(self):
        self.assertFalse(self.order.order_line.filtered('is_delivery'))
        self.env['ir.config_parameter'].sudo().set_param(self.param_name1, 1)
        self.order.write({
            'order_line': [
                (1, self.order.order_line.id, {'product_uom_qty': 30}),
            ],
        })
        line_delivery = self.order.order_line.filtered('is_delivery')
        self.assertEqual(line_delivery.price_unit, 0)
        line2 = self.order.order_line.new({
            'order_id': self.order.id,
            'product_id': self.product.id,
            'product_uom_qty': 2,
        })
        _execute_onchanges(line2, 'product_id')
        vals = line2._convert_to_write(line2._cache)
        del vals['order_id']
        self.order.write({'order_line': [(0, 0, vals)]})
        line_delivery = self.order.order_line.filtered('is_delivery')
        self.assertEqual(line_delivery.price_unit, 0)

    def test_auto_refresh_picking_with_backorder(self):
        self.env['ir.config_parameter'].sudo().set_param(self.param_name2, 1)
        self.env['ir.config_parameter'].sudo().set_param(self.param_name1, 1)
        self.order.order_line.product_uom_qty = 30
        self.order.action_confirm()
        picking = self.order.picking_ids
        picking.action_assign()
        picking.move_line_ids[0].qty_done = 2
        backorder_wiz_id = picking.button_validate()['res_id']
        backorder_wiz = self.env['stock.backorder.confirmation'].browse(
            backorder_wiz_id)
        backorder_wiz.process()
        line_delivery = self.order.order_line.filtered('is_delivery')
        self.assertEqual(line_delivery.price_unit, 50)
        picking1 = self.order.picking_ids - picking
        picking1.action_assign()
        picking1.move_line_ids[0].qty_done = 8
        backorder_wiz_id1 = picking1.button_validate()['res_id']
        backorder_wiz1 = self.env['stock.backorder.confirmation'].browse(
            backorder_wiz_id1)
        backorder_wiz1.process()
        line_delivery = self.order.order_line.filtered('is_delivery')
        self.assertEqual(line_delivery.price_unit, 50 + 140)

    def test_auto_refresh_picking_with_backorder_and_invoice(self):
        self.env['ir.config_parameter'].sudo().set_param(self.param_name2, 1)
        self.env['ir.config_parameter'].sudo().set_param(self.param_name1, 1)
        self.order.order_line.product_uom_qty = 30
        self.order.action_confirm()
        picking = self.order.picking_ids
        picking.action_assign()
        picking.move_line_ids[0].qty_done = 2
        backorder_wiz_id = picking.button_validate()['res_id']
        backorder_wiz = self.env['stock.backorder.confirmation'].browse(
            backorder_wiz_id)
        backorder_wiz.process()
        line_delivery = self.order.order_line.filtered('is_delivery')
        self.assertEqual(line_delivery.price_unit, 50)
        picking1 = self.order.picking_ids - picking
        picking1.action_assign()
        picking1.move_line_ids[0].qty_done = 8
        backorder_wiz_id1 = picking1.button_validate()['res_id']
        backorder_wiz1 = self.env['stock.backorder.confirmation'].browse(
            backorder_wiz_id1)
        backorder_wiz1.process()
        line_delivery = self.order.order_line.filtered('is_delivery')
        self.assertEqual(line_delivery.price_unit, 50 + 140)
        inv_id = self.order.action_invoice_create()
        invoice = self.env['account.invoice'].browse(inv_id)
        self.assertAlmostEqual(invoice.invoice_line_ids.filtered(
            lambda x: x.product_id == self.carrier.product_id
        )[0].price_subtotal, 50 + 140)
        picking2 = self.order.picking_ids - (picking + picking1)
        picking2.action_assign()
        picking2.move_line_ids[0].qty_done = 4
        backorder_wiz_id2 = picking2.button_validate()['res_id']
        backorder_wiz2 = self.env['stock.backorder.confirmation'].browse(
            backorder_wiz_id2)
        backorder_wiz2.process()
        line_delivery = self.order.order_line.filtered(
            lambda x: x.is_delivery and not x.qty_invoiced)
        self.assertEqual(line_delivery.price_unit, 70)
        picking3 = self.order.picking_ids - (picking + picking1 + picking2)
        picking3.action_assign()
        picking3.move_line_ids[0].qty_done = 6
        backorder_wiz_id3 = picking3.button_validate()['res_id']
        backorder_wiz3 = self.env['stock.backorder.confirmation'].browse(
            backorder_wiz_id3)
        backorder_wiz3.process()
        line_delivery = self.order.order_line.filtered(
            lambda x: x.is_delivery and not x.qty_invoiced)
        self.assertEqual(line_delivery.price_unit, 70 + 110)

    def test_no_auto_refresh_picking(self):
        self.env['ir.config_parameter'].sudo().set_param(self.param_name2, "0")
        self.order.order_line.product_uom_qty = 3
        self.order.action_confirm()
        picking = self.order.picking_ids
        picking.action_assign()
        picking.move_line_ids[0].qty_done = 2
        picking.action_done()
        line_delivery = self.order.order_line.filtered('is_delivery')
        self.assertEqual(line_delivery.price_unit, 0)

    def _confirm_sale_order(self, order):
        sale_form = Form(order)
        # Force the delivery line creation
        with sale_form.order_line.edit(0) as line_form:
            line_form.product_uom_qty = 2
        sale_form.save()
        line_delivery = order.order_line.filtered("is_delivery")
        order.action_confirm()
        return line_delivery

    def _validate_picking(self, picking):
        """Helper method to confirm the pickings"""
        for line in picking.move_lines:
            line.quantity_done = line.product_uom_qty
        picking.action_done()

    def _return_whole_picking(self, picking, to_refund=True):
        """Helper method to create a return of the original picking. It could
        be refundable or not"""
        return_wiz = self.env["stock.return.picking"].with_context(
            active_ids=picking.ids, active_id=picking.ids[0]
        ).create({})
        return_wiz.product_return_moves.quantity = (
            picking.move_lines.quantity_done
        )
        return_wiz.product_return_moves.to_refund = to_refund
        res = return_wiz.create_returns()
        return_picking = self.env["stock.picking"].browse(res["res_id"])
        self._validate_picking(return_picking)

    def _test_autorefresh_void_line(
            self, lock=False, to_refund=True, invoice=False):
        """Helper method to test the possible cases for voiding the line"""
        self.assertFalse(self.order.order_line.filtered("is_delivery"))
        self.env["ir.config_parameter"].sudo().set_param(self.param_name1, 1)
        self.env["ir.config_parameter"].sudo().set_param(self.param_name3, 1)
        line_delivery = self._confirm_sale_order(self.order)
        self._validate_picking(self.order.picking_ids)
        if invoice:
            self.order.action_invoice_create()
        if lock:
            self.order.action_done()
        self._return_whole_picking(self.order.picking_ids, to_refund)
        return line_delivery

    def test_auto_refresh_so_and_return_no_invoiced(self):
        """The delivery line is voided as all conditions apply when the return
        is made"""
        line_delivery = self._test_autorefresh_void_line()
        self.assertEqual(line_delivery.price_unit, 0)
        self.assertEqual(line_delivery.product_uom_qty, 0)

    def test_auto_refresh_so_and_return_no_invoiced_locked(self):
        """The delivery line is voided as all conditions apply when the return
        is made. We overrided the locked state in this case"""
        line_delivery = self._test_autorefresh_void_line(lock=True)
        self.assertEqual(line_delivery.price_unit, 0)
        self.assertEqual(line_delivery.product_uom_qty, 0)

    def test_auto_refresh_so_and_return_invoiced(self):
        """There's already an invoice, so the delivery line can't be voided
        >> no price will be set on delivery line until delivery"""
        line_delivery = self._test_autorefresh_void_line(invoice=True)
        self.assertEqual(line_delivery.price_unit, 0)
        self.assertEqual(line_delivery.product_uom_qty, 1)

    def test_auto_refresh_so_and_return_no_refund(self):
        """The return wasn't flagged to refund, so the delivered qty won't
        change, thus the delivery line shouldn't be either >> no price will be set
        on delivery line until delivery"""
        line_delivery = self._test_autorefresh_void_line(to_refund=False)
        self.assertEqual(line_delivery.price_unit, 0)
        self.assertEqual(line_delivery.product_uom_qty, 1)
