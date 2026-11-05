# Copyright 2026 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestSaleOrderComponent(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        product_model = cls.env["product.product"]
        cls.finished = product_model.create(
            {
                "name": "Finished product",
                "type": "consu",
                "is_storable": True,
                "sale_delay": 5,
            }
        )
        cls.sub = product_model.create(
            {"name": "Sub component", "type": "consu", "is_storable": True}
        )
        cls.comp = product_model.create(
            {"name": "Component", "type": "consu", "is_storable": True}
        )
        cls.bom_sub = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": cls.sub.product_tmpl_id.id,
                "product_qty": 1.0,
                "produce_delay": 3,
                "bom_line_ids": [
                    (0, 0, {"product_id": cls.comp.id, "product_qty": 2.0})
                ],
            }
        )
        cls.bom_finished = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": cls.finished.product_tmpl_id.id,
                "product_qty": 1.0,
                "produce_delay": 2,
                "bom_line_ids": [
                    (0, 0, {"product_id": cls.sub.id, "product_qty": 1.0})
                ],
            }
        )
        cls.partner = cls.env["res.partner"].create({"name": "Component customer"})
        cls.order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.finished.id,
                            "product_uom_qty": 5.0,
                        },
                    )
                ],
            }
        )
        cls.order_line = cls.order.order_line

    def _get_component_lines(self):
        wizard = (
            self.env["sale.component"]
            .with_context(active_id=self.order_line.id)
            .create({})
        )
        return wizard, wizard.line_ids

    def test_bom_explode(self):
        res = self.order._bom_explode(self.finished, [])
        self.assertEqual(len(res), 2)
        by_product = {item["product_id"]: item for item in res}
        self.assertEqual(by_product[self.sub.id]["qty"], 1.0)
        self.assertEqual(by_product[self.comp.id]["qty"], 2.0)
        self.assertEqual(by_product[self.sub.id]["parent_id"], self.finished.id)
        self.assertEqual(by_product[self.comp.id]["parent_id"], self.sub.id)

    def test_bom_explode_no_bom(self):
        self.assertEqual(self.order._bom_explode(self.comp, []), [])

    def test_display_qty_component_widget(self):
        self.assertTrue(self.order_line.display_qty_component_widget)
        product_without_bom = self.env["product.product"].create(
            {"name": "No BoM product", "type": "consu", "is_storable": True}
        )
        line_without_bom = self.env["sale.order.line"].create(
            {
                "order_id": self.order.id,
                "product_id": product_without_bom.id,
                "product_uom_qty": 1.0,
            }
        )
        self.assertFalse(line_without_bom.display_qty_component_widget)

    def test_wizard_components(self):
        wizard, line_ids = self._get_component_lines()
        self.assertEqual(len(line_ids), 2)
        sub_line = line_ids.filtered(lambda line: line.product_id == self.sub)
        comp_line = line_ids.filtered(lambda line: line.product_id == self.comp)
        self.assertEqual(sub_line.component_bom_qty, 1.0)
        self.assertEqual(comp_line.component_bom_qty, 2.0)
        self.assertEqual(comp_line.parent_id, sub_line)
        self.assertEqual(comp_line.sale_order_line_id, self.order_line)
        self.assertEqual(wizard.sale_order_line_id, self.order_line)
        self.assertEqual(comp_line.qty_to_deliver, 10.0)
        self.assertTrue(comp_line.display_qty_widget)
        # qty at date values are computed
        self.assertTrue(comp_line.scheduled_date)
        self.assertTrue(comp_line.warehouse_id)
        self.assertTrue(comp_line.virtual_available_at_date <= 0.0)
        self.assertFalse(comp_line.commitment_date)

    def test_wizard_components_service_product(self):
        self.finished.type = "service"
        _wizard, line_ids = self._get_component_lines()
        self.assertFalse(line_ids)

    def test_component_delay(self):
        _wizard, line_ids = self._get_component_lines()
        comp_line = line_ids.filtered(lambda line: line.product_id == self.comp)
        # sale_delay of the component + produce_delay of its BoM
        self.assertEqual(comp_line._get_component_delay(self.comp), 0.0)
        self.assertEqual(comp_line._get_component_delay(self.sub), 3.0)

    def test_mrp_component_ids(self):
        mto_route = self.env.ref("stock.route_warehouse0_mto", raise_if_not_found=False)
        if mto_route:
            mto_route.active = True
        manufacture_route = self.env.ref("mrp.route_warehouse0_manufacture")
        routes = self.env["stock.route"]
        if mto_route:
            routes |= mto_route
        routes |= manufacture_route
        self.finished.product_tmpl_id.route_ids = routes
        self.order.action_confirm()
        self.assertTrue(self.order.mrp_production_ids)
        self.assertIn(self.sub, self.order.mrp_component_ids)
        # the components filter of the sale order search view is valid
        orders = self.env["sale.order"].search(
            [("mrp_production_ids.move_raw_ids.product_id", "ilike", self.sub.name)]
        )
        self.assertIn(self.order, orders)
