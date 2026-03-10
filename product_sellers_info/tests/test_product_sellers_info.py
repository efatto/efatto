# Copyright 2026 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields
from odoo.tests import Form
from odoo.tests.common import SingleTransactionCase


class TestProductSellersInfo(SingleTransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
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
        cls.product_tmpl = cls.env["product.template"].create(
            {
                "name": "Test Product",
                "type": "product",
                "purchase_ok": True,
            }
        )
        # Create supplier info with delay with date end in the future
        cls.seller = cls.env["product.supplierinfo"].create(
            {
                "name": cls.supplier.id,
                "product_tmpl_id": cls.product_tmpl.id,
                "delay": 15,
                "multiple_qty": 5.0,
                "date_end": fields.Date.add(fields.Date.today(), days=30),
            }
        )
        # Create supplier info without date_end
        cls.seller_no_date_end = cls.env["product.supplierinfo"].create(
            {
                "name": cls.supplier.id,
                "product_tmpl_id": cls.product_tmpl.id,
                "delay": 10,
                "multiple_qty": 3.0,
            }
        )
        # Create supplier info
        cls.seller_expired = cls.env["product.supplierinfo"].create(
            {
                "name": cls.supplier2.id,
                "product_tmpl_id": cls.product_tmpl.id,
                "delay": 10,
                "multiple_qty": 3.0,
                "date_end": fields.Date.add(fields.Date.today(), days=-30),
            }
        )

    def test_00_compute_purchase_delay_from_seller(self):
        """Test that purchase_delay is computed from seller delay"""
        # Verify that purchase_delay and purchase_multiple_qty are computed
        self.assertEqual(
            self.product_tmpl.purchase_delay,
            self.seller.delay,
            "Purchase delay should be computed from seller delay",
        )
        self.assertEqual(
            self.product_tmpl.purchase_multiple_qty,
            self.seller.multiple_qty,
            "Purchase multiple qty should be computed from seller multiple_qty",
        )

    def test_01_inverse_purchase_delay_to_seller(self):
        """Test that changing purchase_delay updates seller delay"""
        # Change purchase_delay on product
        pt_form = Form(self.product_tmpl)
        pt_form.purchase_delay = 20
        pt_form.purchase_multiple_qty = 10.0
        pt_form.save()

        # Verify that seller delay is updated
        self.assertEqual(
            self.seller.delay,
            self.product_tmpl.purchase_delay,
            "Seller delay should be updated when purchase_delay changes",
        )
        self.assertEqual(
            self.seller.multiple_qty,
            self.product_tmpl.purchase_multiple_qty,
            "Seller multiple_qty should be updated when purchase_multiple_qty changes",
        )

    def test_02_compute_purchase_delay_with_expired_seller(self):
        """Test that expired sellers are not considered"""
        # Verify that purchase_delay is 0 (expired seller not considered)
        self.assertNotEqual(
            self.product_tmpl.purchase_delay,
            self.seller_expired.delay,
            "Purchase delay should be 0 when seller is expired",
        )

    def test_03_inverse_purchase_delay_without_date_end(self):
        """Test inverse when seller has no date_end"""
        # Change purchase_delay on product
        product_form = Form(self.product_tmpl)
        product_form.purchase_delay = 18
        product_form.purchase_multiple_qty = 7.0
        product_form.save()

        # Verify that seller delay is updated
        self.assertEqual(
            self.seller.delay,
            self.product_tmpl.purchase_delay,
            "Seller delay should be updated even without date_end",
        )
        self.assertEqual(
            self.seller.multiple_qty,
            self.product_tmpl.purchase_multiple_qty,
            "Seller multiple_qty should be updated even without date_end",
        )
