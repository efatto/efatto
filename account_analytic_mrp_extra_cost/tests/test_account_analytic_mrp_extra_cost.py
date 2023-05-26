# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
# Copyright 2023 Sergio Corato <https://github.com/sergiocorato>
from odoo.tests import SavepointCase, Form
from odoo.tools import mute_logger
from odoo import fields
from odoo.tools.date_utils import relativedelta


class AccountAnalyticMrpExtraCost(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.User = cls.env['res.users'].with_context(no_reset_password=True)
        cls.Product = cls.env['product.product']
        cls.partner = cls.env.ref('base.res_partner_2')
        expenses = cls.env.ref('account.data_account_type_expenses').id
        cls.invoice_line_account_id = cls.env['account.account'].search(
            [('user_type_id', '=', expenses)], limit=1).id
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
        cls.account_journal_purchase.write({
            'group_invoice_lines': True,
            'group_method': 'account',
        })

    @mute_logger(
        'odoo.models', 'odoo.models.unlink', 'odoo.addons.base.ir.ir_model'
    )
    def test_01_invoice_mo(self):
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
        new_price_subproduct_1_1 = self.subproduct_1_1.standard_price + 15.0
        new_price_subproduct_1_2 = self.subproduct_1_2.standard_price - 100.0
        subproduct_1_1_invoice_qty = 12.0
        subproduct_1_2_invoice_qty = 5.0
        subproduct_1_3_invoice_qty = 7.0
        self.assertTrue(self.account_journal_purchase.group_invoice_lines)
        invoice = self.env['account.invoice'].create([{
            'partner_id': self.partner.id,
            'type': 'in_invoice',
            'account_id': self.partner.property_account_payable_id.id,
            'journal_id': self.account_journal_purchase.id,
            'invoice_line_ids': [
                (0, 0, {
                    'name': 'test',
                    'product_id': self.subproduct_1_1.id,
                    'uom_id': self.subproduct_1_1.uom_id.id,
                    'quantity': subproduct_1_1_invoice_qty,
                    'price_unit': new_price_subproduct_1_1,
                    'account_id': self.invoice_line_account_id,
                    'account_analytic_id': self.analytic_account.id,
                }),
                (0, 0, {
                    'name': 'test',
                    'product_id': self.subproduct_1_1.id,
                    'uom_id': self.subproduct_1_1.uom_id.id,
                    'quantity': subproduct_1_1_invoice_qty,
                    'price_unit': new_price_subproduct_1_1,
                    'account_id': self.invoice_line_account_id,
                }),
                (0, 0, {
                    'name': 'test',
                    'product_id': self.subproduct_1_2.id,
                    'uom_id': self.subproduct_1_2.uom_id.id,
                    'quantity': subproduct_1_2_invoice_qty,
                    'price_unit': new_price_subproduct_1_2,
                    'account_id': self.invoice_line_account_id,
                    'account_analytic_id': self.analytic_account.id,
                }),
                (0, 0, {
                    'name': 'test',
                    'product_id': self.subproduct_1_3.id,
                    'uom_id': self.subproduct_1_3.uom_id.id,
                    'quantity': subproduct_1_3_invoice_qty,
                    'price_unit': self.subproduct_1_3.standard_price,
                    'account_id': self.invoice_line_account_id,
                    'account_analytic_id': self.analytic_account.id,
                })
            ]
        }])
        invoice.action_invoice_open()

        analytic_lines = self.env['account.analytic.line'].search([
            ('account_id', '=', self.analytic_account.id),
        ])
        self.assertTrue(analytic_lines)
        self.assertEqual(len(analytic_lines), 1)
        self.assertEqual(len(self.production.move_raw_ids), 3)
        # subproduct 1.1 is invoiced for (10 + 2) * (10 + 15) > compute 300 versus 100 -> + 200
        # subproduct 1.2 is invoiced for (6 - 1) * (price - 100) > not compute
        # subproduct 1.3 is invoiced for (not + 7) * (220) > compute 1540
        # subproduct 1.4 is not invoiced > not in invoice
        extra_cost = 0
        subproduct_1_1_invoice_lines = invoice.invoice_line_ids.filtered(
            lambda x: x.account_analytic_id == self.analytic_account
            and x.product_id == self.subproduct_1_1
        )
        subproduct_1_1_move_raws = self.production.move_raw_ids.filtered(
            lambda x: x.product_id == self.subproduct_1_1
        )
        extra_cost += (
            sum(x.price_subtotal for x in subproduct_1_1_invoice_lines)
            + sum(x.quantity_done * x.price_unit for x in subproduct_1_1_move_raws)
        )
        subproduct_1_3_invoice_lines = invoice.invoice_line_ids.filtered(
            lambda x: x.account_analytic_id == self.analytic_account
            and x.product_id == self.subproduct_1_3
        )
        extra_cost += (
            sum(x.price_subtotal for x in subproduct_1_3_invoice_lines)
        )

        self.assertAlmostEqual(
            analytic_lines.extra_cost,
            extra_cost
        )
