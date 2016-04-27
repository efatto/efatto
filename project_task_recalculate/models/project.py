# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, _
from openerp.exceptions import Warning, ValidationError
from datetime import datetime


class ProjectProject(models.Model):
    _inherit = 'project.project'

    @api.multi
    def project_recalculate(self):
        """
            Recalculate project tasks start and end dates.
            After that, recalculate new project start or end date
        """
        for project in self:
            if not project.calculation_type:
                raise Warning(_("Cannot recalculate project because your "
                                "project don't have calculation type."))
            if (project.calculation_type == 'date_begin' and not
                    project.date_start):
                raise Warning(_("Cannot recalculate project because your "
                                "project don't have date start."))
            if (project.calculation_type == 'date_end' and not
                    project.date):
                raise Warning(_("Cannot recalculate project because your "
                                "project don't have date end."))
            if project.calculation_type != 'none':

                task_with_only_childs = self.env['project.task'].search(
                    [('project_id', '=', project.id),
                    ('child_ids', '!=', False), ('parent_ids', '=', False)])
                for task in task_with_only_childs:
                    task.task_recalculate()

                task_with_childs_parents = self.env['project.task'].search(
                    [('project_id', '=', project.id),
                    ('child_ids', '!=', False), ('parent_ids', '!=', False)])
                for task in task_with_childs_parents:
                    task.task_recalculate()

                task_with_only_parents = self.env['project.task'].search(
                    [('project_id', '=', project.id),
                    ('child_ids', '=', False), ('parent_ids', '!=', False)])
                for task in task_with_only_parents:
                    task.task_recalculate()

                task_without_childs_parents = self.env['project.task'].search(
                    [('project_id', '=', project.id),
                    ('child_ids', '=', False), ('parent_ids', '=', False)])
                for task in task_without_childs_parents:
                    task.task_recalculate()

                vals = project._start_end_dates_prepare()
                if vals:
                    project.write(vals)
        return True


class ProjectTask(models.Model):
    _inherit = 'project.task'

    @api.multi
    def task_recalculate(self):
        # super(ProjectTask, self).task_recalculate()
        to_string = fields.Datetime.to_string

        for task in self:
            if not task.include_in_recalculate:
                return True

            resource, calendar = task._resource_calendar_select()
            increment, project_date, from_days = task._calculation_prepare()
            date_start = False
            date_end = False
            from_days = self._from_days_dec(
                from_days, project_date, resource, calendar, increment)
            start = self._calendar_schedule_days(
                from_days, project_date, resource, calendar)[1]
            if start:
                day = start[0].replace(hour=0, minute=0, second=0)
                first = self._first_interval_of_day_get(
                    day, resource, calendar)
                if first:
                    date_start = first[0]
            if date_start:
                if task.child_ids and not task.parent_ids or (
                    not task.child_ids and not task.parent_ids
                ):
                    end = self._calendar_schedule_days(
                        task.estimated_days, date_start, resource, calendar)[1]
                    if end:
                        date_end = end[1]

                    for child in task.child_ids:
                        child.date_end = child.date_start = False
                        child.date_start = date_end

                elif task.child_ids and task.parent_ids: # raggruppare con elif successivo se si può
                    # prendo la max data dei parents e la imposto come data iniziale e finale
                    # TODO impostare la data dei childs
                    date_start = self._get_max_date_from_parents(task, date_start)
                    end = self._calendar_schedule_days(
                        task.estimated_days, date_start, resource, calendar)[1]
                    if end:
                        date_end = end[1]

                elif not task.child_ids and task.parent_ids: # solo genitori
                    date_start = self._get_max_date_from_parents(task, date_start)

                    end = self._calendar_schedule_days(
                        task.estimated_days, date_start, resource, calendar)[1]
                    if end:
                        date_end = end[1]

            task.with_context(task.env.context, task_recalculate=True).write({
                'date_start': date_start and to_string(date_start) or False,
                'date_end': date_end and to_string(date_end) or False,
                'date_deadline': date_end and to_string(date_end) or False,
            })

        return True

    def _get_max_date_from_parents(self, task, date_start):
        max_date = date_start

        for parent in task.parent_ids:
            if parent.date_end:
                if datetime.strptime(
                        parent.date_end[:10], '%Y-%m-%d') > max_date:
                    max_date = datetime.strptime(
                        parent.date_end[:10], '%Y-%m-%d')

        return max_date
