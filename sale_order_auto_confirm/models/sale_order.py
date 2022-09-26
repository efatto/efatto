# Copyright 2013 Creativiquadrati snc
# Copyright 2020 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, exceptions, models
from datetime import datetime
from dateutil import rrule


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def confirm_sale_orders_in_waiting_confirm(
            self, day_limit=3, festivities=None):
        """
        Funzione chiamata dal cron per confermare i preventivi inseriti più di
        *day_limit* (default 3) giorni fa.
        Non conta il sabato e la domenica e le festività possono venire passate
        come parametro [(giorno, mese), ...]
        """

        if festivities is None or not isinstance(festivities, list):
            festivities = [
                (1, 1), (6, 1), (25, 4), (1, 5), (2, 6), (15, 8),
                (1, 11), (8, 12), (25, 12), (26, 12), (31, 12)]
        if not day_limit or not isinstance(day_limit, int):
            day_limit = 3

        now = datetime.now()
        for order in self.search([('state', '=', 'sent'),
                                  '|',
                                  ('commitment_date', '!=', False),
                                  ('max_commitment_date', '!=', False)]):
            days_between = 0
            for day in rrule.rrule(rrule.DAILY, dtstart=order.date_order, until=now,
                                   byweekday=[0, 1, 2, 3, 4]):
                if (day.day, day.month) not in festivities:
                    days_between += 1
            if days_between > day_limit:
                try:
                    order.action_confirm()
                except (exceptions.UserError, exceptions.ValidationError):
                    pass
        return {}
