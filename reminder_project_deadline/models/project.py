from odoo import models


class Project(models.Model):
    _name = 'project.project'
    _inherit = ['project.project', 'reminder']

    _reminder_date_field = 'date'
    _reminder_attendees_fields = ['user_id'] #favorite_user_ids?
