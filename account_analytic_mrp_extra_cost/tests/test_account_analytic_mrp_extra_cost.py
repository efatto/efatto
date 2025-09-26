# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
# Copyright 2023 Sergio Corato <https://github.com/sergiocorato>
from odoo import fields
from odoo.tests import Form, SavepointCase
from odoo.tools import mute_logger, relativedelta


class AccountAnalyticMrpExtraCost(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.User = cls.env["res.users"].with_context(no_reset_password=True)
        cls.Product = cls.env["product.product"]
        cls.partner = cls.env.ref("base.res_partner_2")
        user_type_expense = cls.env.ref("account.data_account_type_expenses").id
        cls.invoice_line_account = cls.env["account.account"].search(
            [("user_type_id", "=", user_type_expense)], limit=1
        )
        cls.invoice_line_account_1 = cls.env["account.account"].create(
            {
                "code": "EXP_ACCOUNT",
                "name": "Expense account",
                "user_type_id": user_type_expense,
            }
        )
        cls.analytic_account = cls.env["account.analytic.account"].create(
            {
                "name": "Analytic account test",
            }
        )
        cls.subproduct_1_1 = cls.Product.create(
            [
                {
                    "name": "Subproduct 1.1",
                    "type": "product",
                    "standard_price": 10.0,
                }
            ]
        )
        cls.subproduct_1_2 = cls.Product.create(
            [
                {
                    "name": "Subproduct 1.2",
                    "type": "product",
                    "standard_price": 15.0,
                }
            ]
        )
        cls.subproduct_1_3 = cls.Product.create(
            [
                {
                    "name": "Subproduct 1.3",
                    "type": "product",
                    "standard_price": 220.0,
                }
            ]
        )
        cls.subproduct_1_4 = cls.Product.create(
            [
                {
                    "name": "Subproduct 1.4",
                    "type": "product",
                    "standard_price": 777.0,
                }
            ]
        )
        cls.top_product = cls.Product.create(
            [
                {
                    "name": "Top Product",
                    "type": "product",
                    "route_ids": [
                        (
                            6,
                            0,
                            [
                                cls.env.ref("stock.route_warehouse0_mto").id,
                                cls.env.ref("mrp.route_warehouse0_manufacture").id,
                            ],
                        ),
                    ],
                }
            ]
        )
        cls.main_bom = cls.env["mrp.bom"].create(
            [
                {
                    "product_tmpl_id": cls.top_product.product_tmpl_id.id,
                    "bom_line_ids": [
                        (0, 0, {"product_id": cls.subproduct_1_1.id, "product_qty": 5}),
                        (0, 0, {"product_id": cls.subproduct_1_2.id, "product_qty": 3}),
                        (0, 0, {"product_id": cls.subproduct_1_4.id, "product_qty": 7}),
                    ],
                }
            ]
        )
        cls.account_journal_purchase = cls.env["account.journal"].search(
            [
                ("type", "=", "purchase"),
            ]
        )

    def _create_production(self, qty):
        production_form = Form(self.env["mrp.production"])
        production_form.product_id = self.top_product
        production_form.product_uom_id = self.top_product.uom_id
        production_form.bom_id = self.main_bom
        production_form.analytic_account_id = self.analytic_account
        self.production = production_form.save()
        self.assertTrue(self.production)
        self.assertTrue(self.production.analytic_account_id)
        self.production.product_qty = qty
        self.production.action_assign()
        self.production.button_plan()
        produce_form = Form(
            self.env["mrp.product.produce"].with_context(
                active_id=self.production.id,
                active_ids=[self.production.id],
            )
        )
        produce_form.product_qty = self.production.product_qty
        wizard = produce_form.save()
        wizard.do_produce()
        self.production.button_mark_done()
        self.assertEqual(self.production.state, "done")
        return self.production

    @mute_logger("odoo.models", "odoo.models.unlink", "odoo.addons.base.ir.ir_model")
    def test_01_invoice_complete_production(self):
        productions = self._create_production(qty=2)
        productions |= self._create_production(qty=3)
        # create invoice
        new_price_subproduct_1_1 = 25.0
        new_price_subproduct_1_2 = 8.0
        subproduct_1_1_invoice_qty = 12.0  # 10 in MO, purchase 24 pc, 12 with analytic
        subproduct_1_2_invoice_qty = 10.0  # 6 in MO, refund for 5
        subproduct_1_3_invoice_qty = 7.0  # not in MO
        # there are also 14 subproduct 1_4
        invoice_form = Form(self.env["account.invoice"])
        invoice_form.partner_id = self.partner
        invoice_form.type = "in_invoice"
        invoice_form.date_invoice = fields.Date.today() + relativedelta(days=-2)
        invoice_form.account_id = self.partner.property_account_payable_id
        invoice_form.journal_id = self.account_journal_purchase
        with invoice_form.invoice_line_ids.new() as line_form:
            line_form.name = "test"
            line_form.product_id = self.subproduct_1_1
            line_form.uom_id = self.subproduct_1_1.uom_id
            line_form.quantity = subproduct_1_1_invoice_qty + 10
            line_form.price_unit = new_price_subproduct_1_1 + 10
            line_form.account_id = self.invoice_line_account
            line_form.account_analytic_id = self.analytic_account
        with invoice_form.invoice_line_ids.new() as line_form:
            line_form.name = "test"
            line_form.product_id = self.subproduct_1_1
            line_form.uom_id = self.subproduct_1_1.uom_id
            line_form.quantity = subproduct_1_1_invoice_qty
            line_form.price_unit = new_price_subproduct_1_1 + 9
            line_form.account_id = self.invoice_line_account_1
        with invoice_form.invoice_line_ids.new() as line_form:
            line_form.name = "test"
            line_form.product_id = self.subproduct_1_2
            line_form.uom_id = self.subproduct_1_2.uom_id
            line_form.quantity = subproduct_1_2_invoice_qty
            line_form.price_unit = new_price_subproduct_1_2
            line_form.account_id = self.invoice_line_account
            line_form.account_analytic_id = self.analytic_account
        with invoice_form.invoice_line_ids.new() as line_form:
            line_form.name = "test"
            line_form.product_id = self.subproduct_1_3
            line_form.uom_id = self.subproduct_1_3.uom_id
            line_form.quantity = subproduct_1_3_invoice_qty
            line_form.price_unit = self.subproduct_1_3.standard_price
            line_form.account_id = self.invoice_line_account_1
            line_form.account_analytic_id = self.analytic_account
        invoice = invoice_form.save()
        invoice.action_invoice_open()
        # create another invoice to check this invoice, as more recent, is used
        invoice_form1 = Form(self.env["account.invoice"])
        invoice_form1.partner_id = self.partner
        invoice_form1.type = "in_invoice"
        invoice_form1.date_invoice = fields.Date.today()
        invoice_form1.account_id = self.partner.property_account_payable_id
        invoice_form1.journal_id = self.account_journal_purchase
        with invoice_form1.invoice_line_ids.new() as line_form:
            line_form.name = "test"
            line_form.product_id = self.subproduct_1_1
            line_form.uom_id = self.subproduct_1_1.uom_id
            line_form.quantity = subproduct_1_1_invoice_qty
            line_form.price_unit = new_price_subproduct_1_1
            line_form.account_id = self.invoice_line_account
            line_form.account_analytic_id = self.analytic_account
        invoice1 = invoice_form1.save()
        invoice1.action_invoice_open()
        # create a refund to check values
        refund_form = Form(self.env["account.invoice"])
        refund_form.partner_id = self.partner
        refund_form.type = "in_refund"
        refund_form.date_invoice = fields.Date.today()
        refund_form.account_id = self.partner.property_account_payable_id
        refund_form.journal_id = self.account_journal_purchase
        with refund_form.invoice_line_ids.new() as line_form:
            line_form.name = "test"
            line_form.product_id = self.subproduct_1_1
            line_form.uom_id = self.subproduct_1_1.uom_id
            line_form.quantity = 4
            line_form.price_unit = new_price_subproduct_1_1 - 5
            line_form.account_id = self.invoice_line_account
            line_form.account_analytic_id = self.analytic_account
        with refund_form.invoice_line_ids.new() as line_form:
            line_form.name = "test"
            line_form.product_id = self.subproduct_1_2
            line_form.uom_id = self.subproduct_1_2.uom_id
            line_form.quantity = 5
            line_form.price_unit = 4
            line_form.account_id = self.invoice_line_account
            line_form.account_analytic_id = self.analytic_account
        refund = refund_form.save()
        refund.action_invoice_open()
        # create another invoice to check this invoice, as more recent, is used
        invoice_form2 = Form(self.env["account.invoice"])
        invoice_form2.partner_id = self.partner
        invoice_form2.type = "in_invoice"
        invoice_form2.date_invoice = fields.Date.today()
        invoice_form2.account_id = self.partner.property_account_payable_id
        invoice_form2.journal_id = self.account_journal_purchase
        with invoice_form2.invoice_line_ids.new() as line_form:
            line_form.name = "test"
            line_form.product_id = self.subproduct_1_2
            line_form.uom_id = self.subproduct_1_2.uom_id
            line_form.quantity = 2
            line_form.price_unit = new_price_subproduct_1_2
            line_form.account_id = self.invoice_line_account
            line_form.account_analytic_id = self.analytic_account
        invoice2 = invoice_form2.save()
        invoice2.action_invoice_open()

        analytic_lines = self.env["account.analytic.line"].search(
            [
                ("account_id", "=", self.analytic_account.id),
            ]
        )
        self.assertTrue(analytic_lines)
        for production in productions:
            self.assertEqual(len(production.move_raw_ids.mapped("product_id")), 3)
        # subproduct 1.1 is invoiced for 12 pc, 10 of them used in MO, at price 25, so
        # take the cost of 12 * 25€ + 13 * 35€ = 755
        # subproduct 1.2 is invoiced for 10 pc at price 8 and refunded for 5 pc at
        # price 4, but MO uses 6 pc, so take the cost of 6 * 8 = 48 for 2 productions, +
        # 3 productions = 120
        # subproduct 1.3 is invoiced but not used in production, but it has the analytic
        # account set, so take the total cost of the line: 7 * 220 = 1540
        # subproduct 1.4 is not invoiced, so cannot be shown here as it doesn't create
        # an analytic line
        # (note for reporting logic: take the cost of the last purchase with
        # enough quantity to be eligible, if not possible take the last purchase, else
        # take the product standard price (which is the cost))
        actual_cost = 0
        # check subproduct 1_1
        subproduct_1_1_invoice1_lines = invoice1.invoice_line_ids.filtered(
            lambda x: x.account_analytic_id == self.analytic_account
            and x.product_id == self.subproduct_1_1
        )
        subproduct_1_1_invoice_lines = invoice.invoice_line_ids.filtered(
            lambda x: x.account_analytic_id == self.analytic_account
            and x.product_id == self.subproduct_1_1
        )
        subproduct_1_1_move_raws = productions.mapped("move_raw_ids").filtered(
            lambda x: x.product_id == self.subproduct_1_1
        )
        actual_unit_cost1_subproduct_1_1 = sum(
            x.price_subtotal for x in subproduct_1_1_invoice1_lines
        ) / sum(x.quantity for x in subproduct_1_1_invoice1_lines)
        self.assertAlmostEqual(actual_unit_cost1_subproduct_1_1, 25, 2)
        actual_unit_cost_subproduct_1_1 = sum(
            x.price_subtotal for x in subproduct_1_1_invoice_lines
        ) / sum(x.quantity for x in subproduct_1_1_invoice_lines)
        self.assertAlmostEqual(actual_unit_cost_subproduct_1_1, 35, 2)
        actual_qty_subproduct_1_1 = sum(
            x.quantity_done for x in subproduct_1_1_move_raws
        )
        actual_cost += (
            13 * actual_unit_cost_subproduct_1_1 + 12 * actual_unit_cost1_subproduct_1_1
        )
        self.assertAlmostEqual(actual_cost, 755, 2)
        # check subproduct 1_2
        subproduct_1_2_invoice_lines = invoice.invoice_line_ids.filtered(
            lambda x: x.account_analytic_id == self.analytic_account
            and x.product_id == self.subproduct_1_2
        )
        subproduct_1_2_move_raws = productions.mapped("move_raw_ids").filtered(
            lambda x: x.product_id == self.subproduct_1_2
        )
        actual_unit_cost_subproduct_1_2 = sum(
            x.price_subtotal for x in subproduct_1_2_invoice_lines
        ) / sum(x.quantity for x in subproduct_1_2_invoice_lines)
        self.assertAlmostEqual(actual_unit_cost_subproduct_1_2, 8, 2)
        actual_qty_subproduct_1_2 = sum(
            x.quantity_done for x in subproduct_1_2_move_raws
        )
        actual_cost += actual_qty_subproduct_1_2 * actual_unit_cost_subproduct_1_2
        self.assertAlmostEqual(actual_cost, 755 + (48 + 72), 2)
        # check subproduct 1_3
        subproduct_1_3_invoice_lines = invoice.invoice_line_ids.filtered(
            lambda x: x.account_analytic_id == self.analytic_account
            and x.product_id == self.subproduct_1_3
        )
        actual_cost_subproduct_1_3 = sum(
            x.price_subtotal for x in subproduct_1_3_invoice_lines
        )
        actual_qty_subproduct_1_3 = sum(
            x.quantity for x in subproduct_1_3_invoice_lines
        )
        self.assertAlmostEqual(
            actual_cost_subproduct_1_3,
            actual_qty_subproduct_1_3 * self.subproduct_1_3.standard_price,
            2,
        )
        actual_cost += actual_cost_subproduct_1_3
        self.assertAlmostEqual(actual_cost, 755 + (80 + 40) + 1540, 2)
        # Note: the cost of subproduct 1_4 has to be put in reports in another way, as
        # it is not present in analytic lines.
        self.assertAlmostEqual(
            sum(
                analytic_lines.filtered(
                    lambda a: a.product_id == self.subproduct_1_3
                ).mapped("extra_cost")
            ),
            -1540,
            2,
        )
        self.assertAlmostEqual(
            sum(
                analytic_lines.filtered(
                    lambda a: a.product_id == self.subproduct_1_1
                ).mapped("extra_cost")
            ),
            -755,
            2,
        )
        self.assertAlmostEqual(
            sum(
                analytic_lines.filtered(
                    lambda a: a.product_id == self.subproduct_1_2
                ).mapped("extra_cost")
            ),
            -(80 + 40),
            2,
        )
