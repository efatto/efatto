import time
from unittest.mock import patch

from odoo.tests import Form, new_test_user, users
from odoo.tools import mute_logger
from odoo.tools.config import config

from odoo.addons.base.tests.common import BaseCommon


class StockProcurementDraftPurchase(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.procurement_model = cls.env["procurement.group"]
        cls.orderpoint_model = cls.env["stock.warehouse.orderpoint"]
        buy = cls.env.ref("purchase_stock.route_warehouse0_buy")
        cls.subcontractor = cls.env.ref("base.res_partner_3")
        cls.vendor = cls.env.ref("base.res_partner_4")
        supplierinfo_subcontractor = cls.env["product.supplierinfo"].create(
            {
                "partner_id": cls.subcontractor.id,
                "delay": 30,
            }
        )
        supplierinfo_vendor = cls.env["product.supplierinfo"].create(
            {
                "partner_id": cls.vendor.id,
                "delay": 10,
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product Test",
                "standard_price": 50.0,
                "seller_ids": [(6, 0, [supplierinfo_subcontractor.id])],
                "route_ids": [(6, 0, [buy.id])],
                "type": "consu",
                "is_storable": True,
            }
        )
        cls.component = cls.env["product.product"].create(
            {
                "name": "Component Test",
                "standard_price": 7.0,
                "seller_ids": [(6, 0, [supplierinfo_vendor.id])],
                "route_ids": [(6, 0, [buy.id])],
                "type": "consu",
                "is_storable": True,
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
        cls.test_user = new_test_user(
            cls.env,
            name="John",
            login="test",
            groups=(
                "stock.group_stock_manager,"
                "purchase.group_purchase_manager,"
                "mrp.group_mrp_user"
            ),
        )

    def run_stock_procurement_scheduler(self):
        with patch.dict(config.options, {"running_env": "prod"}):
            with mute_logger("odoo.addons.stock.models.procurement"):
                self.procurement_model.run_scheduler()
                time.sleep(10)

    @users("test")
    def test_00_procurement_from_subcontractor(self):
        self.assertEqual(self.product.bom_ids.ids, self.bom.ids)
        self.assertEqual(
            self.product.bom_ids.subcontractor_ids.ids, self.subcontractor.ids
        )
        self.assertTrue(self.product.seller_ids.is_subcontractor)
        op1 = self.orderpoint_model.create(
            {
                "warehouse_id": self.warehouse.id,
                "location_id": self.warehouse.lot_stock_id.id,
                "product_id": self.product.id,
                "product_min_qty": 10.0,
                "product_max_qty": 50.0,
                "qty_multiple": 1.0,
            }
        )
        self.run_stock_procurement_scheduler()
        op1.invalidate_recordset()
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
        self.assertTrue(purchase_order.subcontract_production_ids)
        mo = purchase_order.subcontract_production_ids
        self.assertEqual(mo.state, "confirmed")
        picking = purchase_order.picking_ids
        for move in picking.move_ids:
            if move.product_id.is_storable:
                move.quantity = move.product_uom_qty
                move.picked = True
        picking.button_validate()
        self.assertEqual(picking.state, "done")
        self.assertEqual(mo.state, "done")
