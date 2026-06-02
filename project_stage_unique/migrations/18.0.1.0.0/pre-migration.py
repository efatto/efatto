from openupgradelib import openupgrade

from odoo.addons.project_stage_unique import hooks


@openupgrade.migrate()
def migrate(env, version):
    # Ensure project stage type unicity as until v.14 translations were not considered
    hooks.pre_init_hook(env)
