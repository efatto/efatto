# Copyright 2023 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import time

from odoo.tests.common import Form, SingleTransactionCase
from odoo.tools import mute_logger


class StockProcurementDraftPurchase(SingleTransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.user_model = cls.env["res.users"].with_context(no_reset_password=True)
        cls.partner = cls.env.ref("base.res_partner_2")
        cls.partner.customer_rank = 1
        cls.procurement_model = cls.env["procurement.group"]
        buy = cls.env.ref("purchase_stock.route_warehouse0_buy")
        cls.vendor = cls.env.ref("base.res_partner_3")
        supplierinfo = cls.env["product.supplierinfo"].create(
            {
                "name": cls.vendor.id,
                "delay": 30,
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product Test",
                "standard_price": 50.0,
                "seller_ids": [(6, 0, [supplierinfo.id])],
                "route_ids": [(6, 0, [buy.id])],
            }
        )
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.scheduler_compute_wiz = cls.env["stock.scheduler.compute"]
        # Create User:
        cls.test_user = cls.env["res.users"].create(
            {
                "name": "John",
                "login": "test",
                "groups_id": [
                    (
                        6,
                        0,
                        (
                            cls.env.ref("stock.group_stock_manager")
                            | cls.env.ref("purchase.group_purchase_manager")
                        ).ids,
                    )
                ],
            }
        )

    def run_stock_procurement_scheduler(self):
        with mute_logger("odoo.addons.stock.models.procurement"):
            self.procurement_model.run_scheduler()
            time.sleep(10)

    def test_00_procurement(self):
        # create reordering rule
        orderpoint_form = Form(self.env["stock.warehouse.orderpoint"])
        orderpoint_form.warehouse_id = self.warehouse
        orderpoint_form.location_id = self.warehouse.lot_stock_id
        orderpoint_form.product_id = self.product
        orderpoint_form.product_min_qty = 10.0
        orderpoint_form.product_max_qty = 50.0
        orderpoint_form.qty_multiple = 1.0
        op1 = orderpoint_form.save()
        self.assertEqual(op1.product_location_qty, 0)
        self.assertEqual(op1.incoming_location_qty, 0)
        self.assertEqual(op1.draft_purchase_order_qty, 0)
        self.assertEqual(op1.outgoing_location_qty, 0)
        self.assertEqual(op1.virtual_location_qty, 0)
        self.assertEqual(op1.virtual_location_draft_purchase_qty, 0)
        # launch scheduler, it will order 50 pc of product
        self.run_stock_procurement_scheduler()
        self.assertEqual(op1.draft_purchase_order_qty, 50)
        self.assertEqual(op1.virtual_location_draft_purchase_qty, 50)
        purchase_orders = self.env["purchase.order"].search(
            [("order_line.orderpoint_id", "=", op1.id)]
        )
        self.assertEqual(len(purchase_orders), 1)
        purchase_order1 = purchase_orders[0]
        purchase_line = purchase_order1.order_line.filtered(
            lambda x: x.product_id.id == self.product.id
        )
        self.assertEqual(purchase_line.product_uom_qty, 50)
        self.assertEqual(purchase_order1.state, "draft")
        purchase_order1.print_quotation()
        self.assertEqual(purchase_order1.state, "sent")

        # sell 5 pc would not create any replenishement (10 min, 50 max, 50 incoming,
        # 45 virtual available)
        order_form1 = Form(self.env["sale.order"])
        order_form1.partner_id = self.partner
        with order_form1.order_line.new() as order_line:
            order_line.product_id = self.product
            order_line.product_uom_qty = 5
            order_line.price_unit = 100
        order1 = order_form1.save()
        order1.action_confirm()
        self.run_stock_procurement_scheduler()
        # check that no other RdP are created for this op for the sale order
        purchase_orders = self.env["purchase.order"].search(
            [
                ("order_line.orderpoint_id", "=", op1.id),
                ("state", "=", "draft"),
            ]
        )
        self.assertEqual(len(purchase_orders), 0)

        # sell other 40 pc would create a replenishement (10 min, 50 max, 50 incoming,
        # 45 outgoing, 5 virtual available)
        order_form2 = Form(self.env["sale.order"])
        order_form2.partner_id = self.partner
        with order_form2.order_line.new() as order_line:
            order_line.product_id = self.product
            order_line.product_uom_qty = 40
            order_line.price_unit = 100
        order2 = order_form2.save()
        order2.action_confirm()
        self.run_stock_procurement_scheduler()
        # check that one RdP is created for this op
        purchase_orders = self.env["purchase.order"].search(
            [
                ("order_line.orderpoint_id", "=", op1.id),
                ("state", "=", "draft"),
            ]
        )
        self.assertEqual(len(purchase_orders), 1)
        purchase_order2 = purchase_orders[0]
        purchase_line2 = purchase_order2.order_line.filtered(
            lambda x: x.product_id.id == self.product.id
        )
        self.assertEqual(purchase_line2.product_uom_qty, 45)
        self.assertEqual(purchase_order2.state, "draft")
        purchase_order2.print_quotation()
        self.assertEqual(purchase_order2.state, "sent")

        # check that even if sent the purchase order is not recreated
        self.run_stock_procurement_scheduler()
        purchase_orders = self.env["purchase.order"].search(
            [
                ("order_line.orderpoint_id", "=", op1.id),
                ("state", "=", "draft"),
            ]
        )
        self.assertEqual(len(purchase_orders), 0)
