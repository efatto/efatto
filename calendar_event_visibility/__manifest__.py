# Copyright 2020 Sergio Corato <https://github.com/sergiocorato>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    'name': 'Event visibility',
    'version': '12.0.1.0.0',
    'category': 'other',
    'author': 'Sergio Corato',
    'description':
        'Limit visibility of event to involved users, excluding hr employee.',
    'website': 'https://efatto.it',
    'license': 'AGPL-3',
    'depends': [
        'calendar',
    ],
    'data': [
        'security/calendar_event_security.xml',
    ],
    'installable': True,
}
