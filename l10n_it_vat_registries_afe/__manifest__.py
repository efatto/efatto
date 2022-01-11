# Copyright 2019-2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Italian vat registries report with AFE number",
    "version": "12.0.1.0.0",
    "category": "Account",
    "author": "Sergio Corato",
    "website": "https://efatto.it",
    "license": "AGPL-3",
    "description": "Italian vat registries report with AFE number",
    "depends": [
        "afe_odoo_connector",
        "l10n_it_vat_registries",
    ],
    "data": [
        "views/vat_registries_report.xml",
    ],
    "installable": True
}
