# Copyright 2022 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.addons.mrp_production_demo.tests.common_data import TestProductionData
from odoo.tests import Form
from odoo import fields
from odoo.tools.date_utils import relativedelta


class TestSaleStockMrpProduceDelay(TestProductionData):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env.ref('base.res_partner_2')
        cls.product = cls.env['product.product'].create({
            'name': 'New product',
            'type': 'product',
        })
        cls.product.write({
            'seller_ids': [
                (0, 0, {
                    'name': cls.env.ref('base.res_partner_3').id,
                    'price': 5.0,
                    'min_qty': 0.0,
                    'sequence': 1,
                    'date_start': fields.Date.today() - relativedelta(days=100),
                    'delay': 28,
                }),
            ]
        })
        cls.subproduct_1_1.write({
            'seller_ids': [
                (0, 0, {
                    'name': cls.env.ref('base.res_partner_3').id,
                    'price': 5.0,
                    'min_qty': 0.0,
                    'sequence': 1,
                    'date_start': fields.Date.today() - relativedelta(days=100),
                    'delay': 28,
                }),
            ]
        })
        cls.subproduct_2_1.write({
            'seller_ids': [
                (0, 0, {
                    'name': cls.env.ref('base.res_partner_3').id,
                    'price': 5.0,
                    'min_qty': 0.0,
                    'sequence': 1,
                    'date_start': fields.Date.today() - relativedelta(days=100),
                    'delay': 35,
                }),
            ]
        })

    def _create_sale_order_line(self, order, product, qty, commitment_date=False):
        vals = {
            'order_id': order.id,
            'product_id': product.id,
            'product_uom_qty': qty,
            'price_unit': 100,
            }
        if commitment_date:
            vals.update({
                'commitment_date': fields.Datetime.now()
            })
        line = self.env['sale.order.line'].create(vals)
        line.product_id_change()
        line._convert_to_write(line._cache)
        return line

    def _create_purchase_order_line(self, order, product, qty, date_planned=False):
        vals = {
            'name': product.name,
            'order_id': order.id,
            'product_id': product.id,
            'product_uom': product.uom_po_id.id,
            'product_qty': qty,
            'price_unit': 100,
            }
        if date_planned:
            vals.update({
                'date_planned': date_planned
            })
        line = self.env['purchase.order.line'].create(vals)
        return line

    def test_00_available_info_product(self):
        # check product to purchase
        order1 = self.env['sale.order'].create({
            'partner_id': self.partner.id,
        })
        line1 = self._create_sale_order_line(order1, self.product, 5)
        order1.compute_dates()
        available_date = fields.Date.today() + relativedelta(days=28)
        self.assertEqual(line1.available_date, available_date)
        self.assertEqual(
            line1.available_dates_info,
            '└[COMP] [False] [QTY: 5.0] [TO PURCHASE] plannable date %s.' %
            available_date.strftime('%d/%m/%Y')
        )

    def test_01_available_info_product_mrp(self):
        # todo simulate a product with multiple child boms to show a "tree" of
        #  availability like
        #  product (stock): [available at date x | purchesable for date x]¹
        #  top product [MANUF] 3pc (bom): [available at date x | produceable at date x]²
        #    -> 2pc subproduct2 [MANUF 1-2] * 3 = 6pc (bom): ²
        #       -> 3pc subproduct_1_1 [MANUF 1-1-1] * 3 = 18pc (stock) -> 28 days purch
        #       -> 4pc subproduct_2_1 [MANUF 1-2-1] * 3 = 24pc (stock) -> 35 days purch
        #    -> 5pc subproduct1 [MANUF 1-1] * 3 = 15pc (bom): ¹
        #       -> 2pc subproduct_1_1 [MANUF 1-1-1] * 3 = 30pc (stock) -> 28 days purch

        # set all products unavailable to reset prior tests
        def set_product_unavailable(product):
            for prod in product.bom_ids.mapped('bom_line_ids.product_id'):
                if prod.bom_ids:
                    set_product_unavailable(prod)
                else:
                    prod.virtual_available = 0.0

        set_product_unavailable(self.top_product)

        order1 = self.env['sale.order'].create({
            'partner_id': self.partner.id,
        })
        line1 = self._create_sale_order_line(order1, self.top_product, 3)
        order1.compute_dates()
        available_date = fields.Date.today() + relativedelta(days=35)
        available_date1 = fields.Date.today() + relativedelta(days=28)
        self.assertEqual(line1.available_date, available_date)
        # all product are un-available, so info display all at the produce-purchase date
        self.assertEqual(
            line1.available_dates_info,
            "[BOM] [MANUF] [QTY: 3.0] [TO PRODUCE] plannable date %s.\n"
            "─[BOM] [MANUF 1-2] [QTY: 6.0] [TO PRODUCE] plannable date %s.\n"
            "─└[COMP] [MANUF 1-1-1] [QTY: 18.0] [TO PURCHASE] plannable date %s.\n"
            "─└[COMP] [MANUF 1-2-1] [QTY: 24.0] [TO PURCHASE] plannable date %s.\n"
            "─[BOM] [MANUF 1-1] [QTY: 15.0] [TO PRODUCE] plannable date %s.\n"
            "─└[COMP] [MANUF 1-1-1] [QTY: 30.0] [TO PURCHASE] plannable date %s."
            % (
                available_date.strftime('%d/%m/%Y'),
                available_date.strftime('%d/%m/%Y'),
                available_date1.strftime('%d/%m/%Y'),
                available_date.strftime('%d/%m/%Y'),
                available_date1.strftime('%d/%m/%Y'),
                available_date1.strftime('%d/%m/%Y'),
            )
        )
        # subbom1: 3*5*2 subproduct_1_1 = 30 -> 2 in stock, 25 incoming on 28-5 days (so
        # before the purchase delay), 30+18 needed
        # subbom2: 3*2*3 subproduct_1_1 = 18 -> see above
        #          3*2*4 subproduct_2_1 = 24 -> 0 in stock,  incoming on  days (so
        # before the purchase delay),  needed
        purchase_order1 = self.env['purchase.order'].create({
            'partner_id': self.partner.id,
        })
        purchase_planned_date = fields.Datetime.now() + relativedelta(
                days=self.subproduct_1_1.purchase_delay - 5)
        purchase_line1 = self._create_purchase_order_line(
            purchase_order1, self.subproduct_1_1, 18, purchase_planned_date)
        purchase_order1.button_confirm()
        picking = purchase_order1.picking_ids[0]
        self.assertEqual(picking.move_lines[0].product_id, self.subproduct_1_1)
        self.assertAlmostEqual(picking.move_lines[0].product_qty, 18)
        self.assertAlmostEqual(
            self.subproduct_1_1.virtual_available, 18
        )
        self.assertEqual(
            self.subproduct_1_1.with_context(
                to_date=fields.Date.today()
            ).virtual_available_at_date_expected,
            0
        )
        self.assertEqual(
            self.subproduct_1_1.with_context(
                to_date=purchase_planned_date
            ).virtual_available_at_date_expected,
            18
        )
        # MANUF 1-1-1 is incoming so disappear, as bom MANUF 1-1
        # FIXME qty available are checked for every single line, e.g. a 30 qty available
        #  is sufficient for every lower request, so request for 18 and 30 are all
        #  satisfied
        order1.compute_dates()
        self.assertEqual(
            line1.available_dates_info,
            "[BOM] [MANUF] [QTY: 3.0] [TO PRODUCE] plannable date %s.\n"
            "─[BOM] [MANUF 1-2] [QTY: 6.0] [TO PRODUCE] plannable date %s.\n"
            "─└[COMP] [MANUF 1-2-1] [QTY: 24.0] [TO PURCHASE] plannable date %s.\n"
            "─[BOM] [MANUF 1-1] [QTY: 15.0] [TO PRODUCE] plannable date %s.\n"
            "─└[COMP] [MANUF 1-1-1] [QTY: 30.0] [TO PURCHASE] plannable date %s."
            % (
                available_date.strftime('%d/%m/%Y'),
                available_date.strftime('%d/%m/%Y'),
                available_date.strftime('%d/%m/%Y'),
                available_date1.strftime('%d/%m/%Y'),
                available_date1.strftime('%d/%m/%Y'),
            )
        )
        # now we have:
        # 3 sold top_product in mo confirmed: they are shown in quantity as -3
        # components of 3 top product:
        # 5pc subproduct1 * 3 = 15
        #   2pc subproduct_1_1 * 15 = 30
        # 2pc subproduct2 * 3 = 6
        #   4pc subproduct_2_1 * 6 =  24
        #   3pc subproduct_1_1 * 6 =  18
        # total                       72
        # NOT visible as not in this order product1
        # 2 offered top_product: they are shown in quantity as              -2
        # total top_products                                                -5
        order1.action_confirm()
        # now we have outgoing stock.move and mo to be produced             +3
        self.assertEqual(order1.state, 'sale')
        self.production = self.env['mrp.production'].search(
            [('origin', '=', order1.name)])

        self.production.action_assign()
        produce_form = Form(self.env['mrp.product.produce'].with_context(
                active_id=self.production.id,
                active_ids=[self.production.id],
            ))
        produce_form.product_qty = 2.0
        wizard = produce_form.save()
        wizard.do_produce()
        self.assertEqual(len(self.production), 1)

    # def test_negative_forecast_product(self):
    #     order1 = self.env['sale.order'].create({
    #         'partner_id': self.partner.id,
    #     })
    #     self._update_product_qty(
    #         self.product, order1.warehouse_id.in_type_id.default_location_dest_id, 10)
    #     self._create_sale_order_line(order1, self.product, 15)
    #     # forecast = self.get_forecast(order1)
    #     # self.assertFalse(forecast)
    #     # set commitment date to view forecast
    #     order1.commitment_date = fields.Datetime.now()
    #     forecast = self.get_forecast(order1)
    #     self.assertEqual(forecast[0].get('product_id')[0], self.product.id)
    #     self.assertAlmostEqual(forecast[0].get('quantity'), -5)
    #     order2 = self.env['sale.order'].create({
    #         'partner_id': self.partner.id,
    #         'commitment_date': fields.Datetime.now(),
    #     })
    #     self._create_sale_order_line(order2, self.product, 10)
    #     forecast1 = self.get_forecast(order2)
    #     self.assertAlmostEqual(forecast1[0].get('quantity'), -15)
    #     order1.action_confirm()
