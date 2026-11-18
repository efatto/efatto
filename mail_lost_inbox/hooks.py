# Copyright 2026 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

_logger = logging.getLogger(__name__)


def uninstall_hook(env):
    """Remove the inbox leftovers the ORM does not cascade to."""
    messages = env["mail.message"].sudo().search([("model", "=", "mail.lost.inbox")])
    if messages:
        messages.unlink()
    followers = (
        env["mail.followers"].sudo().search([("res_model", "=", "mail.lost.inbox")])
    )
    if followers:
        followers.unlink()
    attachments = (
        env["ir.attachment"]
        .sudo()
        .search(
            [
                ("res_model", "=", "mail.lost.inbox"),
                ("res_field", "in", [False, "raw_message"]),
            ]
        )
    )
    if attachments:
        _logger.info("Removing %s attachments of the lost mail inbox", len(attachments))
        attachments.unlink()
