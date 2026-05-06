from odoo import models

from odoo.addons.server_env.models.server import running


class Fetchmail(models.Model):
    _inherit = "fetchmail.server"

    @running
    def fetch_mail(self, raise_exception=True):
        return super().fetch_mail(raise_exception=raise_exception)

    @running
    def connect(self, allow_archived=False):
        return super().connect(allow_archived=allow_archived)
