# Copyright 2026 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    @api.model
    def message_process(
        self,
        model,
        message,
        custom_values=None,
        save_original=False,
        strip_attachments=False,
        thread_id=None,
    ):
        """Use the catch-all model as fallback for fetchmail servers.

        Core ``fetchmail.server.fetch_mail`` passes ``object_id.model`` as
        fallback model, so without that field unroutable emails raise and are
        dropped. When the fetchmail server has no model, route them to
        ``mail.catchall`` instead. When ``object_id`` is set it keeps being
        the fallback model: core only uses it for emails that no alias or
        reply can route, i.e. exactly the ones that would otherwise bounce.
        """
        server = (
            self.env["fetchmail.server"]
            .browse(self.env.context.get("default_fetchmail_server_id"))
            .exists()
        )
        if server:
            # Let the fallback model receive direct writes to the catch-all
            # alias, which core would bounce before using the fallback.
            self = self.with_context(mail_fetchmail_catchall=True)
            if not model and not server.object_id:
                model = "mail.catchall"
        return super().message_process(
            model,
            message,
            custom_values=custom_values,
            save_original=save_original,
            strip_attachments=strip_attachments,
            thread_id=thread_id,
        )

    def _detect_write_to_catchall(self, msg_dict):
        """Let the catch-all model receive emails sent to the catch-all alias.

        Core bounces a direct write to the configured catch-all address before
        falling back on the model; for a fetchmail catch-all server the email
        must be stored instead.
        """
        if self.env.context.get("mail_fetchmail_catchall"):
            return False
        return super()._detect_write_to_catchall(msg_dict)
