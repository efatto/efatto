from odoo.tests import tagged

from odoo.addons.base.tests.common import BaseCommon


@tagged("post_install", "-at_install")
class TestMrpSaleInfoLink(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        partner = cls.env["res.partner"].create({"name": "Production search customer"})
        cls.product = cls.env["product.product"].create({"name": "Production search"})
        cls.orders = cls.env["sale.order"].create(
            [
                {
                    "partner_id": partner.id,
                    "order_line": [
                        (0, 0, {"product_id": cls.product.id, "price_unit": 1})
                    ],
                }
                for _ in range(6)
            ]
        )
        (
            cls.empty_order,
            cls.empty_group_order,
            cls.line_order,
            cls.group_order,
            cls.move_order,
            cls.mixed_order,
        ) = cls.orders
        cls.env["procurement.group"].create(
            {
                "name": "Empty group",
                "sale_id": cls.empty_group_order.id,
            }
        )
        group = cls.env["procurement.group"].create(
            {
                "name": "Production group",
                "sale_id": cls.group_order.id,
            }
        )
        mixed_group = cls.env["procurement.group"].create(
            {
                "name": "Mixed group",
                "sale_id": cls.mixed_order.id,
            }
        )
        move_group = cls.env["procurement.group"].create(
            {
                "name": "Move group",
                "sale_id": cls.move_order.id,
            }
        )
        production_group = cls.env["procurement.group"].create(
            {
                "name": "Shared production group",
            }
        )
        cls.productions = cls.env["mrp.production"].create(
            [
                {
                    "product_id": cls.product.id,
                    "product_qty": 1,
                    "product_uom_id": cls.product.uom_id.id,
                    **values,
                }
                for values in [
                    {"name": "LINK/LINE", "sale_line_id": cls.line_order.order_line.id},
                    {"name": "LINK/GROUP", "procurement_group_id": group.id},
                    {"name": "LINK/MOVE", "procurement_group_id": production_group.id},
                    {
                        "name": "LINK/SIBLING",
                        "procurement_group_id": production_group.id,
                    },
                    {
                        "name": "LINK/MIXED",
                        "sale_line_id": cls.mixed_order.order_line.id,
                        "procurement_group_id": mixed_group.id,
                    },
                    {
                        "name": "OTHER/MIXED",
                        "sale_line_id": cls.mixed_order.order_line.id,
                    },
                    {"name": "UNLINKED"},
                ]
            ]
        )
        warehouse = cls.env["stock.warehouse"].search(
            [
                ("company_id", "=", cls.env.company.id),
            ],
            limit=1,
        )
        cls.env["stock.move"].create(
            {
                "name": "Production search move",
                "product_id": cls.product.id,
                "product_uom": cls.product.uom_id.id,
                "product_uom_qty": 1,
                "location_id": warehouse.lot_stock_id.id,
                "location_dest_id": cls.env.ref("stock.stock_location_customers").id,
                "group_id": move_group.id,
                "created_production_id": cls.productions[2].id,
            }
        )

    def _assert_search(self, operator, value, expected):
        result = self.env["sale.order"].search(
            [
                ("id", "in", self.orders.ids),
                ("mrp_production_ids", operator, value),
            ]
        )
        self.assertEqual(result, expected.sorted("id"))

    def test_computed_links(self):
        self.orders._compute_mrp_production_ids()
        self.assertFalse(self.empty_order.mrp_production_ids)
        self.assertFalse(self.empty_group_order.mrp_production_ids)
        self.assertEqual(self.line_order.mrp_production_ids, self.productions[:1])
        self.assertEqual(self.group_order.mrp_production_ids, self.productions[1:2])
        self.assertEqual(self.move_order.mrp_production_ids, self.productions[2:4])
        self.assertEqual(self.mixed_order.mrp_production_ids, self.productions[4:6])

    def test_ids_and_negations(self):
        self.orders._compute_mrp_production_ids()
        for production in self.productions:
            matching = self.orders.filtered(
                lambda order, mo=production: mo in order.mrp_production_ids
            )
            for operator in ("=", "!=", "in", "not in"):
                with self.subTest(production=production.name, operator=operator):
                    value = [production.id] if "in" in operator else production.id
                    expected = (
                        matching if operator in ("=", "in") else self.orders - matching
                    )
                    self._assert_search(operator, value, expected)

    def test_multiple_ids(self):
        targets = self.productions[1:2] | self.productions[3:5]
        matching = self.group_order | self.move_order | self.mixed_order
        self._assert_search("in", targets.ids, matching)
        self._assert_search("not in", targets.ids, self.orders - matching)
        self._assert_search("in", [False, self.productions[4].id], self.mixed_order)
        self._assert_search(
            "not in", [False, self.productions[4].id], self.orders - self.mixed_order
        )

    def test_empty_relations(self):
        empty = self.empty_order | self.empty_group_order
        self._assert_search("=", False, empty)
        self._assert_search("!=", False, self.orders - empty)

    def test_empty_and_missing_ids(self):
        for ids in ([], [False], [max(self.productions.ids) + 1000]):
            with self.subTest(ids=ids):
                self._assert_search("in", ids, self.env["sale.order"])
                self._assert_search("not in", ids, self.orders)

    def test_names(self):
        for operator, value, matching in (
            ("=", "LINK/LINE", self.line_order),
            ("ilike", "link/", self.orders[2:]),
            ("like", "LINK/", self.orders[2:]),
            ("=like", "LINK/SIBLING", self.move_order),
            ("=ilike", "link/sibling", self.move_order),
            ("ilike", "MIXED", self.mixed_order),
            ("ilike", "NONEXISTENT", self.env["sale.order"]),
        ):
            with self.subTest(operator=operator, value=value):
                self._assert_search(operator, value, matching)
                if operator in ("=", "like", "ilike"):
                    negative = {
                        "=": "!=",
                        "like": "not like",
                        "ilike": "not ilike",
                    }[operator]
                    self._assert_search(negative, value, self.orders - matching)

    def test_domain_and_dotted_search(self):
        self._assert_search("any", [("name", "=", "LINK/SIBLING")], self.move_order)
        self._assert_search(
            "not any", [("name", "=", "LINK/SIBLING")], self.orders - self.move_order
        )
        result = self.env["sale.order"].search(
            [
                ("id", "in", self.orders.ids),
                ("mrp_production_ids.name", "=", "LINK/SIBLING"),
            ]
        )
        self.assertEqual(result, self.move_order)

    def test_optional_equality(self):
        self._assert_search("=?", False, self.orders)
        self._assert_search("=?", self.productions[0].id, self.line_order)

    def test_unsupported_operator(self):
        with self.assertRaisesRegex(ValueError, "Unsupported operator"):
            self.env["sale.order"]._search_mrp_production_ids(
                "unsupported", self.productions[0].id
            )
