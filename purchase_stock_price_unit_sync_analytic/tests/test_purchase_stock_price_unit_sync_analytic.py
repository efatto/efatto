# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
# Copyright 2023 Sergio Corato <https://github.com/sergiocorato>
from odoo.addons.mrp_production_demo.tests.common_data import TestProductionData
from odoo.tools import mute_logger
from odoo import fields
from odoo.tools.date_utils import relativedelta


class PurchaseStockPriceUnitSyncAnalytic(TestProductionData):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env.ref('base.res_partner_2')
        buy = cls.env.ref('purchase_stock.route_warehouse0_buy')
        cls.vendor = cls.env.ref('base.res_partner_3')
        supplierinfo = cls.env['product.supplierinfo'].create({
            'name': cls.vendor.id,
        })
        cls.product = cls.env['product.product'].create({
            'name': 'Product Test',
            'type': 'product',
            'standard_price': 50.0,
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
    def test_01_invoice_update_purchase_with_standard_cost_method(self):
        self.assertEqual(self.product.categ_id.property_cost_method, 'standard')
        self.assertNotIn(self.partner, self.product.seller_ids.mapped('name'))
        purchase_order1 = self.env['purchase.order'].create({
            'partner_id': self.partner.id,
        })
        purchase_planned_date1 = fields.Datetime.now() + relativedelta(days=5)
        purchase_line = self._create_purchase_order_line(
            purchase_order1, self.product, 18, purchase_planned_date1)
        purchase_line.account_analytic_id = self.analytic_account
        purchase_order1.button_confirm()
        current_price = purchase_line.price_unit

        # create sale order with self.product and check price_unit of stock move
        # is equal to current price of product
        sale_order = self.env['sale.order'].sudo(self.sale_user).create({
            'partner_id': self.partner.id,
            'analytic_account_id': self.analytic_account.id,
        })
        self._create_sale_order_line(sale_order, self.product, 3)
        sale_order.sudo(self.sale_user).action_confirm()
        self.assertEqual(sale_order.state, 'sale')
        sale_picking = sale_order.picking_ids[0]
        for move_line in sale_picking.move_lines:
            move_line.write({'quantity_done': move_line.product_uom_qty})
        sale_picking.button_validate()
        self.assertEqual(sale_picking.state, 'done')
        self.assertEqual(sale_picking.move_lines[0].price_unit,
                         -self.product.standard_price)
        self.assertEqual(purchase_line.product_uom_qty, 18)
        self.assertEqual(purchase_order1.state, 'purchase')

        picking = purchase_order1.picking_ids[0]
        self._action_pack_operation_auto_fill(picking)
        picking.button_validate()
        self.assertEqual(picking.state, 'done')

        invoice = self.env['account.invoice'].with_context(
            type='in_invoice',
        ).create({
            'partner_id': self.partner.id,
            'purchase_id': purchase_order1.id,
            'account_id': self.partner.property_account_payable_id.id,
        })
        invoice.purchase_order_change()
        # self.check_values(self.po_line, 0, 5, 0, 5, 'invoiced')

        self.assertTrue(invoice)
        invoice_line = invoice.invoice_line_ids
        self.assertEqual(invoice_line.product_id, self.product)

        supplierinfo = self.product.seller_ids.filtered(
            lambda x: x.name == self.partner
        )
        self.assertEqual(purchase_line.price_unit, current_price)
        self.assertEqual(supplierinfo.price, current_price)
        self.assertEqual(picking.move_lines[0].price_unit,
                         self.product.standard_price
                         if self.product.categ_id.property_cost_method == 'standard'
                         else current_price)
        self.assertEqual(self.product.standard_price, self.product.standard_price if
                         self.product.categ_id.property_cost_method == 'standard'
                         else current_price)

        new_price = invoice_line.price_unit + 66
        invoice_line.price_unit = new_price
        purchase_line.write({
            'price_unit': new_price,
        })
        self.assertEqual(purchase_line.price_unit, new_price)
        self.assertEqual(picking.move_lines[0].price_unit, new_price)
        self.assertEqual(self.product.standard_price, self.product.standard_price if
                         self.product.categ_id.property_cost_method == 'standard'
                         else new_price)
        # check sale order stock move price_unit is equal to new_price
        self.assertEqual(sale_picking.move_lines[0].price_unit, -new_price)

    @mute_logger(
        'odoo.models', 'odoo.models.unlink', 'odoo.addons.base.ir.ir_model'
    )
    def test_02_invoice_update_purchase_mo_with_standard_cost_method(self):
        self.assertEqual(self.product.categ_id.property_cost_method, 'standard')
        self.assertNotIn(self.partner, self.product.seller_ids.mapped('name'))
        # create a
        purchase_order1 = self.env['purchase.order'].create({
            'partner_id': self.partner.id,
        })
        purchase_planned_date1 = fields.Datetime.now() + relativedelta(days=5)
        purchase_line = self._create_purchase_order_line(
            purchase_order1, self.subproduct_1_1, 18, purchase_planned_date1)
        purchase_line.account_analytic_id = self.analytic_account
        purchase_order1.button_confirm()
        current_price = purchase_line.price_unit

        # create sale order with self.product and check price_unit of stock move
        # is equal to current price of product
        sale_order = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'analytic_account_id': self.analytic_account.id,
        })
        self._create_sale_order_line(sale_order, self.top_product, 3)
        sale_order.action_confirm()
        self.assertEqual(sale_order.state, 'sale')
        self.production = self.env['mrp.production'].search(
            [('origin', '=', sale_order.name)])
        self.assertTrue(self.production)

        # sale_picking = sale_order.picking_ids[0]
        # for move_line in sale_picking.move_lines:
        #     move_line.write({'quantity_done': move_line.product_uom_qty})
        # sale_picking.button_validate()
        # self.assertEqual(sale_picking.state, 'done')
        # self.assertEqual(sale_picking.move_lines[0].price_unit,
        # -self.product.standard_price)
        # self.assertEqual(purchase_line.product_uom_qty, 18)
        # self.assertEqual(purchase_order1.state, 'purchase')

        picking = purchase_order1.picking_ids[0]
        self._action_pack_operation_auto_fill(picking)
        picking.button_validate()
        self.assertEqual(picking.state, 'done')

        invoice = self.env['account.invoice'].with_context(
            type='in_invoice',
        ).create({
            'partner_id': self.partner.id,
            'purchase_id': purchase_order1.id,
            'account_id': self.partner.property_account_payable_id.id,
        })
        invoice.purchase_order_change()

        self.assertTrue(invoice)
        invoice_line = invoice.invoice_line_ids
        self.assertEqual(invoice_line.product_id, self.subproduct_1_1)

        supplierinfo = self.product.seller_ids.filtered(
            lambda x: x.name == self.partner
        )
        self.assertEqual(purchase_line.price_unit, current_price)
        self.assertEqual(supplierinfo.price, current_price)
        self.assertEqual(picking.move_lines[0].price_unit,
                         self.product.standard_price
                         if self.product.categ_id.property_cost_method == 'standard'
                         else current_price)
        self.assertEqual(self.product.standard_price, self.product.standard_price if
                         self.product.categ_id.property_cost_method == 'standard'
                         else current_price)

        new_price = invoice_line.price_unit + 66
        invoice_line.price_unit = new_price
        purchase_line.write({
            'price_unit': new_price,
        })
        self.assertEqual(purchase_line.price_unit, new_price)
        self.assertEqual(picking.move_lines[0].price_unit, new_price)
        self.assertEqual(self.product.standard_price, self.product.standard_price if
                         self.product.categ_id.property_cost_method == 'standard'
                         else new_price)
        # check sale order stock move price_unit is equal to new_price
        # self.assertEqual(sale_picking.move_lines[0].price_unit, -new_price)
        raw_move = self.production.move_raw_ids.filtered(
            lambda x: x.product_id == self.subproduct_1_1)
        self.assertAlmostEqual(
            raw_move.price_unit, new_price
        )
