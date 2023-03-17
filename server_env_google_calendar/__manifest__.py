# Copyright 2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Server Env Google Calendar',
    'version': '12.0.1.0.1',
    'category': 'other',
    'author': 'Sergio Corato',
    'website': 'https://github.com/sergiocorato/efatto',
    'license': 'AGPL-3',
    'description': 'Use decorator to block Google calendar sync on server when '
                   'running_env != prod',
    'depends': [
        'google_calendar',
        'server_env',
    ],
    'installable': True
}
