# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
# Copyright 2023 Sergio Corato <https://github.com/sergiocorato>
from odoo.tests import SavepointCase, Form
from odoo.tools import mute_logger
from odoo import fields
from odoo.tools.date_utils import relativedelta


class AccountStockPriceUnitSyncAnalytic(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.user_model = cls.env['res.users'].with_context(no_reset_password=True)
        cls.Product = cls.env['product.product']
        cls.partner = cls.env.ref('base.res_partner_2')
        buy = cls.env.ref('purchase_stock.route_warehouse0_buy')
        expenses = cls.env.ref('account.data_account_type_expenses').id
        cls.invoice_line_account_id = cls.env['account.account'].search(
            [('user_type_id', '=', expenses)], limit=1).id
        cls.vendor = cls.env.ref('base.res_partner_3')
        supplierinfo = cls.env['product.supplierinfo'].create({
            'name': cls.vendor.id,
        })
        cls.product1 = cls.Product.create({
            'name': 'Product Test 1',
            'type': 'product',
            'standard_price': 50.0,
            'seller_ids': [(6, 0, [supplierinfo.id])],
            'route_ids': [(6, 0, [buy.id])],
        })
        cls.product2 = cls.Product.create({
            'name': 'Product Test 2',
            'type': 'product',
            'standard_price': 40.0,
            'seller_ids': [(6, 0, [supplierinfo.id])],
            'route_ids': [(6, 0, [buy.id])],
        })
        cls.sale_user = cls.env['res.users'].create({
            'name': 'John',
            'login': 'test',
        })
        cls.sale_user.write({
            'groups_id': [(4, cls.env.ref('sales_team.group_sale_salesman').id)],
        })
        cls.analytic_account = cls.env['account.analytic.account'].create({
            'name': 'Sale analytic account test',
        })
        cls.subproduct_1_1 = cls.Product.create([{
            'name': 'Subproduct 1.1',
            'type': 'product',
        }])
        cls.subproduct_1_2 = cls.Product.create([{
            'name': 'Subproduct 1.2',
            'type': 'product',
        }])
        cls.top_product = cls.Product.create([{
            'name': 'Top Product',
            'type': 'product',
            'route_ids': [
                (6, 0, [cls.env.ref('stock.route_warehouse0_mto').id,
                        cls.env.ref('mrp.route_warehouse0_manufacture').id]),
            ],
        }])
        cls.main_bom = cls.env['mrp.bom'].create([{
            'product_tmpl_id': cls.top_product.product_tmpl_id.id,
            'bom_line_ids': [
                (0, 0, {'product_id': cls.subproduct_1_1.id, 'product_qty': 5}),
                (0, 0, {'product_id': cls.subproduct_1_2.id, 'product_qty': 3}),
            ]
        }])

    def _create_purchase_order_line(self, order, product, qty, date_planned=False):
        vals = {
            'name': product.name,
            'order_id': order.id,
            'product_id': product.id,
            'product_uom': product.uom_po_id.id,
            'product_qty': qty,
            'price_unit': 100,
            }
        if date_planned:
            vals.update({
                'date_planned': date_planned
            })
        line = self.env['purchase.order.line'].create(vals)
        line._onchange_quantity()
        line._convert_to_write(line._cache)
        return line

    def _create_sale_order_line(self, order, product, qty):
        vals = {
            'order_id': order.id,
            'product_id': product.id,
            'product_uom_qty': qty,
            'price_unit': product.list_price,
            }
        line = self.env['sale.order.line'].create(vals)
        line.product_id_change()
        line.product_uom_change()
        line._onchange_discount()
        line._convert_to_write(line._cache)
        return line

    @staticmethod
    def _action_pack_operation_auto_fill(picking):
        for op in picking.mapped('move_line_ids'):
            if op.product_id.type == 'product':
                op.qty_done = op.move_id.product_uom_qty

    @mute_logger(
        'odoo.models', 'odoo.models.unlink', 'odoo.addons.base.ir.ir_model'
    )
    def test_01_invoice_update_purchase(self):
        self.assertEqual(self.product1.categ_id.property_cost_method, 'standard')
        self.assertNotIn(self.partner, self.product1.seller_ids.mapped('name'))
        purchase_order1 = self.env['purchase.order'].create({
            'partner_id': self.partner.id,
        })
        purchase_planned_date1 = fields.Datetime.now() + relativedelta(days=5)
        purchase_line1 = self._create_purchase_order_line(
            purchase_order1, self.product1, 18, purchase_planned_date1)
        purchase_line1.account_analytic_id = self.analytic_account
        purchase_order1.button_confirm()
        # create another purchse order without analytic account
        purchase_order2 = self.env['purchase.order'].create({
            'partner_id': self.partner.id,
        })
        self._create_purchase_order_line(
            purchase_order2, self.product2, 4, purchase_planned_date1)
        purchase_order2.button_confirm()
        # receive products
        purchase_picking1 = purchase_order1.picking_ids[0]
        self._action_pack_operation_auto_fill(purchase_picking1)
        purchase_picking1.button_validate()
        self.assertEqual(purchase_picking1.state, 'done')
        purchase_picking2 = purchase_order2.picking_ids[0]
        self._action_pack_operation_auto_fill(purchase_picking2)
        purchase_picking2.button_validate()
        self.assertEqual(purchase_picking2.state, 'done')

        # create sale order with self.product1 and check price_unit of stock move
        # is equal to current price of product
        sale_order1 = self.env['sale.order'].sudo(self.sale_user).create({
            'partner_id': self.partner.id,
            'analytic_account_id': self.analytic_account.id,
        })
        self._create_sale_order_line(sale_order1, self.product1, 3)
        sale_order1.with_context(test_mrp_production_procurement_analytic=True
                                 ).sudo(self.sale_user).action_confirm()
        self.assertEqual(sale_order1.state, 'sale')
        sale_picking1 = sale_order1.picking_ids[0]
        for move_line in sale_picking1.move_lines:
            move_line.write({'quantity_done': move_line.product_uom_qty})
        sale_picking1.button_validate()

        sale_order2 = self.env['sale.order'].sudo(self.sale_user).create({
            'partner_id': self.partner.id,
            'analytic_account_id': self.analytic_account.id,
        })
        self._create_sale_order_line(sale_order2, self.product2, 2)
        sale_order2.with_context(test_mrp_production_procurement_analytic=True
                                 ).sudo(self.sale_user).action_confirm()
        self.assertEqual(sale_order2.state, 'sale')
        sale_picking2 = sale_order2.picking_ids[0]
        for move_line in sale_picking2.move_lines:
            move_line.write({'quantity_done': move_line.product_uom_qty})
        sale_picking2.button_validate()
        self.assertEqual(sale_picking2.state, 'done')
        self.assertEqual(sale_picking2.move_lines.filtered(
            lambda x: x.product_id == self.product2
        ).price_unit, -self.product2.standard_price)

        self.assertEqual(purchase_line1.product_uom_qty, 18)
        self.assertEqual(purchase_order1.state, 'purchase')

        # change purchase line price, will do nothing
        new_price1 = purchase_line1.price_unit + 22
        purchase_line1.price_unit = new_price1
        # create invoice for purchase order 1
        invoice1 = self.env['account.invoice'].with_context(
            type='in_invoice',
        ).create({
            'partner_id': self.partner.id,
            'purchase_id': purchase_order1.id,
            'account_id': self.partner.property_account_payable_id.id,
        })
        # this function is called by onchange on purchase_id
        invoice1.purchase_order_change()
        # check a new price in invoice line update price in sale picking move
        invoice_line1 = invoice1.invoice_line_ids
        self.assertEqual(invoice_line1.product_id, self.product1)
        self.assertEqual(invoice_line1.account_analytic_id, self.analytic_account)
        new_price2 = invoice_line1.price_unit + 66
        invoice_line1.price_unit = new_price2
        invoice1.action_invoice_open()
        self.assertEqual(invoice1.state, 'open')
        self.assertEqual(sale_picking1.move_lines.filtered(
            lambda x: x.product_id == self.product1
        ).price_unit, -new_price2)

        # create invoice for purchase order 2
        invoice2 = self.env['account.invoice'].with_context(
            type='in_invoice',
        ).create({
            'partner_id': self.partner.id,
            'purchase_id': purchase_order2.id,
            'account_id': self.partner.property_account_payable_id.id,
        })
        # this function is called by onchange on purchase_id
        invoice2.purchase_order_change()
        # check a new price in invoice line update price in sale picking move
        invoice_line2 = invoice2.invoice_line_ids
        self.assertEqual(invoice_line2.product_id, self.product2)
        self.assertFalse(invoice_line2.account_analytic_id)
        new_price3 = invoice_line2.price_unit + 66
        invoice_line2.price_unit = new_price3
        invoice2.action_invoice_open()
        self.assertEqual(invoice2.state, 'open')
        self.assertEqual(sale_picking2.move_lines.filtered(
            lambda x: x.product_id == self.product2
        ).price_unit, -new_price3)

        # add another manually created invoice to test avg price unit
        last_price = new_price2 + 77
        last_invoice = self.env['account.invoice'].create([{
            'partner_id': self.partner.id,
            'type': 'in_invoice',
            'account_id': self.partner.property_account_payable_id.id,
            'invoice_line_ids': [
                (0, 0, {
                    'name': 'test',
                    'product_id': self.product1.id,
                    'uom_id': self.product1.uom_id.id,
                    'quantity': 10.0,
                    'price_unit': last_price,
                    'account_id': self.invoice_line_account_id,
                    'account_analytic_id': self.analytic_account.id,
                })
            ]
        }])
        last_invoice_line = last_invoice.invoice_line_ids[0]
        self.assertEqual(last_invoice_line.account_analytic_id, self.analytic_account)
        self.assertAlmostEqual(last_invoice_line.price_unit, last_price)
        avg_price = (
            last_price * last_invoice_line.quantity
            + new_price2 * invoice_line1.quantity
        ) / (
            last_invoice_line.quantity + invoice_line1.quantity
        )
        # check last price in invoice line update price in sale picking move
        invoice1.action_invoice_open()
        self.assertEqual(invoice1.state, 'open')
        self.assertEqual(sale_picking1.move_lines.filtered(
            lambda x: x.product_id == self.product1
        ).price_unit, - avg_price)

    @mute_logger(
        'odoo.models', 'odoo.models.unlink', 'odoo.addons.base.ir.ir_model'
    )
    def test_02_invoice_update_purchase_mo(self):
        self.assertEqual(self.product1.categ_id.property_cost_method, 'standard')
        self.assertNotIn(self.partner, self.product1.seller_ids.mapped('name'))
        purchase_order1 = self.env['purchase.order'].create({
            'partner_id': self.partner.id,
        })
        purchase_planned_date1 = fields.Datetime.now() + relativedelta(days=5)
        purchase_line = self._create_purchase_order_line(
            purchase_order1, self.subproduct_1_1, 18, purchase_planned_date1)
        purchase_line.account_analytic_id = self.analytic_account
        purchase_order1.button_confirm()

        # create sale order with self.product1 and check price_unit of stock move
        # is equal to current price of product
        sale_order = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'analytic_account_id': self.analytic_account.id,
        })
        self._create_sale_order_line(sale_order, self.top_product, 3)
        sale_order.with_context(test_mrp_production_procurement_analytic=True
                                ).action_confirm()
        self.assertEqual(sale_order.state, 'sale')
        self.production = self.env['mrp.production'].search(
            [('origin', '=', sale_order.name)])
        self.assertTrue(self.production)
        self.assertTrue(self.production.analytic_account_id)
        # transfer and validate purchase picking
        purchase_picking = purchase_order1.picking_ids[0]
        self._action_pack_operation_auto_fill(purchase_picking)
        purchase_picking.button_validate()
        self.assertEqual(purchase_picking.state, 'done')

        invoice = self.env['account.invoice'].with_context(
            type='in_invoice',
        ).create({
            'partner_id': self.partner.id,
            'purchase_id': purchase_order1.id,
            'account_id': self.partner.property_account_payable_id.id,
        })
        # this function is called by onchange on purchase_id
        invoice.purchase_order_change()
        # check a new price in invoice line update price in sale picking move
        invoice_line = invoice.invoice_line_ids
        self.assertEqual(invoice_line.product_id, self.subproduct_1_1)
        new_price = invoice_line.price_unit + 30
        invoice_line.price_unit = new_price
        invoice.action_invoice_open()
        self.assertEqual(invoice.state, 'open')
        raw_moves = self.production.move_raw_ids.filtered(
            lambda x: x.product_id == self.subproduct_1_1)
        for raw_move in raw_moves:
            self.assertAlmostEqual(
                raw_move.price_unit, -new_price
            )

        # do production
        self.production.action_assign()
        self.production.button_plan()

        produce_form = Form(
            self.env['mrp.product.produce'].with_context(
                active_id=self.production.id,
                active_ids=[self.production.id],
            )
        )
        produce_form.product_qty = self.production.product_qty
        wizard = produce_form.save()
        wizard.do_produce()
        self.production.button_mark_done()
        self.assertEqual(self.production.state, 'done')

        # add another manually created invoice to test avg price unit
        last_price = new_price - 19
        last_invoice = self.env['account.invoice'].create([{
            'partner_id': self.partner.id,
            'type': 'in_invoice',
            'account_id': self.partner.property_account_payable_id.id,
            'invoice_line_ids': [
                (0, 0, {
                    'name': 'test',
                    'product_id': self.subproduct_1_1.id,
                    'uom_id': self.subproduct_1_1.uom_id.id,
                    'quantity': 12.0,
                    'price_unit': last_price,
                    'account_id': self.invoice_line_account_id,
                    'account_analytic_id': self.analytic_account.id,
                })
            ]
        }])
        last_invoice_line = last_invoice.invoice_line_ids[0]
        self.assertEqual(last_invoice_line.account_analytic_id, self.analytic_account)
        self.assertAlmostEqual(last_invoice_line.price_unit, last_price)
        avg_price = (
            last_price * last_invoice_line.quantity
            + new_price * invoice_line.quantity
        ) / (
            last_invoice_line.quantity + invoice_line.quantity
        )
        # check last price in invoice line update price in mo raw move
        invoice.action_invoice_open()
        self.assertEqual(invoice.state, 'open')
        for raw_move in raw_moves:
            self.assertAlmostEqual(
                raw_move.price_unit, - avg_price
            )
