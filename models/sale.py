# Copyright (C) 2013 Stefano Siccardi creativiquadrati snc
# Copyright 2020 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api
from dateutil.relativedelta import relativedelta

TOPROCESS = 'to_process'
NOT_EVALUATED = 'to_evaluate'
PRODUCTION_NOT_EVALUATED = 'to_evaluate_production'
MISSING_COMPONENTS_PRODUCE = 'to_produce'
MISSING_COMPONENTS_BUY = 'to_receive'
PRODUCTION_PLANNED = 'production_planned'
PRODUCTION_READY = 'production_ready'
PRODUCTION_STARTED = 'production_started'
WAITING_FOR_PACKING = 'to_pack'
SUBMANUFACTURE_STARTED = 'submanufacture_started'
SUBMANUFACTURE_DONE = 'submanufacture_done'
TEST_CHECK = 'test_check'
DONE = 'production_done'
DELIVERY_READY = 'delivery_ready'
DONE_DELIVERY = 'delivery_done'
AVAILABLEREADY = 'available'
PARTIALLYDELIVERED = 'partially_delivered'
INVOICED = 'invoiced'
SHIPPED = 'shipped'


class SaleOrder(models.Model):
    _inherit = "sale.order"

    STATES = [
        ('to_process', 'BLOCKED - to process'),
        ('to_evaluate', 'BLOCKED - to procure'),
        ('to_evaluate_production', 'BLOCKED - to process production'),
        ('to_produce', 'WAIT MATERIAL manufacture'),
        ('to_receive', 'WAIT MATERIAL'),
        ('production_planned', 'WAIT MANUFACTURE'),
        ('production_ready', 'TO DO'),
        ('production_started', 'IN ASSEMBLY'),
        ('to_pack', 'TO PACK'),
        ('submanufacture_started', 'Submanufacture started'),  # in assembl. esterno
        ('submanufacture_done', 'Submanufacture done'),  # tornate da assemblesterno
        ('test_check', 'Test check'),  # Prova collaudo
        ('delivery_ready', 'READY TO DELIVER'),  # PRONTE PER SPED
        ('production_done', 'Production done'),
        ('partially_delivered', 'Partially delivered'),
        ('delivery_done', 'Delivery done'),
        ('available', 'Available'),
        ('invoiced', 'Invoiced'),
        ('shipped', 'Shipped'),
    ]
    STATES_COLOR_INDEX_MAP = {
        'to_process': 301,
        'to_evaluate': 301,
        'to_evaluate_production': 301,
        'to_produce': 302,
        'to_receive': 302,
        'production_planned': 304,
        'production_ready': 308,
        'production_started': 306,
        'to_pack': 307,
        'submanufacture_started': 314,
        'submanufacture_done': 315,
        'test_check': 316,
        'delivery_ready': 317,
        'production_done': 305,
        'partially_delivered': 309,
        'delivery_done': 305,
        'available': 312,
        'invoiced': 313,
        'shipped': 312,
    }

    # to_process - to_evaluate - to_evaluate_production - production_planned -
    #  available - shipped - to_receive - WHITE 301
    # to_pack - YELLOW 308
    # partially_delivered - CYAN 309
    # production_started - PURPLE 304
    # production_done - delivery_done - BLACK 305
    # to_produce - production_ready - ORANGE 312
    # invoiced - GREEN 313

    # quando si crea l'ordine di vendita e quindi arriva in WHS automaticamente,
    # lo stato dell'SO deve essere 'da processare' (o 'disponibile'),
    # dunque di colore bianco - il magazzino lo vede in WHS ma non lo sta ancora
    # preparando, in attesa di miei comandi.
    #
    # Quando poi l'utente clicca su 'controlla disponibilità' e lo stato dell'OUT
    # passa a 'pronto', lo stato dell'SO deve passare a 'in preparazione a magazzino'
    # e prendere il colore giallo - il magazzino ha l'autorizzazione a prelevare
    # l'ordine (anche perché porto giù il foglio con la distinta di prelievo dell'OUT).
    #
    # Lo stato 'disponibile' evidenzia ordini per il quale materiale è appunto
    # disponibile, ma seguendo la logica di cui sopra, dovrebbe rimanere bianco,
    # in quanto sarebbe ancora da processare/stampare.
    #
    # Detto ciò, l'unico colore giallo deve essere dato allo stato SO
    # 'in preparazione a magazzino', tutto il resto rimane bianco.

    commitment_date = fields.Datetime(string='Scheduled Delivery Date')
    color = fields.Integer(compute='_get_color')
    calendar_state = fields.Selection(
        selection=STATES,
        default='to_process',
        required=True,
        compute='_compute_calendar_state',
        store=True,
        oldname='a_calendario')
    max_commitment_date = fields.Datetime(
        compute='_compute_max_commitment_date',
        inverse='_set_max_commitment_date',
        store=True,
        string='New Scheduled Delivery Date',
        oldname='last_agreed_delivery_date')
    delivery_week = fields.Integer(
        compute='_get_delivery_week',
        store=True)
    custom_production_qty = fields.Integer(
        compute='_compute_custom_production',
        store=True)

    @api.multi
    @api.depends('order_line.product_id.categ_id')
    def _compute_custom_production(self):
        custom_ctg_id = self.env['product.category'].search([
            ('name', '=', 'CUSTOM')
        ])
        for order in self:
            if any([
                x.product_id.categ_id == custom_ctg_id for x in order.order_line
            ]):
                order.custom_production_qty = sum([
                    x.product_qty for x in order.order_line.filtered(
                        lambda y: y.product_id.categ_id == custom_ctg_id
                    )
                ])
            else:
                order.custom_production_qty = 0

    @api.depends('commitment_date')
    def _get_delivery_week(self):
        for order in self:
            if not order.commitment_date:
                order.delivery_week = False
                continue
            order.delivery_week = order.commitment_date.isocalendar()[1]

    @api.multi
    def _set_max_commitment_date(self):
        for order in self:
            order.order_line.write({'commitment_date': order.max_commitment_date})

    @api.depends('order_line.commitment_date',
                 'commitment_date',
                 'confirmation_date')
    def _compute_max_commitment_date(self):
        for order in self.filtered(
                lambda x:
                x.commitment_date or
                x.confirmation_date or
                any(x.mapped('order_line.commitment_date'))):
            dates = []
            if order.commitment_date:
                dates.extend([order.commitment_date])
            if order.confirmation_date:
                dates.extend([order.confirmation_date])
            line_dates = order.order_line.filtered(
                lambda z: z.commitment_date
            ).mapped('commitment_date')
            if line_dates:
                dates.extend(line_dates)
            order.max_commitment_date = max(dates)

    @api.multi
    def _get_color(self):
        for order in self:
            color = order.STATES_COLOR_INDEX_MAP.get(order.calendar_state, 0)
            order.color = color * -1

    @api.onchange('order_line', 'commitment_date')
    def _onchange_commitment_date(self):
        if self.commitment_date or self.order_line.mapped('commitment_date'):
            # if not self.calendar_state:
            # and self.state not in ('draft', 'sent')
            # perchè c'era questo onchange solo in questi stati?
            max_commitment_date = self.max_commitment_date or self.commitment_date
            if max_commitment_date:
                calendar_state = self.get_forecast_calendar_state(
                    max_commitment_date=max_commitment_date)
                if calendar_state:
                    self.calendar_state = calendar_state

    def get_forecast_calendar_state(self, max_commitment_date=False):
        # Ordine dei vari stati calendar_state in base a quelli più importanti
        # esempio: se un ordine ha una produzione con stato PRODUCTION_STARTED
        # ed una con stato MISSING_COMPONENTS_BUY
        # l'ordine deve avere stato MISSING_COMPONENTS_BUY, perchè peggiore.
        cal_order = [
            TOPROCESS,
            NOT_EVALUATED,
            PRODUCTION_NOT_EVALUATED,
            MISSING_COMPONENTS_BUY,
            MISSING_COMPONENTS_PRODUCE,
            PRODUCTION_PLANNED,
            SUBMANUFACTURE_STARTED,
            SUBMANUFACTURE_DONE,
            TEST_CHECK,
            PRODUCTION_READY,
            PRODUCTION_STARTED,
            PARTIALLYDELIVERED,
            AVAILABLEREADY,
            WAITING_FOR_PACKING,
            DELIVERY_READY,
            DONE_DELIVERY,
            INVOICED,
            SHIPPED,
            DONE,
        ]
        calendar_state = False
        if self.procurement_group_id or self.order_line.mapped('procurement_group_id'):
            calendar_states = []
            procurement_group_ids = self.procurement_group_id
            procurement_group_ids |= self.order_line.mapped('procurement_group_id')
            for procurement_group in procurement_group_ids:
                states = self.forecast_procurement(
                    procurement_group, max_commitment_date)
                if states:
                    calendar_states += states
            if calendar_states:
                calendar_states = filter(None, calendar_states)
                calendar_state = min(
                    calendar_states, key=lambda x: cal_order.index(x[0]))[0]
        return calendar_state

    def forecast_procurement(self, procurement, max_commitment_date):
        calendar_states = []
        # group_id in stock.move
        picking_ids = self.env['stock.picking'].search([
            ('group_id', '=', procurement.id),
            ('state', '!=', 'cancel'),
        ])
        if picking_ids:
            calendar_state = []
            if all([x.state == 'done' for x in picking_ids]):
                calendar_state = DONE_DELIVERY
            elif all([x.state == 'assigned' for x in picking_ids]):
                if all([x.carrier_tracking_ref for x in picking_ids]):
                    calendar_state = DELIVERY_READY
                else:
                    calendar_state = WAITING_FOR_PACKING
            elif any([x.state == 'done' for x in picking_ids])\
                    and any([x.state != 'done' for x in picking_ids]):
                calendar_state = PARTIALLYDELIVERED
            if calendar_state:
                calendar_states.append((calendar_state, fields.Datetime.now()))
        # this is needed if picking are not done only i presume, tocheck
        # group_id in purchase.order
        purchase_line_ids = self.env['purchase.order.line'].search([
            ('procurement_group_id', '=', procurement.id),
            ('state', '!=', 'cancel'),
        ])
        if purchase_line_ids:
            for purchase_line in purchase_line_ids:
                if purchase_line.state == 'done':
                    calendar_states.append((WAITING_FOR_PACKING, fields.Datetime.now()))
                elif purchase_line.state == 'purchase':
                    # I think if we have not recieved the product yet, it should
                    # just return missing buy component. but I kept the old version
                    planned_date = max(
                        fields.Datetime.now(), purchase_line.order_id.date_planned)
                    if planned_date and max_commitment_date and \
                            planned_date > max_commitment_date:
                        calendar_states.append((MISSING_COMPONENTS_BUY, planned_date))
                    else:
                        # availableready is just a state i made to make a difference
                        # between buy and maufacture products
                        calendar_states.append((AVAILABLEREADY, fields.Datetime.now()))
        mrp_production_ids = self.env['mrp.production'].search([
            ('sale_id', '=', procurement.sale_id.id),
            ('state', '!=', 'cancel'),
        ])
        if mrp_production_ids:
            for mrp_production in mrp_production_ids:
                if mrp_production.state == 'done':
                    calendar_states.append((DONE, fields.Datetime.now()))
                elif mrp_production.state == 'confirmed':
                    if any([x for x in mrp_production.move_raw_ids
                            if x.state not in ['cancel', 'assigned']]):
                        datetime_planned = fields.Datetime.now() + relativedelta(
                            days=mrp_production.product_id.produce_delay)
                        calendar_states.append(
                            (MISSING_COMPONENTS_PRODUCE, datetime_planned)
                        )
                    elif mrp_production.date_planned_start >= fields.Datetime.now():
                        calendar_states.append(
                            (PRODUCTION_PLANNED, fields.Datetime.now())
                        )
                    else:
                        calendar_states.append(
                            (PRODUCTION_READY, fields.Datetime.now())
                        )
                elif mrp_production.state == 'planned':
                    calendar_states.append(
                        (PRODUCTION_PLANNED, fields.Datetime.now())
                    )
                elif mrp_production.state == 'progress':
                    calendar_states.append(
                        (PRODUCTION_STARTED, fields.Datetime.now())
                    )
                if mrp_production.additional_state:
                    calendar_states.append(
                        (mrp_production.additional_state, fields.Datetime.now())
                    )
        # check if all lines of type product or consu of so are invoiced
        if all([ol.qty_delivered == ol.qty_invoiced == ol.product_uom_qty for ol in
                self.order_line if ol.product_id
                and ol.product_id.type in ['product', 'consu']])\
                or self.invoice_status == 'invoiced' or self.force_invoiced:
            calendar_states = [(INVOICED, fields.Datetime.now())]
            # check if all invoices linked to SO have tracking_ref filled
            # DISABLED by direct request
            # if all([inv.carrier_tracking_ref for inv in self.invoice_ids]):
            #     calendar_states = [(SHIPPED, fields.Datetime.now())]
        if not (picking_ids or purchase_line_ids or mrp_production_ids):
            # ignore this procurement as it is cancelled
            return False
        if not calendar_states:
            calendar_states = [(TOPROCESS, fields.Datetime.now())]
        return calendar_states

    @api.depends('order_line', 'order_line.qty_invoiced',
                 'picking_ids', 'picking_ids.state', 'production_ids.additional_state')
    def _compute_calendar_state(self):
        for order in self:
            order.calendar_state = order.get_forecast_calendar_state() or \
                                   order.calendar_state or 'to_process'

    @api.multi
    def update_forecast_state(self):
        for order in self:
            calendar_state = order.get_forecast_calendar_state()
            if calendar_state:
                order.calendar_state = calendar_state

    def alert_customer_changed_delivery(self):
        """
        This function opens a window to compose an email,
        with the "changed delivery date" template opened by default.
        """
        self.ensure_one()
        template = self.env.ref(
            'sale_order_calendar_state.email_template_delivery_date_changed',
            raise_if_not_found=False)
        local_context = dict(
            default_model='sale.order',
            default_res_id=self.id,
            default_use_template=bool(template),
            default_template_id=template and template.id or False,
            default_composition_mode='comment',
            change_agreed_date=True,
        )
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'target': 'new',
            'context': local_context,
        }
