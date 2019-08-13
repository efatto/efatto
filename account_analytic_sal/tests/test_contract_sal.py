# -*- coding: utf-8 -*-

from odoo.addons.contract.tests.test_contract import TestContractBase
import time


class AccountAnalyticAccount(TestContractBase):
    @classmethod
    def setUpClass(cls):
        super(AccountAnalyticAccount, cls).setUpClass()
        # todo: check hours amount are correctly computed from sale order and
        #  sale order line on contract, at creation and modification
        cls.product_model = cls.env['product.product']
        cls.product_on_timesheet_ordered = cls.product_model.create({
            'name': 'Product on timesheet ordered',
            'track_service': 'timesheet',
            'invoice_policy': 'order',
            'type': 'service',
            'uom_id': cls.env.ref('product.product_uom_hour').id,
            'uom_po_id': cls.env.ref('product.product_uom_hour').id,
            'list_price': 50.0,
            'taxes_id': [(6, 0, cls.env['account.tax'].search(
                [('type_tax_use', '=', 'sale')], limit=1).ids)]
        })
        # product_uom_day
        cls.product_on_timesheet_delivered = cls.product_model.create({
            'name': 'Product on timesheet delivered',
            'track_service': 'timesheet',
            'invoice_policy': 'delivery',
            'type': 'service',
            'uom_id': cls.env.ref('product.product_uom_hour').id,
            'uom_po_id': cls.env.ref('product.product_uom_hour').id,
            'list_price': 50.0,
            'taxes_id': [(6, 0, cls.env['account.tax'].search(
                [('type_tax_use', '=', 'sale')], limit=1).ids)]
        })
        cls.product_on_task_ordered = cls.product_model.create({
            'name': 'Product on task ordered',
            'track_service': 'task',
            'invoice_policy': 'order',
            'type': 'service',
            'uom_id': cls.env.ref('product.product_uom_hour').id,
            'uom_po_id': cls.env.ref('product.product_uom_hour').id,
            'list_price': 50.0,
            'taxes_id': [(6, 0, cls.env['account.tax'].search(
                [('type_tax_use', '=', 'sale')], limit=1).ids)]
        })
        cls.product_on_task_delivered = cls.product_model.create({
            'name': 'Product on task delivered',
            'track_service': 'task',
            'invoice_policy': 'delivery',
            'type': 'service',
            'uom_id': cls.env.ref('product.product_uom_hour').id,
            'uom_po_id': cls.env.ref('product.product_uom_hour').id,
            'list_price': 50.0,
            'taxes_id': [(6, 0, cls.env['account.tax'].search(
                [('type_tax_use', '=', 'sale')], limit=1).ids)]
        })
        cls.product_on_order = cls.product_model.create({
            'name': 'Product manual on n. on order',
            'track_service': 'manual',
            'invoice_policy': 'order',
            'type': 'service',
            'uom_id': cls.env.ref('product.product_uom_unit').id,
            'uom_po_id': cls.env.ref('product.product_uom_unit').id,
            'list_price': 50.0,
            'taxes_id': [(6, 0, cls.env['account.tax'].search(
                [('type_tax_use', '=', 'sale')], limit=1).ids)]
        })

    def test_sale_order_1_on_timesheet_ordered(self):
        sale_order = self.env['sale.order'].create({
            'partner_id': self.env.ref('base.res_partner_3').id,
            'date_order': time.strftime('%Y-%m-%d'),
            'order_line': [
                (0, 0, {
                    'product_id': self.product_on_timesheet_ordered.id,
                    'product_uom_qty': 5,
                    'product_uom': self.product_on_timesheet_ordered.uom_id.id,
                    'price_unit': self.product_on_timesheet_ordered.list_price,
                    'name': 'Development on ts ordered',
                }),
            ]
        })
        self.assertEqual(len(sale_order.order_line), 1,
                         msg="Order line was not created")
        sale_order.action_confirm()
        contract = self.env['account.analytic.account'].search([
            ('name', '=', sale_order.name)
        ])
        self.assertEqual(len(contract), 1, msg="Contract was not created")
        self.assertAlmostEqual(
            contract.qty_ordered, 5.0,
            msg="Qty ordered is different from sale")
        project = self.env['project.project'].search([
            ('name', '=', sale_order.name)
        ])
        self.assertEqual(len(project), 1, msg="Project was not created")
        self.assertEqual(len(project.task_ids), 0,
                         msg="Task for timesheet track was created")
        # todo create some ts worked lines
        # todo create invoice and check if invoiced is equal ordered
        sale_order.action_cancel()
        sale_order.action_draft()
        sale_order.write({
            'order_line': [(0, 0, {
                'product_id': self.product_on_task_ordered.id,
                'product_uom_qty': 5,
                'product_uom': self.product_on_task_ordered.uom_id.id,
                'price_unit': self.product_on_task_ordered.list_price,
                'name': 'Development on ts delivered',
            })]
        })
        sale_order.action_confirm()
        self.assertEqual(len(sale_order.order_line), 2,
                         msg="Sale order line was not created")
        self.assertEqual(len(project.task_ids), 1,
                         msg="Task from task type sale order line was not"
                             " created")
        self.assertAlmostEqual(
            contract.qty_ordered, 10.0,
            msg="Qty ordered is different from sale")
