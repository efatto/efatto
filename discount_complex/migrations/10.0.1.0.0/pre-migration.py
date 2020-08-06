# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # install sale_triple_discount
    env.cr.execute(
        "update ir_module_module set state='to install' "
        "where name='sale_triple_discount' and state='uninstalled'"
    )
