# Copyright 2026 Sergio Corato
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Helpdesk AI Draft Replies",
    "summary": "Draft ticket replies with an AI model: pseudonymized personal "
    "data, two technician approvals, confidence level, Q&A archive",
    "version": "18.0.1.0.0",
    "category": "After-Sales",
    "license": "AGPL-3",
    "author": "Sergio Corato",
    "website": "https://github.com/efatto/efatto",
    "depends": ["helpdesk_mgmt", "ai_oca_bridge"],
    "data": [
        "security/helpdesk_ai_draft_security.xml",
        "security/ir.model.access.csv",
        "data/helpdesk_ai_review_reason_data.xml",
        "data/ir_config_parameter_data.xml",
        "views/helpdesk_ai_review_reason_views.xml",
        "views/helpdesk_ai_draft_log_views.xml",
        "views/helpdesk_ai_qa_views.xml",
        "views/helpdesk_ticket_views.xml",
        "wizards/helpdesk_ai_review_wizard_views.xml",
        "wizards/helpdesk_ai_qa_import_wizard_views.xml",
        "views/helpdesk_ai_draft_menus.xml",
    ],
    "installable": True,
}
