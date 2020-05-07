# Copyright 2017-2020 Sergio Corato <https://github.com/sergiocorato>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    'name': 'Ricevute bancarie improvements',
    'version': '12.0.1.0.0',
    'category': 'other',
    'author': 'Sergio Corato',
    'website': 'https://efatto.it',
    'description': '''
    Added features:
    - show ABI CAB in riba list;
    - get bank from riba line if added manually;
    - add checks for negative lines and sum;
    - add search view to abi-cab (TODO PR);
    - move date accepted, date accreditation and date paid in front of riba view;
    - get number of invoice from move line if invoice is not linked.
    ''',
    'license': 'LGPL-3',
    'depends': [
        'l10n_it_abicab',
        'l10n_it_ricevute_bancarie',
    ],
    'data': [
        'views/partner_view.xml',
        'views/res_bank_view.xml',
        'views/riba_view.xml',
    ],
    'installable': True
}
