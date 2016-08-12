# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from . import models


def pre_init_hook(cr):
    #  first remove unused task type created manually
    cr.execute("DELETE from project_task_type where id not in "
               "(select stage_id from project_task) and id > 8")

    cr.execute(
        "SELECT id, name from project_task_type where name in (SELECT name"
        " from project_task_type WHERE id not in(SELECT MAX(id)"
        " from project_task_type GROUP BY name))")
    rest = duplication_ids = cr.fetchall()
    for duplication_id in duplication_ids:
        rest.remove(duplication_id)
        for r in rest:
            if duplication_id[1] == r[1]:
                cr.execute("UPDATE project_task SET stage_id = {0} WHERE"
                           " stage_id = {1}".format(duplication_id[0], r[0]))

    # finally remove unused task type resulting from removing duplications
    cr.execute("DELETE from project_task_type where id not in "
               "(select stage_id from project_task) and id > 8")
