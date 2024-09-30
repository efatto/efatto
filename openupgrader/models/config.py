
from odoo import fields, models


class AutoInstallModule(models.Model):
    _name = "auto.install.module"
    _description = "AutoInstall Module"

    name = fields.Text(string="Technical Name of Installed Module")
    module_installed_id = fields.Many2one(
        comodel_name="ir.module.module",
        string="Module Installed (alternative of name)",
    )
    module_to_install = fields.Text(
        string="Technical Name of Module To Install",
        required=True,
    )


class ModuleName(models.Model):
    _name = "module.name"
    _description = "Module name"

    name = fields.Text(string="Module Technical Name")


class SqlUpdateCommand(models.Model):
    _name = "sql.update.command"
    _description = "SQL Update Command"
    _rec_name = "sql_command"

    sql_command = fields.Text(string="SQL Command")


class OdooVersion(models.Model):
    _name = "odoo.version"
    _description = "Odoo Version"

    name = fields.Char(
        string="Odoo Version name",
        help="Like 12.0",
        required=True,
    )
    python_version = fields.Char(
        string="Python Version",
        help="Like 3.7",
        required=True,
    )


class OpenupgraderConfig(models.Model):
    _name = "openupgrader.config"
    _description = "Openupgrader config"
    _rec_name = "odoo_version"

    odoo_version = fields.Many2one(
        comodel_name="odoo.version",
        string="Odoo version",
    )
    sql_update_command_ids = fields.Many2many(
        comodel_name="sql.update.command",
        string="SQL update commands")
    module_auto_install_ids = fields.Many2many(
        comodel_name="auto.install.module",
        string="Auto install modules",
        help="List of modules to install if there is another module installed",
    )
    module_to_delete_after_migration_ids = fields.Many2many(
        comodel_name="ir.module.module",
        relation="delete_module_rel",
        column1="current_module_id",
        column2="delete_module_id",
        string="Modules to delete after migration",
        help="List of modules to delete",
    )
    module_to_uninstall_after_migration_ids = fields.Many2many(
        comodel_name="ir.module.module",
        relation="uninstall_after_module_rel",
        column1="current_module_id",
        column2="uninstall_module_after_id",
        string="Module to uninstall after migration",
    )
    module_to_uninstall_before_migration_ids = fields.Many2many(
        comodel_name="ir.module.module",
        relation="uninstall_before_module_rel",
        column1="current_module_id",
        column2="uninstall_module_before_id",
        string="Module to uninstall before migration",
    )


class RemoteRepo(models.Model):
    _name = "remote.repo"
    _description = "Remote Repo"

    name = fields.Char(string="Remote Repo Name")
    remote_url = fields.Char(string="Remote Repo URL")
    remote_branch = fields.Char(string="Remote Repo Branch")


class OpenupgraderRepo(models.Model):
    _name = "openupgrader.repo"
    _description = "Openupgrader repositories for version"
    _rec_name = "odoo_version"

    odoo_version = fields.Many2one(
        comodel_name="odoo.version",
        string="Odoo version",
    )
    remote_repo_ids = fields.Many2many(
        comodel_name="remote.repo",
        string="Remote",
    )
