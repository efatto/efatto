# Copyright 2016-2020 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Better view of task on calendar',
    'version': '12.0.1.0.1',
    'category': 'Extra Tools',
    'summary': 'View task on calendar based on date_end and date_start',
    'description':
        'View task on calendar based on date_end and date_start',
    'author': 'Sergio Corato',
    'website': 'https://github.com/sergiocorato/efatto',
    'license': 'AGPL-3',
    'depends': [
        'project',
    ],
    'data': [
        'views/task_view.xml'
    ],
    'installable': True,
}
