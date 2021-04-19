# Copyright 2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Server Env Mail',
    'version': '12.0.1.0.1',
    'category': 'other',
    'author': 'Sergio Corato',
    'website': 'https://efatto.it',
    'license': 'AGPL-3',
    'description': 'Use decorator to block mail fetch and send on server when '
                   'running_env != prod',
    'depends': [
        'fetchmail',
        'mail',
        'server_env',
    ],
    'installable': True
}
