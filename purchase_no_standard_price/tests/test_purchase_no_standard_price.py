from datetime import timedelta

from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.tests import Form, new_test_user, users

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT, BaseCommon


class TestPurchaseNoStandardPrice(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        new_test_user(
            cls.env, login="test-purchase-user", groups="purchase.group_purchase_user"
        )
        cls.vendor = cls.env.ref("base.res_partner_3")
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product",
                "standard_price": 5.0,
                "seller_ids": [
                    (
                        0,
                        0,
                        {
                            "partner_id": cls.vendor.id,
                            "price": 10.0,
                            "date_end": fields.Date.today() + relativedelta(days=-1),
                        },
                    )
                ],
            }
        )
        cls.product2 = cls.env["product.product"].create(
            {
                "name": "Product 2",
                "standard_price": 6.0,
                "seller_ids": [
                    (
                        0,
                        0,
                        {
                            "partner_id": cls.vendor.id,
                            "price": 10.0,
                        },
                    )
                ],
            }
        )

    @users("test-purchase-user")
    def test_00_purchase_order(self):
        qty, qty1, ref = 20, 40, "Vendor Reference"
        purchase_order = self.env["purchase.order"].create(
            {
                "partner_id": self.vendor.id,
                "partner_ref": ref,
            }
        )
        purchase_form = Form(purchase_order)
        with purchase_form.order_line.new() as purchase_line_form:
            purchase_line_form.product_id = self.product
            purchase_line_form.product_qty = qty
            purchase_line_form.product_uom = self.product.uom_po_id
            purchase_line_form.name = self.product.name
            purchase_line_form.date_planned = fields.Date.today() + timedelta(days=20)
        with purchase_form.order_line.new() as purchase_line_form:
            purchase_line_form.product_id = self.product2
            purchase_line_form.product_qty = qty1
            purchase_line_form.product_uom = self.product2.uom_po_id
            purchase_line_form.name = self.product2.name
            purchase_line_form.date_planned = fields.Date.today() + timedelta(days=20)
        purchase_order = purchase_form.save()
        purchase_order.button_confirm()
        self.assertEqual(
            len(purchase_order.order_line), 2, msg="Order line was not created"
        )
        self.assertRecordValues(
            purchase_order.order_line,
            [
                {
                    "product_id": self.product.id,
                    "price_unit": 0,
                },
                {
                    "product_id": self.product2.id,
                    "price_unit": 10,
                },
            ],
        )
