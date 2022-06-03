# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, _


class ir_mail_server(models.Model):
    _inherit = "ir.mail_server"

    @api.model
    def send_email(self, message, mail_server_id=None,
                   smtp_server=None, smtp_port=None,
                   smtp_user=None, smtp_password=None, smtp_encryption=None,
                   smtp_debug=False):
        mail_server = False
        email_from = message['From']
        domain_list = email_from.split('>')[0].split('@')
        if len(domain_list) == 2:
            domain = domain_list[1]
            #search mail_server on domain of user sending mail
            mail_server = self.search([('name', '=', domain)])
        if mail_server:
            mail_server_id = mail_server.id
        return super(ir_mail_server, self).send_email(
            message, mail_server_id=mail_server_id,
            smtp_server=smtp_server, smtp_port=smtp_port,
            smtp_user=smtp_user, smtp_password=smtp_password,
            smtp_encryption=smtp_encryption, smtp_debug=smtp_debug
        )
