from odoo.tests import Form

from odoo.addons.mrp_production_demo.tests.common_data import TestProductionData


class TestMrpFixPhantomInactiveBom(TestProductionData):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_00_mo(self):
        # Create an MO for top product
        mo_form = Form(self.production_model)
        mo_form.product_id = self.top_product
        mo_form.bom_id = self.main_bom
        mo_form.product_qty = 1
        mo = mo_form.save()
        mo.action_confirm()
        self.assertRecordValues(
            mo.move_raw_ids,
            [
                {"product_id": self.subproduct_1_1.id},
                {"product_id": self.subproduct_2_1.id},
                {"product_id": self.sub_bom_phantom_1.bom_line_ids.product_id.id},
            ],
        )

    def test_01_mo_with_inactive_product_and_bom(self):
        # Create an MO for top product with inactive product and bom
        self.sub_bom_phantom_2.product_tmpl_id.product_variant_id.active = False
        self.sub_bom_phantom_2.active = False
        mo_form = Form(self.production_model)
        mo_form.product_id = self.top_product
        mo_form.bom_id = self.main_bom
        mo_form.product_qty = 1
        mo = mo_form.save()
        mo.action_confirm()
        self.assertRecordValues(
            mo.move_raw_ids,
            [
                {"product_id": self.subproduct_1_1.id},
                {"product_id": self.subproduct_2_1.id},
                {"product_id": self.sub_bom_phantom_1.bom_line_ids.product_id.id},
            ],
        )
