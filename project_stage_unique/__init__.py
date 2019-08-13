# -*- coding: utf-8 -*-

from . import models


def pre_init_hook(cr):
    cr.execute("SELECT max(id) from project_task_type")
    max_id = cr.fetchone()[0]
    old_id = 3
    #  first remove unused task type created manually
    cr.execute("DELETE from project_task_type where id not in "
               "(select stage_id from project_task) and id > %s and "
               "id <= %s", (old_id, max_id - 8))
    cr.execute("DELETE from project_task_type where id not in "
               "(select stage_id from project_task) and id > %s", max_id)

    cr.execute(
        "SELECT id, name from project_task_type where name in (SELECT name"
        " from project_task_type WHERE id not in(SELECT MAX(id)"
        " from project_task_type GROUP BY name))")
    rest = duplication_ids = cr.fetchall()
    for duplication_id in duplication_ids:
        rest.remove(duplication_id)
        for r in rest:
            if duplication_id[1] == r[1]:
                cr.execute("UPDATE project_task SET stage_id = %s WHERE"
                           " stage_id = %s", (duplication_id[0], r[0]))

    # finally remove unused task type resulting from removing duplications
    cr.execute("DELETE from project_task_type where id not in "
               "(select stage_id from project_task) and id > %s and "
               "id <= %s", (old_id, max_id - 8))
    cr.execute("DELETE from project_task_type where id not in "
               "(select stage_id from project_task) and id > %s", max_id)

