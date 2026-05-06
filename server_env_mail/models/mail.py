from odoo import models

from odoo.addons.server_env.models.server import running


class MailMail(models.Model):
    _inherit = "mail.mail"

    @running
    def send(self, auto_commit=False, raise_exception=False, post_send_callback=None):
        return super().send(
            auto_commit=auto_commit,
            raise_exception=raise_exception,
            post_send_callback=post_send_callback,
        )
