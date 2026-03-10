import time

from odoo.tests.common import Form, SavepointCase
from odoo.tools import mute_logger


class StockOrderpointGeneretorSale(SavepointCase):
    @classmethod
    def setUpClass(cls):
        # TODO this is a copy from other module
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
        # create the reordering rule model
        orderpoint_template_form = Form(self.env["stock.warehouse.orderpoint.template"])
        orderpoint_template_form.warehouse_id = self.warehouse
        orderpoint_template_form.location_id = self.warehouse.lot_stock_id
        orderpoint_template_form.auto_generate = True
        orderpoint_template_form.is_new_orderpoint_draft = True
        orderpoint_template_form.compute_on_out = True
        orderpoint_template_form.move_days = 365
        orderpoint_template_form.service_level = 0.97
        orderpoint_template_form.order_mngt_cost = 70
        opt = orderpoint_template_form.save()
        opt.write({"product_ctg_ids": [(6, 0, [self.product.categ_id.id])]})
        # launch scheduler, it will order 50 pc of product
        self.run_stock_procurement_scheduler()
        opt.refresh()
        # check that even if sent the purchase order is not recreated
        self.run_stock_procurement_scheduler()
        purchase_orders = self.env["purchase.order"].search(
            [
                ("order_line.orderpoint_id", "=", opt.id),
                ("state", "=", "draft"),
            ]
        )
        self.assertEqual(len(purchase_orders), 0)

    def test_01_create_instances_basic(self):
        """Test button_create_orderpoints creates orderpoints with correct fields"""
        self.product.orderpoint_generate_active = True
        orderpoint_template_form = Form(self.env["stock.warehouse.orderpoint.template"])
        orderpoint_template_form.warehouse_id = self.warehouse
        orderpoint_template_form.location_id = self.warehouse.lot_stock_id
        orderpoint_template_form.compute_on_sale = True
        orderpoint_template_form.move_days = 365
        orderpoint_template_form.service_level = 0.95
        orderpoint_template_form.order_mngt_cost = 50
        orderpoint_template_form.variation_percent = 10
        opt = orderpoint_template_form.save()
        opt.product_ctg_ids = [(6, 0, [self.product.categ_id.id])]

        # Call button_create_orderpoints
        opt.button_create_orderpoints()

        # Check that orderpoint was created
        orderpoints = self.env["stock.warehouse.orderpoint"].search(
            [("product_id", "=", self.product.id), ("orderpoint_tmpl_id", "=", opt.id)]
        )
        self.assertEqual(len(orderpoints), 1)
        orderpoint = orderpoints[0]

        # Verify fields are set correctly
        self.assertEqual(orderpoint.orderpoint_tmpl_id, opt)
        self.assertEqual(orderpoint.product_id, self.product)
        self.assertEqual(orderpoint.location_id, self.warehouse.lot_stock_id)
        self.assertIn(self.product.default_code, orderpoint.name)
        self.assertTrue(orderpoint.product_min_qty >= 0)
        self.assertTrue(orderpoint.product_max_qty >= orderpoint.product_min_qty)

    def test_02_create_instances_with_auto_min_max(self):
        """Test button_create_orderpoints calculates min/max quantities correctly"""
        self.product.orderpoint_generate_active = True
        orderpoint_template_form = Form(self.env["stock.warehouse.orderpoint.template"])
        orderpoint_template_form.warehouse_id = self.warehouse
        orderpoint_template_form.location_id = self.warehouse.lot_stock_id
        orderpoint_template_form.compute_on_sale = True
        orderpoint_template_form.auto_min_qty = True
        orderpoint_template_form.auto_max_qty = True
        orderpoint_template_form.move_days = 180
        orderpoint_template_form.service_level = 0.97
        orderpoint_template_form.order_mngt_cost = 70
        opt = orderpoint_template_form.save()
        opt.product_ctg_ids = [(6, 0, [self.product.categ_id.id])]

        opt.button_create_orderpoints()

        orderpoints = self.env["stock.warehouse.orderpoint"].search(
            [("product_id", "=", self.product.id), ("orderpoint_tmpl_id", "=", opt.id)]
        )
        self.assertEqual(len(orderpoints), 1)
        orderpoint = orderpoints[0]

        # Verify auto-calculated quantities
        self.assertGreater(orderpoint.product_min_qty, 0)
        self.assertGreater(orderpoint.product_max_qty, orderpoint.product_min_qty)

    def test_03_create_instances_draft_mode(self):
        """Test button_create_orderpoints creates draft orderpoints when flag is set"""
        self.product.orderpoint_generate_active = True
        orderpoint_template_form = Form(self.env["stock.warehouse.orderpoint.template"])
        orderpoint_template_form.warehouse_id = self.warehouse
        orderpoint_template_form.location_id = self.warehouse.lot_stock_id
        orderpoint_template_form.compute_on_sale = True
        orderpoint_template_form.move_days = 365
        orderpoint_template_form.service_level = 0.95
        orderpoint_template_form.order_mngt_cost = 50
        orderpoint_template_form.is_new_orderpoint_draft = True
        opt = orderpoint_template_form.save()
        opt.product_ctg_ids = [(6, 0, [self.product.categ_id.id])]

        # Create orderpoints via button
        opt.button_create_orderpoints()

        # Check orderpoint is draft and inactive
        orderpoints = (
            self.env["stock.warehouse.orderpoint"]
            .with_context(active_test=False)
            .search(
                [
                    ("product_id", "=", self.product.id),
                    ("orderpoint_tmpl_id", "=", opt.id),
                ]
            )
        )
        self.assertEqual(len(orderpoints), 1)
        orderpoint = orderpoints[0]
        self.assertTrue(orderpoint.is_draft)
        self.assertFalse(orderpoint.active)

    def test_04_create_instances_qty_multiple(self):
        """Test button_create_orderpoints sets qty_multiple from product"""
        self.product.orderpoint_generate_active = True
        self.product.purchase_multiple_qty = 5
        orderpoint_template_form = Form(self.env["stock.warehouse.orderpoint.template"])
        orderpoint_template_form.warehouse_id = self.warehouse
        orderpoint_template_form.location_id = self.warehouse.lot_stock_id
        orderpoint_template_form.compute_on_sale = True
        orderpoint_template_form.move_days = 365
        orderpoint_template_form.service_level = 0.95
        orderpoint_template_form.order_mngt_cost = 50
        opt = orderpoint_template_form.save()
        opt.product_ctg_ids = [(6, 0, [self.product.categ_id.id])]

        opt.button_create_orderpoints()

        orderpoints = self.env["stock.warehouse.orderpoint"].search(
            [("product_id", "=", self.product.id), ("orderpoint_tmpl_id", "=", opt.id)]
        )
        self.assertEqual(len(orderpoints), 1)
        orderpoint = orderpoints[0]
        self.assertEqual(orderpoint.qty_multiple, 5)

    def test_05_create_instances_variation_percent(self):
        """Test button_create_orderpoints applies variation_percent correctly"""
        self.product.orderpoint_generate_active = True
        orderpoint_template_form = Form(self.env["stock.warehouse.orderpoint.template"])
        orderpoint_template_form.warehouse_id = self.warehouse
        orderpoint_template_form.location_id = self.warehouse.lot_stock_id
        orderpoint_template_form.compute_on_sale = True
        orderpoint_template_form.move_days = 365
        orderpoint_template_form.service_level = 0.95
        orderpoint_template_form.order_mngt_cost = 50
        orderpoint_template_form.variation_percent = 20
        opt = orderpoint_template_form.save()
        opt.product_ctg_ids = [(6, 0, [self.product.categ_id.id])]

        opt.button_create_orderpoints()

        orderpoints = self.env["stock.warehouse.orderpoint"].search(
            [("product_id", "=", self.product.id), ("orderpoint_tmpl_id", "=", opt.id)]
        )
        self.assertEqual(len(orderpoints), 1)
        # The variation percent should affect the consumed_qty_by_lead_time calculation
        # which influences min_qty
        self.assertGreater(orderpoints[0].product_min_qty, 0)

    def test_06_create_instances_exclude_phantom_bom(self):
        """Test button_create_orderpoints excludes products with phantom BOM"""
        self.product.orderpoint_generate_active = True
        # Create a phantom BOM for the product
        bom_form = Form(self.env["mrp.bom"])
        bom_form.product_tmpl_id = self.product.product_tmpl_id
        bom_form.type = "phantom"
        bom_form.save()

        orderpoint_template_form = Form(self.env["stock.warehouse.orderpoint.template"])
        orderpoint_template_form.warehouse_id = self.warehouse
        orderpoint_template_form.location_id = self.warehouse.lot_stock_id
        orderpoint_template_form.compute_on_sale = True
        orderpoint_template_form.move_days = 365
        orderpoint_template_form.service_level = 0.95
        orderpoint_template_form.order_mngt_cost = 50
        opt = orderpoint_template_form.save()
        opt.product_ctg_ids = [(6, 0, [self.product.categ_id.id])]

        opt.button_create_orderpoints()

        # Check that no orderpoint was created
        orderpoints = self.env["stock.warehouse.orderpoint"].search(
            [("product_id", "=", self.product.id), ("orderpoint_tmpl_id", "=", opt.id)]
        )
        self.assertEqual(len(orderpoints), 0)
        # Check log_info contains message about phantom BOM
        self.assertIn("phantom bom", opt.log_info.lower())

    def test_07_create_instances_exclude_missing_price(self):
        """Test button_create_orderpoints excludes products without standard_price"""
        # Create product without price
        product_no_price = self.env["product.product"].create(
            {
                "name": "Product Without Price",
                "default_code": "NOPRICE",
                "standard_price": 0,
                "orderpoint_generate_active": True,
                "categ_id": self.product.categ_id.id,
            }
        )

        orderpoint_template_form = Form(self.env["stock.warehouse.orderpoint.template"])
        orderpoint_template_form.warehouse_id = self.warehouse
        orderpoint_template_form.location_id = self.warehouse.lot_stock_id
        orderpoint_template_form.compute_on_sale = True
        orderpoint_template_form.move_days = 365
        orderpoint_template_form.service_level = 0.95
        orderpoint_template_form.order_mngt_cost = 50
        opt = orderpoint_template_form.save()
        opt.product_ctg_ids = [(6, 0, [product_no_price.categ_id.id])]

        opt.button_create_orderpoints()

        # Check that no orderpoint was created
        orderpoints = self.env["stock.warehouse.orderpoint"].search(
            [
                ("product_id", "=", product_no_price.id),
                ("orderpoint_tmpl_id", "=", opt.id),
            ]
        )
        self.assertEqual(len(orderpoints), 0)
        # Check log_info contains message about missing price
        self.assertIn("missing price", opt.log_info.lower())

    def test_08_create_instances_compute_on_out(self):
        """Test button_create_orderpoints with compute_on_out flag"""
        self.product.orderpoint_generate_active = True
        orderpoint_template_form = Form(self.env["stock.warehouse.orderpoint.template"])
        orderpoint_template_form.warehouse_id = self.warehouse
        orderpoint_template_form.location_id = self.warehouse.lot_stock_id
        orderpoint_template_form.compute_on_out = True
        orderpoint_template_form.move_days = 365
        orderpoint_template_form.service_level = 0.95
        orderpoint_template_form.order_mngt_cost = 50
        opt = orderpoint_template_form.save()
        opt.product_ctg_ids = [(6, 0, [self.product.categ_id.id])]

        opt.button_create_orderpoints()

        orderpoints = self.env["stock.warehouse.orderpoint"].search(
            [("product_id", "=", self.product.id), ("orderpoint_tmpl_id", "=", opt.id)]
        )
        self.assertEqual(len(orderpoints), 1)
        # Verify orderpoint was created with correct template reference
        self.assertEqual(orderpoints[0].orderpoint_tmpl_id, opt)

    def test_09_create_instances_log_info(self):
        """Test button_create_orderpoints populates log_info with calculation details"""
        self.product.orderpoint_generate_active = True
        orderpoint_template_form = Form(self.env["stock.warehouse.orderpoint.template"])
        orderpoint_template_form.warehouse_id = self.warehouse
        orderpoint_template_form.location_id = self.warehouse.lot_stock_id
        orderpoint_template_form.compute_on_sale = True
        orderpoint_template_form.move_days = 180
        orderpoint_template_form.service_level = 0.97
        orderpoint_template_form.order_mngt_cost = 70
        opt = orderpoint_template_form.save()
        opt.product_ctg_ids = [(6, 0, [self.product.categ_id.id])]

        opt.button_create_orderpoints()

        # Check log_info is populated with calculation details
        self.assertTrue(opt.log_info)
        self.assertIn(self.product.default_code, opt.log_info)
        self.assertIn("Move days", opt.log_info)
        self.assertIn("Qty by day", opt.log_info)
        self.assertIn("Purchase delay", opt.log_info)
        self.assertIn("Security stock", opt.log_info)
        self.assertIn("Minimum qty", opt.log_info)
        self.assertIn("Maximum qty", opt.log_info)

    def test_10_create_instances_multiple_products(self):
        """Test button_create_orderpoints handles multiple products correctly"""
        # Create additional products
        product2 = self.env["product.product"].create(
            {
                "name": "Product Test 2",
                "standard_price": 75.0,
                "default_code": "TEST002",
                "orderpoint_generate_active": True,
                "categ_id": self.product.categ_id.id,
            }
        )
        product3 = self.env["product.product"].create(
            {
                "name": "Product Test 3",
                "standard_price": 100.0,
                "default_code": "TEST003",
                "orderpoint_generate_active": True,
                "categ_id": self.product.categ_id.id,
            }
        )
        self.product.orderpoint_generate_active = True

        orderpoint_template_form = Form(self.env["stock.warehouse.orderpoint.template"])
        orderpoint_template_form.warehouse_id = self.warehouse
        orderpoint_template_form.location_id = self.warehouse.lot_stock_id
        orderpoint_template_form.compute_on_sale = True
        orderpoint_template_form.move_days = 365
        orderpoint_template_form.service_level = 0.95
        orderpoint_template_form.order_mngt_cost = 50
        opt = orderpoint_template_form.save()
        opt.product_ctg_ids = [(6, 0, [self.product.categ_id.id])]

        opt.button_create_orderpoints()

        # Check that orderpoints were created for all products
        orderpoints = self.env["stock.warehouse.orderpoint"].search(
            [("orderpoint_tmpl_id", "=", opt.id)]
        )
        self.assertEqual(len(orderpoints), 3)
        product_ids = orderpoints.mapped("product_id")
        self.assertIn(self.product, product_ids)
        self.assertIn(product2, product_ids)
        self.assertIn(product3, product_ids)
