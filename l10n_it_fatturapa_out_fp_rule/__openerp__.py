# -*- coding: utf-8 -*-
# Copyright 2018 Lorenzo Battistini
# Copyright 2018 Sergio Zanchetta (Associazione PNLUG - Gruppo Odoo)
# Copyright 2019 Sergio Corato
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

{
    'name': 'Italian Localization - Fattura elettronica - Integrazione '
            'Dichiarazione Intento',
    "summary": "Modulo ponte tra emissione fatture elettroniche e "
               "dichiarazione intento",
    "version": "8.0.1.0.0",
    "development_status": "Beta",
    "category": "Hidden",
    'website': 'https://efatto.it',
    "author": "Sergio Corato",
    "maintainers": [],
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "auto_install": True,
    "depends": [
        "l10n_it_fatturapa_out",
        "account_fiscal_position_rule",
    ],
}
