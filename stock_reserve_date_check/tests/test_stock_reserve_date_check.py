from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import Form
from odoo.tools import mute_logger
from odoo.tools.date_utils import relativedelta

from odoo.addons.mrp_production_demo.tests.common_data import TestProductionData


class TestStockReserveDateCheck(TestProductionData):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env.ref("base.res_partner_2")
        cls.partner.customer_rank = 1
        cls.buy_route = cls.env.ref("purchase_stock.route_warehouse0_buy")
        cls.manufacture_route = cls.env.ref("mrp.route_warehouse0_manufacture")
        cls.vendor = cls.env.ref("base.res_partner_3")
        supplierinfo = cls.env["product.supplierinfo"].create(
            [
                {
                    "partner_id": cls.vendor.id,
                    "delay": 10,
                }
            ]
        )
        cls.product = cls.env["product.product"].create(
            [
                {
                    "name": "Product Test",
                    "standard_price": 50.0,
                    "type": "consu",
                    "seller_ids": [(6, 0, [supplierinfo.id])],
                    "route_ids": [(6, 0, [cls.buy_route.id])],
                }
            ]
        )
        # Create User:
        cls.test_user = cls.env["res.users"].create(
            {
                "name": "John",
                "login": "test",
                "email": "test@test.email",
            }
        )
        cls.test_user.write(
            {
                "groups_id": [(4, cls.env.ref("sales_team.group_sale_salesman").id)],
            }
        )

    def _create_sale_order_line(self, order, product, qty, commitment_date=False):
        order_form = Form(
            order.with_user(self.test_user),
            view="sale_order_line_date.sale_order_commitment_date_form_view",
        )
        with order_form.order_line.new() as line_form:
            line_form.product_id = product
            line_form.product_uom_qty = qty
            line_form.price_unit = 100
        order = order_form.save()
        if commitment_date:
            order.order_line.commitment_date = commitment_date

    @mute_logger("odoo.models", "odoo.models.unlink", "odoo.addons.base.ir.ir_model")
    def test_00_sale_from_stock(self):
        order1 = (
            self.env["sale.order"]
            .with_user(self.test_user)
            .create(
                {
                    "partner_id": self.partner.id,
                    "enable_reserve_date_check": True,
                }
            )
        )
        self._create_sale_order_line(order1, self.product, 5)
        self.assertEqual(self.product.type, "consu")
        # available_date_str = (
        #     fields.Date.today() + relativedelta(days=self.product.purchase_delay)
        # ).strftime("%d/%m/%Y")
        exception_msg = "Reservation of product.*is not possible for date.*"
        # ) % (
        #     self.product.default_code,
        #     self.product.name,
        #     fields.Date.today().strftime("%d/%m/%Y"),
        #     available_date_str,
        # )
        with self.assertRaisesRegex(UserError, exception_msg):
            order1.with_user(self.test_user).action_confirm()
        self.assertEqual(order1.state, "draft")

    def test_01_sale_from_stock(self):
        order2 = (
            self.env["sale.order"]
            .with_user(self.test_user)
            .create(
                {
                    "partner_id": self.partner.id,
                    "enable_reserve_date_check": True,
                }
            )
        )
        commitment_date = fields.Datetime.now() + relativedelta(days=10)
        self._create_sale_order_line(
            order2, self.product, qty=5, commitment_date=commitment_date
        )
        self.assertEqual(order2.order_line[0].commitment_date, commitment_date)
        order2.with_user(self.test_user).action_confirm()
        self.assertEqual(order2.state, "sale")

    @mute_logger("odoo.models", "odoo.models.unlink", "odoo.addons.base.ir.ir_model")
    def test_02_sale_from_mrp(self):
        self.main_bom.produce_delay = 14
        self.main_bom.days_to_prepare_mo = 7
        order3 = (
            self.env["sale.order"]
            .with_user(self.test_user)
            .create(
                {
                    "partner_id": self.partner.id,
                    "enable_reserve_date_check": True,
                }
            )
        )
        commitment_date = fields.Datetime.now() + relativedelta(days=10)
        self._create_sale_order_line(
            order3, self.top_product, qty=5, commitment_date=commitment_date
        )
        with self.assertRaises(UserError):
            order3.with_user(self.test_user).action_confirm()
        self.assertEqual(order3.state, "draft")
        # top product 14 days + subproduct 28 days
        commitment_date = fields.Datetime.now() + relativedelta(days=14 + 28)
        order_line = order3.order_line[0]
        order_line.commitment_date = commitment_date
        order3.with_user(self.test_user).action_confirm()
        self.assertEqual(order3.state, "sale")
        self.assertEqual(order3.order_line[0].commitment_date, commitment_date)
        order3._action_cancel()  # to bypass warnings
        self.assertEqual(order3.state, "cancel")
        order3.action_draft()
        order3.action_confirm()
        self.assertEqual(order3.state, "sale")
