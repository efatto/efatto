# Copyright 2020 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.sale_timesheet.tests.common import TestCommonSaleTimesheetNoChart
import time


class TestSaleDeliveredPercent(TestCommonSaleTimesheetNoChart):
    @classmethod
    def setUpClass(cls):
        super(TestSaleDeliveredPercent, cls).setUpClass()
        cls.product_model = cls.env['product.product']
        cls.analytic_line_model = cls.env['account.analytic.line']
        cls.employee_user = cls.env['hr.employee'].create({
            'name': 'Employee User',
            'timesheet_cost': 15,
        })
        cls.product_on_timesheet_ordered = cls.product_model.create({
            'name': 'Product on timesheet ordered',
            'service_policy': 'ordered_timesheet',
            'service_tracking': 'project_only',
            'type': 'service',
            'uom_id': cls.env.ref('uom.product_uom_unit').id,
            'uom_po_id': cls.env.ref('uom.product_uom_unit').id,
            'list_price': 50.0,
            'taxes_id': [(6, 0, cls.env['account.tax'].search(
                [('type_tax_use', '=', 'sale')], limit=1).ids)]
        })
        cls.product_on_timesheet_delivered = cls.product_model.create({
            'name': 'Product on timesheet delivered',
            'service_policy': 'delivered_timesheet',
            'service_tracking': 'project_only',
            'type': 'service',
            'uom_id': cls.env.ref('uom.product_uom_unit').id,
            'uom_po_id': cls.env.ref('uom.product_uom_unit').id,
            'list_price': 50.0,
            'taxes_id': [(6, 0, cls.env['account.tax'].search(
                [('type_tax_use', '=', 'sale')], limit=1).ids)]
        })
        cls.product_on_task_ordered = cls.product_model.create({
            'name': 'Product on task ordered',
            'service_policy': 'ordered_timesheet',
            'service_tracking': 'task_new_project',
            'type': 'service',
            'uom_id': cls.env.ref('uom.product_uom_unit').id,
            'uom_po_id': cls.env.ref('uom.product_uom_unit').id,
            'list_price': 50.0,
            'taxes_id': [(6, 0, cls.env['account.tax'].search(
                [('type_tax_use', '=', 'sale')], limit=1).ids)]
        })
        cls.product_on_task_delivered = cls.product_model.create({
            'name': 'Product on task delivered',
            'service_policy': 'delivered_timesheet',
            'service_tracking': 'task_new_project',
            'type': 'service',
            'uom_id': cls.env.ref('uom.product_uom_unit').id,
            'uom_po_id': cls.env.ref('uom.product_uom_unit').id,
            'list_price': 50.0,
            'taxes_id': [(6, 0, cls.env['account.tax'].search(
                [('type_tax_use', '=', 'sale')], limit=1).ids)]
        })
        cls.product_on_order = cls.product_model.create({
            'name': 'Product manual on n. on order',
            'service_policy': 'delivered_manual',
            'service_tracking': 'task_new_project',
            'type': 'service',
            'uom_id': cls.env.ref('uom.product_uom_unit').id,
            'uom_po_id': cls.env.ref('uom.product_uom_unit').id,
            'list_price': 50.0,
            'taxes_id': [(6, 0, cls.env['account.tax'].search(
                [('type_tax_use', '=', 'sale')], limit=1).ids)]
        })

    def _create_timesheet(self, project, amount, task=False):
        return self.env['account.analytic.line'].create({
            'name': 'Test Line',
            'project_id': project.id,
            'task_id': task.id if task else False,
            'unit_amount': amount,
            'employee_id': self.employee_user.id,
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
        analytic = self.env['account.analytic.account'].search([
            ('name', '=', sale_order.name)
        ])
        self.assertEqual(len(analytic), 1, msg="Contract was not created")

        project = self.env['project.project'].search([
            ('name', '=', sale_order.name)
        ])
        self.assertEqual(len(project), 1, msg="Project was not created")
        self.assertEqual(len(project.task_ids), 0,
                         msg="Task for timesheet track was created")
        # create tasks and set planned_hours
        task1 = self.env['project.task'].create({
            'name': 'test task',
            'project_id': project.id,
            'planned_hours': 50,
        })
        task2 = self.env['project.task'].create({
            'name': 'test task',
            'project_id': project.id,
            'planned_hours': 150,
        })
        # create some ts worked lines
        self._create_timesheet(project, 4, task1)
        self._create_timesheet(project, 12, task2)
        # check if qty_delivered is correct percent value
        self.assertAlmostEqual(project.sale_line_id.qty_delivered, 16/200.0)
        # check if tasks are not duplicated when order is set to draft and re-confirmed
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
        self.assertEqual(len(project.task_ids), 3,
                         msg="Task from task type sale order line was not created")
