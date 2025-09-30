# Copyright 2023 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Invoice analytic line mrp actual cost",
    "summary": "Compute actual mrp cost from analytic line from invoices",
    "version": "14.0.1.0.0",
    "category": "Accounting",
    "author": "Sergio Corato",
    "website": "https://github.com/efatto/efatto",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "mis_builder_query_drilldown",
        "mrp_analytic",
        "sale_mrp",
    ],
    "data": [
        "views/account.xml",
        "views/account_invoice_line_views.xml",
    ],
}
