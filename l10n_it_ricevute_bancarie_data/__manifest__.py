# Copyright 2016-2020 Sergio Corato <https://github.com/sergiocorato>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    'name': 'Termini di pagamento per ricevute bancarie',
    'version': '12.0.1.0.4',
    'category': 'Localisation/Italy',
    'description': 'Ri.ba. sbf data',
    'author': 'Corato Sergio',
    'website': 'https://github.com/sergiocorato/efatto',
    'license': 'LGPL-3',
    'depends': [
        'account_payment_term_extension',
        'l10n_it_ricevute_bancarie',
        'l10n_it_fiscal_payment_term',
    ],
    'data': [
        'data/payment_data.xml',
    ],
    'installable': True
}
