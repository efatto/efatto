# -*- coding: utf-8 -*-
{
    'name': "Reminders and Agenda for Issues",
    'version': '1.0.0',
    'author': 'Matmoz d.o.o.',
    'license': 'GPL-3',
    'category': 'Reminders and Agenda',
    'website': 'https://www.matmoz.si',
    'price': 21.00,
    'currency': 'EUR',
    'depends': ['project','reminder_base', 'service_desk_issue'],
    'data': [
        'security/ir.model.access.csv',
        'views.xml',
    ],
    'installable': False,
}
