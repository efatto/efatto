from odoo import models

from odoo.addons.server_env.models.server import running


class MailMail(models.Model):
    _inherit = "mail.mail"

    @running
    def send(self, auto_commit=False, raise_exception=False):
        return super().send(auto_commit=auto_commit, raise_exception=raise_exception)
