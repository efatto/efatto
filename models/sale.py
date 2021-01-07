# Copyright (C) 2013 Stefano Siccardi creativiquadrati snc
# Copyright 2020 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api, _
from datetime import timedelta
from dateutil.relativedelta import relativedelta

TOPROCESS = 'to_process'
NOT_EVALUATED = 'to_evaluate'
PRODUCTION_NOT_EVALUATED = 'to_evaluate_production'
MISSING_COMPONENTS_PRODUCE = 'to_produce'
MISSING_COMPONENTS_BUY = 'to_receive'
PRODUCTION_READY = 'production_ready'  # EX production_ready_toproduce
PRODUCTION_STARTED = 'production_started'
WAITING_FOR_PACKING = 'to_pack'
DONE = 'production_done'
DONE_DELIVERY = 'delivery_done'
AVAILABLEREADY = 'available'
PARTIALLYDELIVERED = 'partially_delivered'
INVOICED = 'invoiced'
SHIPPED = 'shipped'


class SaleOrder(models.Model):
    _inherit = "sale.order"

    STATES = [
        ('to_process', 'To process'),
        ('to_evaluate', 'Some procurements not yet processed'),
        ('to_evaluate_production', 'Production not yet processed'),
        ('to_produce', 'Missing components to produce'),
        ('to_receive', 'Missing components to receive'),
        ('production_ready', 'Ready to produce'),
        ('production_started', 'Production started'),
        ('to_pack', 'Waiting for packing'),
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
        'to_produce': 301,
        'to_receive': 301,
        'production_ready': 301,
        'production_started': 301,
        'to_pack': 308,
        'production_done': 305,
        'partially_delivered': 309,
        'delivery_done': 305,
        'available': 301,
        'invoiced': 312,
        'shipped': 313,
    }

    # to_process - to_evaluate - to_evaluate_production - available - WHITE 301
    # to_produce - to_receive - production_ready - production_started - WHITE 301
    # to_pack - YELLOW 308
    # partially_delivered - CYAN 309
    # production_done - delivery_done - BLACK 305
    # invoiced - ORANGE 312
    # shipped - GREEN 313

    color = fields.Integer(compute='_get_color')
    revision = fields.Integer(default=1)
    calendar_state = fields.Selection(
        selection=STATES,
        default='to_process',
        required=True,
        compute='_compute_calendar_state',
        store=True,
        oldname='a_calendario')
    max_commitment_date = fields.Datetime(
        compute='_compute_max_commitment_date',
        store=True,
        oldname='last_agreed_delivery_date')
    delivery_week = fields.Integer(
        compute='_get_delivery_week',
        store=True)
        # inverse='_set_delivery_week',

    # @api.onchange('delivery_week')
    # def _set_delivery_week(self):
    #     # We must use max_commitment_date because it's the only one that can
    #     # always be modified
    #     # the kanban seems to work fine but  the delivery_week gets only the
    #     # isocalendar[1] we only have the week number and since 2018 is near,
    #     # isnt it possible we have some problems if we change the date from december
    #     # to january
    #     if self.state == 'sale' and self.delivery_week:
    #         # get the day max_commitment_date (the old date),
    #         # get the new delivery week,
    #         # set the new lastagreeddate to the old day of the week on the new delivery
    #         # week
    #         if self.commitment_date:
    #             if not self.max_commitment_date:
    #                 self.max_commitment_date = self.commitment_date
    #             old_delivery_week = self.max_commitment_date.isocalendar()[1]
    #             new_date = self.max_commitment_date + relativedelta(
    #                 days=(self.delivery_week - old_delivery_week) * 7)
    #         else:
    #             new_iso_date = fields.Datetime.now().replace(
    #
    #             )
    #             new_iso_date = str(dt.datetime.now().year) + '-' + str(
    #                 self.delivery_week) + '-1'
    #             new_date = fields.Datetime.from_string(new_iso_date, "%Y-%W-%w")
    #             self.commitment_date = new_date
    #
    #         new_date_string = new_date.strftime(DATE_FORMAT)
    #         self.max_commitment_date = new_date_string

    @api.depends('commitment_date')
    def _get_delivery_week(self):
        for order in self:
            if not order.commitment_date:
                order.delivery_week = False
                continue
            order.delivery_week = order.commitment_date.isocalendar()[1]

    @api.depends('order_line')
    def _compute_max_commitment_date(self):
        for order in self.filtered(
                lambda x: any(x.mapped('order_line.commitment_date'))):
            order.max_commitment_date = max(
                order.order_line.filtered(
                    lambda z: z.commitment_date
                ).mapped('commitment_date')
            )

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
            NOT_EVALUATED,
            PRODUCTION_NOT_EVALUATED,
            MISSING_COMPONENTS_BUY,
            MISSING_COMPONENTS_PRODUCE,
            PRODUCTION_READY,
            PRODUCTION_STARTED,
            DONE,
            PARTIALLYDELIVERED,
            AVAILABLEREADY,
            WAITING_FOR_PACKING,
            DONE_DELIVERY,
            INVOICED,
            SHIPPED,
        ]
        calendar_state = False
        if self.procurement_group_id:
            calendar_states = self.forecast_procurement(
                self.procurement_group_id, max_commitment_date)
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
        ])
        if picking_ids:
            calendar_state = WAITING_FOR_PACKING  # == AVAILABLEREADY
            if all([x.state == 'done' for x in picking_ids]):
                calendar_state = DONE_DELIVERY
            elif all([x.state == 'assigned' for x in picking_ids]):
                calendar_state = AVAILABLEREADY
            elif any([x.state == 'done' for x in picking_ids])\
                    and any([x.state != 'done' for x in picking_ids]):
                calendar_state = PARTIALLYDELIVERED
            calendar_states.append((calendar_state, fields.Datetime.now()))
        # this is needed if picking are not done only i presume, tocheck
        # group_id in purchase.order
        purchase_line_ids = self.env['purchase.order.line'].search([
            ('procurement_group_id', '=', procurement.id)
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
            ('procurement_group_id', '=', procurement.id),
        ])
        if mrp_production_ids:
            for mrp_production in mrp_production_ids:
                if mrp_production.state == 'done':
                    calendar_states.append((DONE, fields.Datetime.now()))
                elif mrp_production.state == 'confirmed':
                    calendar_states.append(
                        (PRODUCTION_NOT_EVALUATED, fields.Datetime.now())
                    )
                elif mrp_production.state == 'planned':
                    if any([x for x in mrp_production.move_raw_ids
                            if x.state not in ['cancel', 'assigned']]):
                        datetime_planned = fields.Datetime.now() + relativedelta(
                            days=mrp_production.product_id.produce_delay)
                        calendar_states.append(
                            (MISSING_COMPONENTS_PRODUCE, datetime_planned)
                        )
                    else:
                        calendar_states.append(
                            (PRODUCTION_READY, fields.Datetime.now())
                        )
                elif mrp_production.state == 'progress':
                    calendar_states.append(
                        (PRODUCTION_STARTED, fields.Datetime.now())
                    )
        # check if all lines of type product or consu of so are invoiced
        if all([ol.qty_delivered == ol.qty_invoiced == ol.product_uom_qty for ol in
                self.order_line if ol.product_id
                and ol.product_id.type in ['product', 'consu']]):
            calendar_states = [(INVOICED, fields.Datetime.now())]
            # check if all invoices linked to SO have tracking_ref filled
            if all([inv.carrier_tracking_ref for inv in self.invoice_ids]):
                calendar_states = [(SHIPPED, fields.Datetime.now())]
        return calendar_states

    @api.depends('order_line', 'order_line.qty_invoiced',
                 'picking_ids', 'picking_ids.state')
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
