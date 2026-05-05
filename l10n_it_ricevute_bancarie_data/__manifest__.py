# Copyright 2016 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Termini di pagamento per ricevute bancarie",
    "version": "18.0.1.0.0",
    "category": "Localisation/Italy",
    "summary": "Ri.ba. sbf data",
    "author": "Sergio Corato",
    "website": "https://github.com/efatto/efatto",
    "license": "AGPL-3",
    "depends": [
        "account_payment_term_extension",
        "l10n_it_riba_oca",
        "l10n_it_edi_extension",
    ],
    "data": [
        "data/payment_data.xml",
    ],
    "installable": True,
}
