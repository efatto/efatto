# Copyright 2020 Tecnativa - Ernesto Tejeda
# Copyright 2021 Sergio Corato <https://github.com/sergiocorato>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from collections import defaultdict
from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.date_utils import relativedelta


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    virtual_available_at_date = fields.Float(
        compute='_compute_stock_qty_at_date', store=True)
    scheduled_date = fields.Datetime(
        compute='_compute_stock_qty_at_date', store=True)
    free_qty_today = fields.Float(
        compute='_compute_stock_qty_at_date', store=True)
    qty_available_today = fields.Float(
        compute='_compute_stock_qty_at_date', store=True)
    warehouse_id = fields.Many2one(
        'stock.warehouse', compute='_compute_stock_qty_at_date', store=True)
    qty_to_deliver = fields.Float(store=True)
    is_mto = fields.Boolean(store=True)
    display_qty_widget = fields.Boolean(store=True)
    available_date = fields.Date()
    last_available_date_compute = fields.Datetime()
    available_dates_info = fields.Text()
    predicted_arrival_late = fields.Boolean()
    late_product_ids = fields.Many2many('product.product')

    @api.depends('product_id', 'product_uom_qty', 'qty_delivered', 'state',
                 'commitment_date', 'order_id.commitment_date')
    def _compute_qty_to_deliver(self):
        """ Based on _compute_qty_to_deliver method of sale.order.line
            model in Odoo v13 'sale_stock' module.
        """
        for line in self:
            line.qty_to_deliver = line.product_uom_qty - line.qty_delivered
            line.display_qty_widget = (line.state == 'draft'
                                       and not line.commitment_date
                                       and not line.order_id.commitment_date
                                       and line.product_type == 'product'
                                       and line.qty_to_deliver > 0)

    @api.depends('product_id', 'product_uom_qty', 'commitment_date')
    def _compute_stock_qty_at_date(self):
        """ Based on _compute_free_qty method of sale.order.line
            model in Odoo v13 'sale_stock' module.
        """
        #  we expose the first date in which the products are really
        #  available from stock to customer
        # do not do super() as this override other logic and consume time
        # storing fields will not recall this method on all record at every change
        # consumed components are already computed by stock
        # do not consider manufacturing products
        qty_processed_per_product = defaultdict(lambda: 0)
        for line in self.sorted(key=lambda r: r.sequence):
            if not line.product_id:
                continue
            line.warehouse_id = line.order_id.warehouse_id
            self._cr.execute("""
            SELECT
                sub.date,
                sub.product_id,
                sub.child_product_id,
                SUM(sub.quantity) AS quantity,
                SUM(SUM(sub.quantity))
                OVER (PARTITION BY sub.child_product_id ORDER BY sub.date)
                AS cumulative_quantity
            FROM
            (
            SELECT
                min(l.id) AS id,
                s.id AS order_id,
                'A - Sale' AS name,
                l.product_id AS product_id,
                l.product_id AS child_product_id,
                CASE WHEN l.commitment_date IS NOT NULL
                THEN to_char(l.commitment_date, 'YYYY-MM-DD')
                ELSE to_char(s.commitment_date, 'YYYY-MM-DD') END
                AS date,
                sum(l.product_uom_qty / u.factor * u2.factor) * -1 as quantity,
                s.company_id as company_id
            FROM
                sale_order_line l
                  join sale_order s on (l.order_id=s.id)
                  join res_partner partner on s.partner_id = partner.id
                    left join product_product p on (l.product_id=p.id)
                        left join product_template t on (p.product_tmpl_id=t.id)
                left join uom_uom u on (u.id=l.product_uom)
                left join uom_uom u2 on (u2.id=t.uom_id)
            WHERE
                s.state IN ('draft', 'sent')
                AND s.active = 't'
                AND (s.commitment_date IS NOT NULL OR l.commitment_date IS NOT NULL)
                AND l.product_id = %s
            GROUP BY
                l.product_id,
                l.order_id,
                t.uom_id,
                l.commitment_date,
                s.company_id,
                s.id
            UNION SELECT
                MIN(id) as id,
                null as order_id,
                'B - Stock' AS name,
                product_id as product_id,
                product_id as child_product_id,
                to_char(date, 'YYYY-MM-DD') as date,
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
            """, (line.product_id.id, line.product_id.id,))
            res = self._cr.dictfetchall()
            # adapt available qty if current SO line has a commitment date, to avoid
            # double computation (1 in query ad another 1 in code)
            fix_qty = line.product_uom_qty if (
                line.commitment_date or line.order_id.commitment_date) else 0.0
            # dates on which availability is enough for requested qty
            candidate_availables = [
                x for x in res if x['cumulative_quantity'] >= line.product_uom_qty]
            # se ci sono date successive con quantità negativa, non è disponibile
            availables = []
            for candidate_available in candidate_availables:
                not_available = [
                    x for x in res if
                    (x['cumulative_quantity'] + fix_qty) < line.product_uom_qty
                    and x['date'] >= candidate_available['date']
                ]
                if not_available:
                    continue
                availables.append(candidate_available)
            lower_available_qty = 0
            if availables:
                # check if this move, available in a certain date, will remove product
                # reserved for future, so stock will become negative
                lower_available_qty = availables[0]['cumulative_quantity']
                for available in availables:
                    if available['cumulative_quantity'] < lower_available_qty:
                        lower_available_qty = available['cumulative_quantity']
                if lower_available_qty < line.product_uom_qty:
                    availables = []
            if availables:
                # there are multiple available dates: get the lower qty
                availables.sort(key=lambda self: self['cumulative_quantity'])
                available = availables[0]
                # show the first available date
                availables.sort(key=lambda self: self['date'])
                available_date = availables[0]
                scheduled_date = fields.Datetime.from_string(available_date['date'])
                # product = line.product_id.with_context(
                #     to_date=scheduled_date, warehouse=line.warehouse_id.id)
                # qty_available = available['cumulative_quantity']
                # free_qty = product.free_qty
                # show the lower quantity available
                virtual_available = available['cumulative_quantity']
                qty_processed = qty_processed_per_product[line.product_id.id]
                line.scheduled_date = scheduled_date
                line.qty_available_today = 0
                line.free_qty_today = available['cumulative_quantity']
                virtual_available_at_date = virtual_available - qty_processed
                line.virtual_available_at_date = virtual_available_at_date
                qty_processed_per_product[line.product_id.id] += line.product_uom_qty
            else:
                line.virtual_available_at_date = lower_available_qty
                line.scheduled_date = line.commitment_date\
                    and line.commitment_date + timedelta(days=1)\
                    or fields.Datetime.now()
                line.free_qty_today = 0
                line.qty_available_today = 0

    def get_available_date(self, product_id, qty, date_start, available_date=False,
                           level=0):
        commitment_date = self.commitment_date and self.commitment_date.date() \
            or self.order_id.commitment_date and self.order_id.commitment_date.date() \
            or self.order_id.date_order and self.order_id.date_order.date()
        child = "└"
        child_multi = "├"
        vertical = "─"
        stock_available_date = False
        available_info = []
        available_dates_info = ''
        domain_quant_loc, domain_move_in_loc, domain_move_out_loc = \
            product_id._get_domain_locations()
        incoming_stock_moves = self.env['stock.move'].search([
            ('product_id', '=', product_id.id),
            ('product_uom_qty', '>', 0),
            ('state', 'not in', ['done', 'cancel']),
            ('date', '>=', commitment_date),
        ] + domain_move_in_loc)
        reserved_stock_moves = self.env['stock.move'].search([
            ('product_id', '=', product_id.id),
            ('product_uom_qty', '>', 0),
            ('state', 'not in', ['done', 'cancel']),
            ('date', '>=', commitment_date),
        ] + domain_move_out_loc)
        for reserve_date in (
            [x.date() for x in reserved_stock_moves.mapped('date_expected')] +
            [y.date() for y in incoming_stock_moves.mapped('date_expected')] +
            [commitment_date]
        ):
            available_info.append({
                'info': 'Stock move',
                'date': reserve_date,
                'qty': product_id.with_context(
                    to_date=reserve_date
                ).virtual_available_at_date_expected
            })
        # FIXME when all dates has sufficient availability is ignored!
        # todo remove all availability with a previous availability with qty <
        #  requested qty, to prevent "steal" of goods from reserved moves
        #  get the available date later of the far available date with qty <
        if available_info:
            farther_unreservable_dates = [
                x['date'] for x in available_info if x['qty'] < qty
            ]
            if not farther_unreservable_dates:
                # all dates have a sufficient qty
                farther_unreservable_dates = [min([
                    x['date'] for x in available_info
                ])]
            if len(farther_unreservable_dates) == len(available_info):
                # None of the available dates meets the requested quantity
                stock_available_date = False
            elif farther_unreservable_dates:
                stock_available_date = min([
                    x['date'] for x in available_info if x['date']
                    >= max(farther_unreservable_dates) and
                    x['qty'] >= qty
                ] or [False])
        else:
            raise UserError('No available info found!')
        if product_id.bom_ids:
            # fixme need to filter boms?
            option = "TO PRODUCE"
            bom_id = product_id.bom_ids[0]
            avail_dates = []
            if stock_available_date:
                available_date = stock_available_date
                option = 'FROM STOCK'
                available_text = \
                    _('%s[BOM] [%s] [QTY: %s] [%s] plannable date %s.\n') % (
                        vertical * level,
                        product_id.default_code,
                        qty,
                        option,
                        available_date.strftime('%d/%m/%Y'),
                    )
            else:
                for bom_line in bom_id.bom_line_ids.sorted(
                        key=lambda x: x.product_id.bom_ids, reverse=True):
                    avail_date, avail_text = \
                        self.get_available_date(
                            bom_line.product_id,
                            qty * bom_line.product_qty,
                            date_start,
                            available_date,
                            level=level + 1)
                    if avail_date:
                        avail_dates.append(avail_date)
                    if avail_text and avail_text not in available_dates_info:
                        available_dates_info += avail_text
                if avail_dates:
                    available_date = max(avail_dates)
                    available_text = \
                        _('%s[BOM] [%s] [QTY: %s] [%s] plannable date %s.\n') % (
                            vertical * level,
                            product_id.default_code,
                            qty,
                            option,
                            available_date.strftime('%d/%m/%Y'),
                        )
                else:
                    available_text = \
                        _('%s[BOM] [%s] [QTY: %s] [%s] plannable date %s.\n') % (
                            vertical * level,
                            product_id.default_code,
                            qty,
                            option,
                            'Not found',
                        )
            if available_text and available_text not in available_dates_info:
                available_dates_info += available_text
            if bom_id.routing_id:
                delay = sum(bom_id.mapped(
                    'routing_id.operation_ids.time_cycle_manual') or [0]) / 1440
                available_date += relativedelta(days=int(delay))
        else:
            purchase_available_date = (
                fields.Date.today()
                + relativedelta(days=int(product_id.purchase_delay))
            )
            if stock_available_date and stock_available_date <= purchase_available_date:
                available_date = stock_available_date
                option = 'FROM STOCK'
                available_text = \
                    _('%s[COMP] [%s] [QTY: %s] [%s] plannable date %s.\n') % (
                        vertical * (level - 1) + child,
                        product_id.default_code,
                        qty,
                        option,
                        available_date.strftime('%d/%m/%Y'),
                    )
            else:
                # Check if ordering the product the incoming date will be sooneer
                option = 'TO PURCHASE'
                if not available_date or (
                        stock_available_date and
                        purchase_available_date < stock_available_date):
                    available_date = purchase_available_date
                else:
                    available_date = stock_available_date
                    option = 'FROM STOCK'
                available_text = \
                    _('%s[COMP] [%s] [QTY: %s] [%s] plannable date %s.\n') % (
                        vertical * (level - 1) + child,
                        product_id.default_code,
                        qty,
                        option,
                        available_date.strftime('%d/%m/%Y'),
                    )
            if available_text not in available_dates_info:
                available_dates_info += available_text
        return available_date, available_dates_info

    @api.multi
    def action_delayed_line(self):
        commitment_date_tz = fields.Datetime.context_timestamp(
            self, self.commitment_date or self.order_id.commitment_date or
            self.order_id.date_order)
        raise UserError(_(
            'This line is scheduled for: %s.\n'
            'However it is now planned to arrive for %s.\n %s') % (
                commitment_date_tz.strftime('%d/%m/%Y'),
                self.available_date.strftime('%d/%m/%Y'),
                self.available_dates_info,
            )
        )

    def open_view_stock_reserved(self):
        # use domain for late components
        res = super().open_view_stock_reserved()
        product = self.product_id if self.product_id.type != 'service' else False
        if product and product.qty_available < self.product_uom_qty \
                and product.bom_ids and self.late_product_ids:
            res['context'] = {'search_default_id': self.late_product_ids.ids}
        return res


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    available_date = fields.Date(
        help="First available date computed in date/hour of available_date_compute",
        compute='_compute_available_date', store=True)
    last_available_date_compute = fields.Datetime(
        compute='_compute_available_date', store=True)

    @api.multi
    @api.depends('order_line.available_date')
    def _compute_available_date(self):
        for order in self:
            available_dates = [
                x for x in order.order_line.mapped('available_date') if x]
            last_available_date_computes = [
                x for x in order.order_line.mapped('last_available_date_compute') if x]
            if available_dates:
                order.available_date = max(available_dates)
            else:
                order.available_date = False
            if last_available_date_computes:
                order.last_available_date_compute = max(last_available_date_computes)
            else:
                order.last_available_date_compute = False

    @api.multi
    def compute_dates(self):
        for line in self.order_line.sorted(key=lambda r: r.sequence):
            if not line.product_id:
                line.available_date = False
                line.available_dates_info = False
                line.predicted_arrival_late = False
                continue
            commitment_date = line.commitment_date and line.commitment_date.date() or \
                line.order_id.commitment_date and \
                line.order_id.commitment_date.date() or \
                line.order_id.date_order and line.order_id.date_order.date()
            avail_date, avail_date_info = \
                line.get_available_date(
                    line.product_id,
                    line.product_uom_qty,
                    commitment_date,
                )
            line.available_date = avail_date
            line.last_available_date_compute = fields.Datetime.now()
            dates_info = avail_date_info.split('\n')
            commitment_date_str = commitment_date.strftime('%d/%m/%Y')
            dates_info_clean = [x for x in dates_info if commitment_date_str not in x
                                and x != '']
            dates_info_clean.reverse()
            line.available_dates_info = '\n'.join([x for x in dates_info_clean])
            late_product_codes = [y.split('] [')[1] for y in dates_info_clean]
            line.late_product_ids = self.env['product.product'].search([
                ('default_code', 'in', late_product_codes)
            ]).ids
            predicted_arrival_late = False
            if line.available_date > commitment_date:
                predicted_arrival_late = True
            line.predicted_arrival_late = predicted_arrival_late
