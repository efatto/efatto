# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
# Copyright 2023 Sergio Corato <https://github.com/sergiocorato>
from odoo.tests import SavepointCase, Form
from odoo.tools import mute_logger


class AccountAnalyticMrpExtraCost(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.User = cls.env['res.users'].with_context(no_reset_password=True)
        cls.Product = cls.env['product.product']
        cls.partner = cls.env.ref('base.res_partner_2')
        user_type_expense = cls.env.ref('account.data_account_type_expenses').id
        cls.invoice_line_account = cls.env['account.account'].search(
            [('user_type_id', '=', user_type_expense)], limit=1)
        cls.invoice_line_account_1 = cls.env['account.account'].create({
            'code': 'EXP_ACCOUNT',
            'name': 'Expense account',
            'user_type_id': user_type_expense,
        })
        cls.analytic_account = cls.env['account.analytic.account'].create({
            'name': 'Analytic account test',
        })
        cls.subproduct_1_1 = cls.Product.create([{
            'name': 'Subproduct 1.1',
            'type': 'product',
            'standard_price': 10.0,
        }])
        cls.subproduct_1_2 = cls.Product.create([{
            'name': 'Subproduct 1.2',
            'type': 'product',
            'standard_price': 15.0,
        }])
        cls.subproduct_1_3 = cls.Product.create([{
            'name': 'Subproduct 1.3',
            'type': 'product',
            'standard_price': 220.0,
        }])
        cls.subproduct_1_4 = cls.Product.create([{
            'name': 'Subproduct 1.4',
            'type': 'product',
            'standard_price': 777.0,
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
                (0, 0, {'product_id': cls.subproduct_1_4.id, 'product_qty': 7}),
            ]
        }])
        cls.account_journal_purchase = cls.env['account.journal'].search([
            ('type', '=', 'purchase'),
        ])

    @mute_logger(
        'odoo.models', 'odoo.models.unlink', 'odoo.addons.base.ir.ir_model'
    )
    def test_01_invoice_complete_production(self):
        self.production = self.env['mrp.production'].create({
            'name': 'MO-Test',
            'product_id': self.top_product.id,
            'product_uom_id': self.top_product.uom_id.id,
            'product_qty': 2,
            'bom_id': self.main_bom.id,
            'analytic_account_id': self.analytic_account.id,
        })
        self.assertTrue(self.production)
        self.assertTrue(self.production.analytic_account_id)
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

        # create invoice
        new_price_subproduct_1_1 = 25.0
        new_price_subproduct_1_2 = 8.0
        subproduct_1_1_invoice_qty = 12.0  # 10 in MO, purchase 24 pc, 12 with analytic
        subproduct_1_2_invoice_qty = 5.0  # 6 in MO
        subproduct_1_3_invoice_qty = 7.0  # not in MO, there are 14 subproduct 1_4
        invoice_form = Form(self.env['account.invoice'])
        invoice_form.partner_id = self.partner
        invoice_form.type = 'in_invoice'
        invoice_form.account_id = self.partner.property_account_payable_id
        invoice_form.journal_id = self.account_journal_purchase
        with invoice_form.invoice_line_ids.new() as line_form:
            line_form.name = 'test'
            line_form.product_id = self.subproduct_1_1
            line_form.uom_id = self.subproduct_1_1.uom_id
            line_form.quantity = subproduct_1_1_invoice_qty
            line_form.price_unit = new_price_subproduct_1_1
            line_form.account_id = self.invoice_line_account
            line_form.account_analytic_id = self.analytic_account
        with invoice_form.invoice_line_ids.new() as line_form:
            line_form.name = 'test'
            line_form.product_id = self.subproduct_1_1
            line_form.uom_id = self.subproduct_1_1.uom_id
            line_form.quantity = subproduct_1_1_invoice_qty
            line_form.price_unit = new_price_subproduct_1_1 + 9
            line_form.account_id = self.invoice_line_account_1
        with invoice_form.invoice_line_ids.new() as line_form:
            line_form.name = 'test'
            line_form.product_id = self.subproduct_1_2
            line_form.uom_id = self.subproduct_1_2.uom_id
            line_form.quantity = subproduct_1_2_invoice_qty
            line_form.price_unit = new_price_subproduct_1_2
            line_form.account_id = self.invoice_line_account
            line_form.account_analytic_id = self.analytic_account
        with invoice_form.invoice_line_ids.new() as line_form:
            line_form.name = 'test'
            line_form.product_id = self.subproduct_1_3
            line_form.uom_id = self.subproduct_1_3.uom_id
            line_form.quantity = subproduct_1_3_invoice_qty
            line_form.price_unit = self.subproduct_1_3.standard_price
            line_form.account_id = self.invoice_line_account_1
            line_form.account_analytic_id = self.analytic_account
        invoice = invoice_form.save()
        invoice.action_invoice_open()

        analytic_lines = self.env['account.analytic.line'].search([
            ('account_id', '=', self.analytic_account.id),
        ])
        self.assertTrue(analytic_lines)
        self.assertEqual(len(self.production.move_raw_ids), 3)
        # subproduct 1.1 is invoiced for 12 pc, 10 of them used in MO, at price 25, so
        # take the cost of 10 * 25 = 250
        # subproduct 1.2 is invoiced for 5 pc, but MO uses 6 pc, at price 8, so take the
        # cost of 6 * 8 = 48
        # subproduct 1.3 is invoiced but not used in production, but it has the analytic
        # account set, so take the total cost of the line: 7 * self.subproduct_1_3.standard_price
        # subproduct 1.4 is not invoiced, so take the cost of the last purchase with
        # enough quantity to be eligible, if not possible take the last purchase, else
        # take the product standard price (which is the cost)
        actual_cost = 0
        # check subproduct 1_1
        subproduct_1_1_invoice_lines = invoice.invoice_line_ids.filtered(
            lambda x: x.account_analytic_id == self.analytic_account
            and x.product_id == self.subproduct_1_1
        )
        subproduct_1_1_move_raws = self.production.move_raw_ids.filtered(
            lambda x: x.product_id == self.subproduct_1_1
        )
        actual_unit_cost_subproduct_1_1 = (
            sum(x.price_subtotal for x in subproduct_1_1_invoice_lines)
            / sum(x.quantity for x in subproduct_1_1_invoice_lines)
        )
        self.assertAlmostEqual(actual_unit_cost_subproduct_1_1, 25, 2)
        actual_qty_subproduct_1_1 = sum(
            x.quantity_done for x in subproduct_1_1_move_raws)
        actual_cost += (actual_qty_subproduct_1_1 * actual_unit_cost_subproduct_1_1)
        self.assertAlmostEqual(actual_cost, 250, 2)
        # check subproduct 1_2
        subproduct_1_2_invoice_lines = invoice.invoice_line_ids.filtered(
            lambda x: x.account_analytic_id == self.analytic_account
                      and x.product_id == self.subproduct_1_2
        )
        subproduct_1_2_move_raws = self.production.move_raw_ids.filtered(
            lambda x: x.product_id == self.subproduct_1_2
        )
        actual_unit_cost_subproduct_1_2 = (
            sum(x.price_subtotal for x in subproduct_1_2_invoice_lines)
            / sum(x.quantity for x in subproduct_1_2_invoice_lines)
        )
        self.assertAlmostEqual(actual_unit_cost_subproduct_1_2, 8, 2)
        actual_qty_subproduct_1_2 = sum(
            x.quantity_done for x in subproduct_1_2_move_raws)
        actual_cost += (actual_qty_subproduct_1_2 * actual_unit_cost_subproduct_1_2)
        self.assertAlmostEqual(actual_cost, 250 + 48, 2)
        # check subproduct 1_3
        subproduct_1_3_invoice_lines = invoice.invoice_line_ids.filtered(
            lambda x: x.account_analytic_id == self.analytic_account
                      and x.product_id == self.subproduct_1_3
        )
        actual_cost_subproduct_1_3 = (
            sum(x.price_subtotal for x in subproduct_1_3_invoice_lines)
        )
        actual_qty_subproduct_1_3 = sum(
            x.quantity for x in subproduct_1_3_invoice_lines)
        self.assertAlmostEqual(
            actual_cost_subproduct_1_3,
            actual_qty_subproduct_1_3 * self.subproduct_1_3.standard_price, 2)
        actual_cost += actual_cost_subproduct_1_3
        self.assertAlmostEqual(
            actual_cost, 250 + 48 + 1540, 2)
        # TODO get cost of subproduct 1_4, which is not invoiced and don't have an
        #  analytic line
        subproduct_1_4_move_raws = self.production.move_raw_ids.filtered(
            lambda x: x.product_id == self.subproduct_1_4
        )
        actual_qty_subproduct_1_4 = sum(
            x.quantity_done for x in subproduct_1_4_move_raws)
        actual_cost_subproduct_1_4 = (
            actual_qty_subproduct_1_4 * self.subproduct_1_4.standard_price
        )
        # todo this cost is not present in analytic lines, how to show it? use a
        #  dedicated row in mis builder?
        # check value in analytic lines is the same
        self.assertAlmostEqual(
            sum(analytic_lines.mapped("extra_cost")),
            - actual_cost,
            2
        )
