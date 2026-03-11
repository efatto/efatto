# Copyright 2026 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields
from odoo.tests import Form
from odoo.tests.common import SingleTransactionCase
from odoo.tools.date_utils import relativedelta


class TestProductObsolescenceManagement(SingleTransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.partner = cls.env.ref("base.res_partner_2")
        cls.supplier = cls.env["res.partner"].create(
            {
                "name": "Test Supplier",
                "supplier_rank": 1,
            }
        )
        # Create multiple suppliers
        cls.supplier2 = cls.env["res.partner"].create(
            {
                "name": "Test Supplier 2",
                "supplier_rank": 1,
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "product",
                "purchase_ok": True,
            }
        )
        cls.seller = cls.env["product.supplierinfo"].create(
            {
                "name": cls.supplier.id,
                "product_tmpl_id": cls.product.product_tmpl_id.id,
            }
        )
        cls.cron_obsolesence_id = cls.env.ref(
            "product_obsolescence_management.ir_cron_product_state"
        )

    def test_00_assign_product_state_create_min_qty(self):
        """Test that setting `is end of life` state for a product with sold quantities
        in state `sale` assign min qty"""
        order_form = Form(self.env["sale.order"])
        order_form.partner_id = self.partner
        with order_form.order_line.new() as line:
            line.product_id = self.product
            line.product_uom_qty = 30
            line.product_uom = self.product.uom_id
            line.price_unit = 100
            line.name = self.product.name
        sale_order = order_form.save()
        self.product.product_state_id.is_end_of_life = True
        self.cron_obsolesence_id.method_direct_trigger()
        self.assertEqual(
            self.product.min_stock_qty,
            0,
        )
        sale_order.action_confirm()
        self.assertEqual(sale_order.state, "sale")
        self.cron_obsolesence_id.method_direct_trigger()
        self.assertEqual(
            self.product.min_stock_qty,
            sale_order.order_line.product_uom_qty / 10,
        )

    def test_01_purchase_order_set_date_available(self):
        """Test that creating a purchase order will set the date available"""
        order_form = Form(self.env["purchase.order"])
        order_form.partner_id = self.supplier
        with order_form.order_line.new() as line:
            line.product_id = self.product
            line.product_qty = 30
            line.product_uom = self.product.uom_po_id
            line.price_unit = 100
            line.date_planned = fields.Date.today() + relativedelta(days=15)
        purchase_order = order_form.save()
        replacement_product_available_date = fields.first(
            purchase_order.order_line
        ).date_planned
        self.assertEqual(
            replacement_product_available_date.date(),
            fields.Date.today() + relativedelta(days=15),
        )
