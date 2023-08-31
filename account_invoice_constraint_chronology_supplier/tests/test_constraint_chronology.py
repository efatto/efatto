# Copyright 2015-2019 ACSONE SA/NV (<http://acsone.eu>)
# Copyright 2020 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import datetime, timedelta

from odoo.exceptions import UserError
from odoo.tests.common import Form, SavepointCase
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class TestAccountConstraintChronologySupplier(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.inv_model = cls.env["account.move"]
        cls.user_model = cls.env["res.users"].with_context(no_reset_password=True)
        cls.group_accounting = cls.env.ref("account.group_account_user")
        cls.account_user = cls.user_model.create(
            [
                {
                    "name": "Accounting user",
                    "login": "account user",
                    "email": "account@email.it",
                    "groups_id": [
                        (4, cls.group_accounting.id),
                    ],
                }
            ]
        )
        cls.account_type_expense = cls.env["account.account.type"].create(
            {
                "name": "Account type expense",
                "type": "other",
                "include_initial_balance": True,
                "internal_group": "expense",
            }
        )
        cls.account_expense = cls.env["account.account"].create(
            {
                "name": "Account expense",
                "code": "X2021",
                "user_type_id": cls.account_type_expense.id,
                "reconcile": True,
            }
        )
        cls.account_journal_purchase_check = cls.env["account.journal"].create(
            {
                "name": "Purchase journal with check chronology",
                "code": "PURCH",
                "type": "purchase",
                "check_chronology": True,
            }
        )
        cls.account_journal_purchase = cls.env["account.journal"].create(
            {
                "name": "Purchase journal without check chronology",
                "code": "PURCH",
                "type": "purchase",
            }
        )
        cls.product = cls.env["product.product"].create({"name": "product name"})

    def create_simple_invoice(self, journal_id, date):
        invoice_form = Form(
            self.inv_model.with_user(self.account_user).with_context(
                check_move_validity=False,
                company_id=self.account_user.company_id.id,
                default_move_type="in_invoice",
            )
        )
        invoice_form.date = date
        invoice_form.invoice_date = date
        invoice_form.partner_id = self.env.ref("base.res_partner_2")
        invoice_form.journal_id = journal_id
        with invoice_form.invoice_line_ids.new() as invoice_line_form:
            invoice_line_form.product_id = self.product
            invoice_line_form.quantity = 1.0
            invoice_line_form.price_unit = 100.0
            invoice_line_form.name = "product that cost 100"
            invoice_line_form.account_id = self.account_expense
        invoice = invoice_form.save()
        return invoice

    def test_invoice_draft(self):
        journal = self.account_journal_purchase_check
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        date = yesterday.strftime(DEFAULT_SERVER_DATE_FORMAT)
        self.create_simple_invoice(journal, date)
        date = today.strftime(DEFAULT_SERVER_DATE_FORMAT)
        invoice_2 = self.create_simple_invoice(journal, date)
        self.assertTrue(
            (invoice_2.state == "draft"), "Initial invoice state is not Draft"
        )
        invoice_2.action_post()
        self.assertTrue((invoice_2.state == "posted"), "Invoice state is not Posted")

    def test_invoice_draft_no_check(self):
        journal = self.account_journal_purchase
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        date = yesterday.strftime(DEFAULT_SERVER_DATE_FORMAT)
        self.create_simple_invoice(journal, date)
        date = today.strftime(DEFAULT_SERVER_DATE_FORMAT)
        invoice_2 = self.create_simple_invoice(journal, date)
        self.assertTrue(
            (invoice_2.state == "draft"), "Initial invoice state is not Draft"
        )
        invoice_2.action_post()
        self.assertTrue(invoice_2.state == "posted", "Invoice state is not Posted")

    def test_invoice_validate_with_date_lesser_then_invoice_date(self):
        journal = self.account_journal_purchase_check
        today = datetime.now()
        tomorrow = today + timedelta(days=1)
        date_tomorrow = tomorrow.strftime(DEFAULT_SERVER_DATE_FORMAT)
        invoice_1 = self.create_simple_invoice(journal, date_tomorrow)
        self.assertTrue(
            (invoice_1.state == "draft"), "Initial invoice state is not Draft"
        )
        invoice_1.action_post()
        date = today.strftime(DEFAULT_SERVER_DATE_FORMAT)
        invoice_2 = self.create_simple_invoice(journal, date_tomorrow)
        invoice_2.write({"date": date})
        self.assertTrue(
            (invoice_2.state == "draft"), "Initial invoice state is not Draft"
        )
        with self.assertRaises(UserError):
            invoice_2.action_post()

    def test_journal_change_type(self):
        self.account_journal_purchase.check_chronology = True
        self.assertTrue(self.account_journal_purchase.check_chronology)
        self.account_journal_purchase.type = "bank"
        self.account_journal_purchase._onchange_type()
        self.assertFalse(self.account_journal_purchase.check_chronology)

    def test_supplier_invoice_date(self):
        journal = self.account_journal_purchase_check
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        invoice = self.create_simple_invoice(
            journal, today.strftime(DEFAULT_SERVER_DATE_FORMAT)
        )
        invoice.date = yesterday.strftime(DEFAULT_SERVER_DATE_FORMAT)
        with self.assertRaises(UserError):
            invoice.action_post()
