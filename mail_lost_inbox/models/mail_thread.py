# Copyright 2026 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    @api.model
    def message_route(
        self, message, message_dict, model=None, thread_id=None, custom_values=None
    ):
        """Store emails that Odoo cannot route in the lost mail inbox.

        The mail gateway (``fetchmail`` or ``odoo-mailgate.py``) calls this
        method without a fallback model: a ``ValueError`` means the email
        would be dropped. Store it instead and report success so the mail
        server does not retry it forever.
        """
        LostInbox = self.env["mail.lost.inbox"].sudo()
        # Keep catch-all emails before core bounces them. Bounces, replies and
        # fallback models are left to core routing unchanged.
        if (
            not model
            and not thread_id
            and not message_dict.get("is_bounce")
            and not message_dict.get("parent_id")
            and LostInbox._is_direct_catchall(message_dict)
            and LostInbox._should_keep_catchall(message_dict)
            and (
                LostInbox._should_keep_automatic(message_dict)
                or not LostInbox._is_automatic(message)
            )
        ):
            try:
                with self.env.cr.savepoint():
                    LostInbox._capture_message(message, message_dict, reason="catchall")
            except Exception:
                _logger.exception(
                    "Could not store catch-all email %s in the lost mail inbox",
                    message_dict.get("message_id"),
                )
            else:
                return []
        try:
            return super().message_route(
                message,
                message_dict,
                model=model,
                thread_id=thread_id,
                custom_values=custom_values,
            )
        except ValueError as error:
            if "no possible route found" not in str(error).lower():
                raise
            # Keep the pre-existing behaviour for automatic and bulk emails
            # unless the feature is explicitly enabled.
            if not LostInbox._should_keep_automatic(
                message_dict
            ) and LostInbox._is_automatic(message):
                raise
            reason = "catchall" if LostInbox._is_catchall(message_dict) else "no_route"
            try:
                with self.env.cr.savepoint():
                    LostInbox._capture_message(message, message_dict, reason=reason)
            except Exception as capture_error:
                _logger.exception(
                    "Could not store unroutable email %s in the lost mail inbox",
                    message_dict.get("message_id"),
                )
                raise error from capture_error
            return []
