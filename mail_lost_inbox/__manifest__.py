# Copyright 2026 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Mail Lost Inbox",
    "summary": "Keep unroutable incoming emails in an inbox and route them "
    "to the right record [WIP: review and test before usage, if needed]",
    "version": "18.0.1.0.0",
    "category": "Productivity/Discuss",
    "author": "Sergio Corato",
    "website": "https://github.com/efatto/efatto",
    "license": "AGPL-3",
    "application": True,
    "depends": ["mail"],
    "data": [
        "security/mail_lost_inbox_security.xml",
        "security/ir.model.access.csv",
        "data/ir_cron_data.xml",
        "wizards/mail_lost_inbox_route_views.xml",
        "views/mail_lost_inbox_views.xml",
        "views/mail_lost_inbox_rule_views.xml",
        "views/res_config_settings_views.xml",
        "views/mail_lost_inbox_menus.xml",
    ],
    "installable": True,
    "uninstall_hook": "uninstall_hook",
}
