# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp.osv import fields, osv


class project(osv.osv):
    _inherit = "project.project"

    # override to remove
    # LEFT JOIN project_task_type ON project_task.stage_id =
    #  project_task_type.id
    # AND project_task_type.fold = False
    def _progress_rate(self, cr, uid, ids, names, arg, context=None):
        res = super(project, self)._progress_rate(
            cr, uid, ids, names, arg, context=context)
        child_parent = self._get_project_and_children(cr, uid, ids, context)
        # compute planned_hours, total_hours, effective_hours specific
        # to each project
        cr.execute("""
            SELECT project_id, COALESCE(SUM(planned_hours), 0.0),
                COALESCE(SUM(total_hours), 0.0), COALESCE(SUM(effective_hours),
                 0.0)
            FROM project_task
            WHERE project_task.project_id IN %s
            GROUP BY project_id
            """, (tuple(child_parent.keys()),))
        # aggregate results into res
        res = dict([(id, {'planned_hours': 0.0, 'total_hours': 0.0,
                          'effective_hours': 0.0}) for id in ids])
        for id, planned, total, effective in cr.fetchall():
            # add the values specific to id to all parent projects of id in
            #  the result
            while id:
                if id in ids:
                    res[id]['planned_hours'] += planned
                    res[id]['total_hours'] += total
                    res[id]['effective_hours'] += effective
                id = child_parent[id]
        # compute progress rates
        for id in ids:
            if res[id]['total_hours']:
                res[id]['progress_rate'] = round(
                    100.0 * res[id]['effective_hours'] / res[id][
                        'total_hours'], 2)
            else:
                res[id]['progress_rate'] = 0.0
        return res
