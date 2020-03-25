# Copyright 2017-2020 Sergio Corato <https://github.com/sergiocorato>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    'name': 'Ricevute bancarie extension',
    'version': '12.0.1.0.0',
    'category': 'Accounting',
    'author': 'Sergio Corato',
    'website': 'http://www.efatto.it',
    'description': 'Ricevute bancarie bank riba from partner',
    'license': 'LGPL-3',
    'depends': [
        'account_bank',
        'account_payment_term_extension',
        'l10n_it_abicab',
        'l10n_it_ricevute_bancarie',
    ],
    'data': [
        'views/account_view.xml',
        'views/partner_view.xml',
        'views/res_bank_view.xml',
        'views/riba_view.xml',
    ],
    'installable': False
}
