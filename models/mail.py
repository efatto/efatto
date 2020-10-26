# Copyright 2020 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# Copyright (C) 2013 Stefano Siccardi creativiquadrati snc

from odoo import models, api


class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    @api.multi
    def send_mail(self, auto_commit=False):
        """
        If the email has been sent from the "Alert partner of the change"
        button, update the sale order max_commitment_date.
        """

        if (self._context.get('default_model', False) == 'sale.order' and
            self._context.get('default_res_id', False) and self._context.get(
                'change_agreed_date', False)):
            self.env['sale.order'].set_new_agreed_delivery_date(
                self._context['default_res_id'])
        return super(MailComposeMessage, self).send_mail()
