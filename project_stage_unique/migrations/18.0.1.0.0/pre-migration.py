from openupgradelib import openupgrade

from odoo.addons.project_stage_unique.hooks import pre_init_hook


@openupgrade.migrate()
def migrate(env, version):
    pre_init_hook(env)
