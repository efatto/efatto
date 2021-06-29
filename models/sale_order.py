# Copyright 2020 Tecnativa - Ernesto Tejeda
# Copyright 2021 Sergio Corato <https://github.com/sergiocorato>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from collections import defaultdict
from datetime import timedelta

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.depends('product_id', 'customer_lead', 'product_uom_qty', 'commitment_date',
                 'order_id.warehouse_id', 'order_id.commitment_date',
                 'product_id.produce_delay', 'product_id.purchase_delay',
                 'product_id.sale_delay')
    def _compute_qty_at_date(self):
        """ Based on _compute_free_qty method of sale.order.line
            model in Odoo v13 'sale_stock' module.
        """
        #  we expose the first date in which the products are really
        #  available from stock to customer
        super()._compute_qty_at_date()
        qty_processed_per_product = defaultdict(lambda: 0)
        grouped_lines = defaultdict(lambda: self.env['sale.order.line'])
        now = fields.Datetime.now()
        for line in self.sorted(key=lambda r: r.sequence):
            # check if this for is needed or superseeded by sql query
            if not line.display_qty_widget:
                continue
            line.warehouse_id = line.order_id.warehouse_id
            if line.commitment_date:
                date = line.commitment_date
            elif line.order_id.commitment_date:
                date = line.order_id.commitment_date
            else:
                if line.order_id.state in ['sale', 'done']:
                    confirm_date = line.order_id.confirmation_date
                else:
                    confirm_date = now
                date = confirm_date + timedelta(line.customer_lead or 0.0)
            grouped_lines[(line.warehouse_id.id, date)] |= line
        treated = self.browse()
        for (warehouse, scheduled_date), lines in grouped_lines.items():
            for line in lines:
                # todo aggiungere le vendite sent con data di impegno come nell'altro
                self._cr.execute("""
                SELECT
                    sub.date,
                    sub.product_id,
                    sub.child_product_id,
                    SUM(sub.quantity) AS quantity,
                    CASE WHEN MIN(sub.name) = 'B - Stock'
                    THEN
                    SUM(SUM(sub.quantity))
                    OVER (PARTITION BY sub.child_product_id ORDER BY sub.date)
                    ELSE NULL
                    END
                    AS cumulative_quantity
                FROM
                (
                SELECT 
                    to_char(date, 'YYYY-MM-DD') as date,
                    'B - Stock' AS name,
                    product_id as product_id,
                    product_id as child_product_id,
                    sum(product_qty) AS quantity,
                    company_id
                FROM 
                    (SELECT
                    MIN(id) as id,
                    MAIN.product_id as product_id,
                    SUB.date as date,
                    CASE WHEN MAIN.date = SUB.date 
                        THEN sum(MAIN.product_qty) ELSE 0 END as product_qty,
                    MAIN.company_id as company_id
                    FROM
                        (SELECT
                            MIN(sq.id) as id,
                            sq.product_id,
                            CURRENT_DATE as date,
                            SUM(sq.quantity) AS product_qty,
                            sq.company_id
                            FROM
                            stock_quant as sq
                            LEFT JOIN
                            product_product ON product_product.id = sq.product_id
                            LEFT JOIN
                            stock_location location_id ON sq.location_id = location_id.id
                            WHERE
                            location_id.usage = 'internal'
                            GROUP BY date, sq.product_id, sq.company_id
                            UNION ALL
                            SELECT
                            MIN(-sm.id) as id,
                            sm.product_id,
                            CASE WHEN sm.date_expected > CURRENT_DATE
                            THEN sm.date_expected
                            ELSE CURRENT_DATE END
                            AS date,
                            SUM(sm.product_qty) AS product_qty,
                            sm.company_id
                            FROM
                               stock_move as sm
                            LEFT JOIN
                               product_product ON product_product.id = sm.product_id
                            LEFT JOIN
                            stock_location dest_location ON sm.location_dest_id = dest_location.id
                            LEFT JOIN
                            stock_location source_location ON sm.location_id = source_location.id
                            WHERE
                            sm.state IN ('confirmed','partially_available','assigned','waiting') and
                            source_location.usage != 'internal' and dest_location.usage = 'internal'
                            GROUP BY sm.date_expected, sm.product_id, sm.company_id
                            UNION ALL
                            SELECT
                                MIN(-sm.id) as id,
                                sm.product_id,
                                CASE WHEN sm.date_expected > CURRENT_DATE
                                    THEN sm.date_expected
                                    ELSE CURRENT_DATE END
                                AS date,
                                SUM(-(sm.product_qty)) AS product_qty,
                                sm.company_id
                            FROM
                               stock_move as sm
                            LEFT JOIN
                               product_product ON product_product.id = sm.product_id
                            LEFT JOIN
                               stock_location source_location ON sm.location_id = source_location.id
                            LEFT JOIN
                               stock_location dest_location ON sm.location_dest_id = dest_location.id
                            WHERE
                                sm.state IN ('confirmed','partially_available','assigned','waiting') and
                            source_location.usage = 'internal' and dest_location.usage != 'internal'
                            GROUP BY sm.date_expected,sm.product_id, sm.company_id)
                         as MAIN
                         LEFT JOIN
                         (SELECT DISTINCT date
                          FROM
                          (
                             SELECT CURRENT_DATE AS DATE
                             UNION ALL
                             SELECT sm.date_expected AS date
                             FROM stock_move sm
                             LEFT JOIN
                             stock_location source_location ON sm.location_id = source_location.id
                             LEFT JOIN
                             stock_location dest_location ON sm.location_dest_id = dest_location.id
                             WHERE
                             sm.state IN ('confirmed','assigned','waiting')
                             and sm.date_expected > CURRENT_DATE
                             and ((dest_location.usage = 'internal' 
                             AND source_location.usage != 'internal')
                              or (source_location.usage = 'internal' 
                             AND dest_location.usage != 'internal'))) AS DATE_SEARCH)
                             SUB ON (SUB.date IS NOT NULL)
                        GROUP BY MAIN.product_id,SUB.date, MAIN.date, MAIN.company_id
                        ) AS FINAL
                    WHERE product_qty != 0 AND product_id = %s
                    GROUP BY product_id, date, company_id
                    ) AS sub
                    GROUP BY product_id, child_product_id, date
                """, (line.product_id.id, ))
                res = self._cr.dictfetchall()
                # dates on which availability is enough for requested qty
                candidate_availables = [
                    x for x in res if x['cumulative_quantity'] > line.product_uom_qty]
                # se ci sono date successive con quantità negativa, non è disponibile
                availables = []
                for candidate_available in candidate_availables:
                    not_available = [
                        x for x in res if
                        x['cumulative_quantity'] < line.product_uom_qty
                        and x['date'] >= candidate_available['date']
                    ]
                    if not_available:
                        continue
                    availables.append(candidate_available)
                if availables:
                    scheduled_date = fields.Datetime.from_string(availables[0]['date'])
                product = line.product_id.with_context(
                    to_date=scheduled_date, warehouse=warehouse)
                qty_available = product.qty_available
                free_qty = product.free_qty
                virtual_available = product.virtual_available
                qty_processed = qty_processed_per_product[product.id]
                line.scheduled_date = scheduled_date
                line.qty_available_today = qty_available - qty_processed
                line.free_qty_today = free_qty - qty_processed
                virtual_available_at_date = virtual_available - qty_processed
                line.virtual_available_at_date = virtual_available_at_date
                qty_processed_per_product[product.id] += line.product_uom_qty
            treated |= lines
        remaining = (self - treated)
        remaining.write({
            "virtual_available_at_date": False,
            "scheduled_date": False,
            "free_qty_today": False,
            "qty_available_today": False,
            "warehouse_id": False,
        })
