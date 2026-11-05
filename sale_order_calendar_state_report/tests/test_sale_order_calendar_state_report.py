from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestSaleOrderCalendarStateReport(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Report Customer"})
        cls.product = cls.env["product.product"].create(
            {"name": "Report Product", "is_storable": True}
        )
        cls.env["mrp.bom"].create(
            {"product_tmpl_id": cls.product.product_tmpl_id.id, "product_qty": 1.0}
        )
        cls.order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product.id,
                            "product_uom_qty": 3.0,
                            "price_unit": 10.0,
                        },
                    )
                ],
            }
        )
        cls.order.action_confirm()
        cls.production = cls.env["mrp.production"].create(
            {
                "product_id": cls.product.id,
                "product_qty": 3.0,
                "procurement_group_id": cls.order.procurement_group_id.id,
            }
        )
        cls.order.invalidate_recordset()
        cls.report_model = cls.env["sale.order.calendar.state.report"]

    def test_report_view_columns(self):
        """Every column of the SQL view must exist and be readable."""
        report = self.report_model.search([("name", "=", self.order.name)])
        self.assertEqual(len(report), 1)
        self.assertEqual(report.calendar_state, self.order.calendar_state)
        self.assertEqual(report.production_id, self.production)
        self.assertEqual(report.production_qty, 3.0)
        self.assertEqual(report.amount_untaxed, 30.0)
        self.assertEqual(
            fields.Date.to_date(report.sale_order_max_commitment_date),
            self.order.max_commitment_date.date(),
        )
        self.assertEqual(
            fields.Date.to_date(report.production_date_planned_start),
            self.production.date_start.date(),
        )
        self.assertEqual(report.country_id, self.partner.country_id)

    def test_report_group_by_calendar_state(self):
        groups = self.report_model._read_group(
            [("name", "=", self.order.name)],
            ["calendar_state"],
            ["production_qty:sum"],
        )
        self.assertEqual(groups, [(self.order.calendar_state, 3.0)])

    def test_report_date_filter(self):
        """The 'from last month' search filters must be usable on the view."""
        today = fields.Date.context_today(self.order)
        first_day_last_month = (today + relativedelta(months=-1)).replace(day=1)
        domain = [
            ("name", "=", self.order.name),
            ("sale_order_max_commitment_date", ">=", first_day_last_month),
            ("production_date_planned_start", ">=", first_day_last_month),
        ]
        self.assertEqual(len(self.report_model.search(domain)), 1)
