
import time

from odoo.tests.common import Form, SingleTransactionCase
from odoo.tools import mute_logger


class StockProcurementDraftPurchase(SingleTransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.user_model = cls.env["res.users"].with_context(no_reset_password=True)
        cls.procurement_model = cls.env["procurement.group"]
        cls.orderpoint_model = cls.env["stock.warehouse.orderpoint"]
        buy = cls.env.ref("purchase_stock.route_warehouse0_buy")
        cls.subcontractor = cls.env.ref("base.res_partner_3")
        cls.vendor = cls.env.ref("base.res_partner_4")
        supplierinfo_subcontractor = cls.env["product.supplierinfo"].create(
            {
                "name": cls.subcontractor.id,
                "delay": 30,
            }
        )
        supplierinfo_vendor = cls.env["product.supplierinfo"].create(
            {
                "name": cls.vendor.id,
                "delay": 10,
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product Test",
                "standard_price": 50.0,
                "seller_ids": [(6, 0, [supplierinfo_subcontractor.id])],
                "route_ids": [(6, 0, [buy.id])],
            }
        )
        cls.component = cls.env["product.product"].create(
            {
                "name": "Component Test",
                "standard_price": 7.0,
                "seller_ids": [(6, 0, [supplierinfo_vendor.id])],
                "route_ids": [(6, 0, [buy.id])],
            }
        )
        bom_form = Form(cls.env["mrp.bom"])
        bom_form.product_tmpl_id = cls.product.product_tmpl_id
        bom_form.product_qty = 1
        bom_form.type = "subcontract"
        bom_form.subcontractor_ids.add(cls.subcontractor)
        with bom_form.bom_line_ids.new() as line:
            line.product_id = cls.component
            line.product_qty = 3
        cls.bom = bom_form.save()
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.scheduler_compute_wiz = cls.env["stock.scheduler.compute"]
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

    def test_00_procurement_from_subcontractor(self):
        self.assertEqual(self.product.bom_ids.ids, self.bom.ids)
        self.assertEqual(self.product.bom_ids.subcontractor_ids.ids,
                         self.subcontractor.ids)
        self.assertTrue(self.product.seller_ids.is_subcontractor)
        orderpoint_form = Form(self.orderpoint_model)
        orderpoint_form.warehouse_id = self.warehouse
        orderpoint_form.location_id = self.warehouse.lot_stock_id
        orderpoint_form.product_id = self.product
        orderpoint_form.product_min_qty = 10.0
        orderpoint_form.product_max_qty = 50.0
        orderpoint_form.qty_multiple = 1.0
        op1 = orderpoint_form.save()
        self.run_stock_procurement_scheduler()
        op1.refresh()
        purchase_orders = self.env["purchase.order"].search(
            [("order_line.product_id", "=", op1.product_id.id)]
        )
        self.assertEqual(len(purchase_orders), 1)
        purchase_order = purchase_orders[0]
        purchase_line = purchase_order.order_line.filtered(
            lambda x: x.product_id.id == self.product.id
        )
        self.assertEqual(purchase_line.product_uom_qty, 50)
        self.assertEqual(purchase_order.state, "draft")
        purchase_order.button_confirm()
        self.assertEqual(purchase_order.state, "purchase")
