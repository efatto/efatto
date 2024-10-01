
from odoo import fields, models, tools, api, _
from odoo.exceptions import UserError

import odooly
import shutil
import subprocess
import time
import os
import signal
# from main import openupgrade_fixes


class OpenupgraderMigration(models.Model):
    _name = "openupgrader.migration"
    _description = "Openupgrader Migration"
    _rec_name = 'from_version'

    """
    PROCEDURA:
    copiare nella cartella ~ i file:
    database.gz [file creato con pg_dump [database] | gzip > database.gz
    e filestore.tar [file creato con tar -cvzf filestore.tar ./filestore
    oppure
    database.sql e cartella del filestore [estratti da auto_backup]
    e lanciare con
    import openupgrader
    mig = openupgrader.Connection('db', 'amministratore_db', 'pw_db', '5435')
    in seguito lanciare i comandi seguenti ripetutamente per ogni versione
    mig.prepare_migration()
    mig.do_migration()
    oppure
    mig.prepare_do_migration()
    n.b.: per il momento è supportata solo la migrazione di 1 versione per volta
    :param db: il database da migrare (il nuovo nome)
    :param user: l'utente amministrativo
    :param password: la password dell'utente amministrativo
    :param db_port: la porta del database su cui la funzione andra a
    cancellare e ripristinare il database da migrare
    xmlrpc_port: la porta su cui è accessibile il servizio - viene
    impostata come 80 + i due numeri finali della porta del db
    n.b. non deve essere in uso da altre istanze
    n.b. per comodità ho creato dei cluster di postgres 11 con le porte 5439-40-41
    in mancanza va con il postgres di default nella porta indicata
    troubleshooting:
    per correggere il problema
    can't find '__main__' module in '/usr/share/python-wheels/pep517-0.8.2-py2.py3
    -none-any.whl/pep517/_in_process.py'
    e altri, ho forzato la reinstallazione delle varie librerie
    ../bin/pip install --force-reinstall -r requirements.txt
    """

    db_name = fields.Char(string="Database name",
                          default=lambda self: self.env.cr.dbname)
    db_user = fields.Char(string="Database user")
    db_password = fields.Char(string="Database password")
    pg_user = fields.Char(string="Postgres user", default="odoo")
    disabled_cron_ids = fields.Many2many(
        comodel_name="ir.cron",
        string="Disabled ir crons",
    )
    odoo_pid = fields.Char(string="Odoo migrated process PID")
    db_port = fields.Char(string="Database port", default='5432')
    xmlrpc_port = fields.Char(string="XmlRpc port", default='8032')
    folder = fields.Char(
        default=lambda self: self._default_folder(),
        help="Absolute path for migrated Odoo instance",
        required=True,
    )
    # self.fixes = openupgrade_fixes.Fixes()
    from_version = fields.Many2one(
        comodel_name="odoo.version",
        string="From Odoo Version",
    )
    to_version = fields.Many2one(
        comodel_name="odoo.version",
        string="To Odoo Version",
    )
    restore_db_update = fields.Boolean(string="Restore DB and update")
    restore_db_only = fields.Boolean(string="Restore DB")
    create_venv = fields.Boolean(string="Creare Odoo Virtualenv")
    filestore = fields.Boolean()
    migrate_ddt = fields.Boolean()
    repo_ids = fields.Many2many(
        comodel_name="openupgrader.repo",
        relation="openupgrader_migration_repo_rel",
        column1="migration_id",
        column2="repo_id",
        string="Repositories",
    )
    config_ids = fields.Many2many(
        comodel_name="openupgrader.config",
        relation="openupgrader_migration_config_rel",
        column1="migration_id",
        column2="config_id",
        string="Openupgrader config",
    )
    # self.odoo_client = False
    openupgrade_repo = fields.Char(
        string="OpenUpgrade Repository",
    )
    odoo_repo = fields.Char(
        string="Odoo Repository",
    )

    @api.model
    def _default_folder(self):
        """Default to ``backups`` folder inside current server datadir."""
        return os.path.join(tools.config["data_dir"], "openupgrade", self.env.cr.dbname)

    def odoo_connect(self):
        self.odoo_client = odooly.Client(
            server='http://localhost:%s' % self.xmlrpc_port,
            db=self.env.cr.dbname,
            user=self.db_user,
            password=self.db_password,
        )
        time.sleep(5)

    def start_odoo(self, version, update=False, extra_command='', save=False):
        """
        :param version: odoo version to start (8.0, 9.0, 10.0, ...)
        :param update: if True odoo will be updated with -u all and stopped
        :param extra_command: command that will be passed after executable
        :param save: if True save .odoorc and stop Odoo
        :return: Odoo instance in "self.odoo_client" if not updated, else nothing
        """
        version_name = version.name
        folder = '%s/%s' % (self.folder, version_name)
        load = 'web'
        if version_name == '10.0':
            load = 'web,web_kanban'
        if version_name not in ['7.0', '8.0', '9.0', '10.0', '11.0']:
            load = 'base,web'
        if version_name not in [
            '7.0', '8.0', '9.0', '10.0', '11.0', '12.0', '13.0'
        ]:
            load += ',openupgrade_framework,module_change_auto_install'
        executable = 'openerp-server' if version_name in ['7.0', '8.0', '9.0']\
            else 'odoo'
        odoorc_exist = bool(
            os.path.isfile(
                os.path.join(folder, '.odoorc')
            )
            and not self.migrate_ddt
        )
        addons_path = f'{folder}/repos/odoo/addons,'
        if version_name in ['8.0', '9.0', '10.0', '11.0', '12.0', '13.0']:
            addons_path = f"{folder}/odoo/addons,"
        extra_addons_path = \
            f',{folder}/repos/odoo/odoo/addons,{folder}/odoo'
        if version_name in ['10.0', '11.0', '12.0', '13.0']:
            extra_addons_path = f',{folder}/odoo/odoo/addons'
        bash_command = \
            f"bin/{executable} " \
            f"{'-c .odoorc' if odoorc_exist else ''} " \
            f"{not odoorc_exist and f'--addons-path={addons_path}' or ''}" \
            f"{not odoorc_exist and f'{folder}/addons-extra' or ''}" \
            f"{not odoorc_exist and extra_addons_path or ''} " \
            f"{extra_command} " \
            f"--db_port={self.db_port} --xmlrpc-port={self.xmlrpc_port} " \
            f"--logfile={folder}/migration.log " \
            f"{not odoorc_exist and '--limit-time-cpu=1600' or ''} " \
            f"{not odoorc_exist and '--limit-time-real=3200' or ''} " \
            f"{not odoorc_exist and '--limit-memory-soft=4147483648' or ''} " \
            f"{not odoorc_exist and '--limit-memory-hard=4679107584' or ''} " \
            f"--load={load} "
        if version_name != '7.0':
            bash_command += "--data-dir=%s/data_dir " % folder
        if update:
            bash_command += " -u all -d %s --stop" % self.env.cr.dbname
        if save:
            bash_command += " -s --stop"
        process = subprocess.Popen(
            bash_command.split(), stdout=subprocess.PIPE)
        self.odoo_pid = process.pid
        if update or extra_command:
            process.wait()
        else:
            time.sleep(15)
            if not save:
                self.odoo_connect()
            else:
                not_auto_install_list = [
                    "partner_autocomplete", "iap", "mail_bot", "account_edi",
                    "account_edi_facturx", "account_edi_ubl", "l10n_it_stock_ddt"
                ]
                mod_not_install = \
                    f"modules_auto_install_disabled = {','.join(not_auto_install_list)}"
                subprocess.Popen(
                    ['mv ~/.odoorc ./'], shell=True
                ).wait()
                subprocess.Popen(
                    [f'sed -i "s/^osv_memory_age_limit.*/{mod_not_install}/g" .odoorc'],
                    shell=True
                ).wait()
        time.sleep(5)

    def stop_odoo(self):
        if self.odoo_pid:
            os.kill(self.odoo_pid, signal.SIGTERM)
            time.sleep(10)
            os.kill(self.odoo_pid, signal.SIGTERM)

    def disable_mail(self, disable=False):
        state = 'draft' if disable else 'done'
        active = False if disable else True
        fetchmail_server_ids = self.env["fetchmail.server"].search([
            ("state", "=", state),
        ])
        if fetchmail_server_ids:
            fetchmail_server_ids.write({"state": state})
        ir_mail_server_ids = self.env["ir.mail_server"].with_context(
            active_test=False,
        ).search([
            ("active", "=", active),
        ])
        if ir_mail_server_ids:
            ir_mail_server_ids.write({"active": active})

    def move_filestore(self, from_folder=False, from_version=False, to_version=False,
                       restore_db_only=False):
        if not from_folder:
            from_folder = (
                f'{self.folder}/{from_version}/data_dir'
                f'/filestore/{self.env.cr.dbname}')
        to_version_filestore = (
            f'{self.folder}/{to_version}/data_dir'
            f'/filestore/{self.env.cr.dbname}')
        if os.path.isdir(to_version_filestore) and not restore_db_only:
            shutil.rmtree(to_version_filestore, ignore_errors=True)
        if not restore_db_only:
            os.rename(from_folder, to_version_filestore)

    def restore_filestore(self, from_version, to_version):
        filestore_path = os.path.join(
            self.folder, to_version, 'data_dir', 'filestore'
        )
        if not os.path.isdir(filestore_path):
            os.makedirs(filestore_path, exist_ok=True)
        dump_folder = os.path.join(self.path, 'filestore')
        dump_file = os.path.join(self.path, 'filestore.tar')
        if os.path.isdir(dump_folder):
            self.move_filestore(from_folder=dump_folder, to_version=to_version)
            return
        elif os.path.isfile(dump_file):
            os.rename(dump_file, f'{self.folder}/filestore.{from_version}.tar')
        dump_file = os.path.join(
            self.folder, f'filestore.{from_version}.tar')
        filestore_db_path = os.path.join(
            filestore_path, self.env.cr.dbname
        )
        if not os.path.isdir(filestore_db_path):
            os.mkdir(filestore_db_path)
        process = subprocess.Popen([
            f'tar -zxvf {dump_file} --strip-components=1 -C {filestore_db_path}/'
        ], shell=True)
        process.wait()

    def dump_filestore(self, version_name):
        process = subprocess.Popen([
            'cd %s/%s/data_dir/filestore && tar -zcvf %s/filestore.%s.tar %s' % (
                self.folder, version_name, self.folder, version_name, self.env.cr.dbname)
        ], shell=True)
        process.wait()

    def dump_database(self, version_name):
        process = subprocess.Popen(
            [
                f'pg_dump -O -p {self.db_port} -d {self.env.cr.dbname} > '
                f'{os.path.join(self.folder, "database.%s.sql" % version_name)}'
            ], shell=True)
        process.wait()

    def restore_db(self):
        subprocess.Popen(
            [f'dropdb -p {self.db_port} {self.env.cr.dbname}_migrate_{self.to_version.name}'],
            shell=True).wait()
        subprocess.Popen(
            [f'createdb -p {self.db_port} '
             f'{self.env.cr.dbname}_migrate_{self.to_version.name}'],
            shell=True).wait()
        dump_file_sql = os.path.join(
            self.folder, "database.%s.sql" % self.from_version.name)
        if not os.path.isfile(dump_file_sql):
            raise UserError(_("Dump sql file %s not found!") % dump_file_sql)

        subprocess.Popen(
            [
                f'cat {dump_file_sql} | psql -U {self.pg_user} -p {self.db_port} '
                f'-d {self.env.cr.dbname}_migrate_{self.to_version.name}'
            ],
            shell=True).wait()
        os.unlink(dump_file_sql)

    def button_prepare_migration(self):
        self.ensure_one()
        to_version = self.to_version
        from_version = self.from_version
        restore_db_only = self.restore_db_only
        if self.create_venv:
            self.create_venv_git_version(to_version)
            self.create_venv_git_version(from_version)
        if self.restore_db_update:
            self.dump_database(from_version.name)
            if self.filestore:
                self.restore_filestore(from_version, from_version)
            self.restore_db()
            self.disable_mail(disable=True)
            # n.b. when updating, at the end odoo service is stopped
            self.start_odoo(from_version, update=True)
            self.restore_db_update = False
        # restore db if not restored before, not needed if migration for more version
        elif restore_db_only:
            self.restore_db()
            self.restore_db_only = False
        if self.filestore:
            self.move_filestore(from_version=from_version, to_version=to_version,
                                restore_db_only=restore_db_only)
        self.disable_mail(disable=True)
        # self.sql_fixes(self.env["openupgrader.config"].search([("odoo_version", "=", from_version)]))
        self.uninstall_modules(from_version, before_migration=True)
        self.delete_old_modules(from_version)

    def disable_cron(self, disable=False):
        # disable cron on current running istance, to be re-enabled in the migrated one
        if disable:
            ir_cron_ids = self.env["ir.cron"].search([])
            ir_cron_ids.write({"active": False})
            self.disabled_cron_ids = ir_cron_ids
        if not disable and self.disabled_cron_ids:
            sql = (f"UPDATE ir_cron SET active = true WHERE id in "
                   f"{(_id for _id in self.disabled_cron_ids.ids)};")
            subprocess.Popen(
                [f'psql -p {self.db_port} -d '
                 f'{self.env.cr.dbname}_migrate_{self.to_version.name} -c "{sql}"'],
                shell=True
            )

    def button_do_migration(self):
        self.disable_cron(True)
        to_version = self.to_version
        from_version = self.from_version
        # if to_version == '11.0':
        #     self.fix_taxes(from_version)
        # if to_version == '12.0' and self.fix_banks:
        #     self.fixes.migrate_bank_riba_id_bank_ids(from_version)
        #     self.fixes.migrate_bank_riba_id_bank_ids_invoice(from_version)
        # if from_version == '12.0' and self.migrate_ddt:
        #     self.migrate_l10n_it_ddt_to_l10n_it_delivery_note(from_version)
        self.start_odoo(to_version, update=True)
        self.uninstall_modules(to_version, after_migration=True)
        self.auto_install_modules(to_version)
        self.sql_fixes(self.env["openupgrader.config"].search([
            ("odoo_version", "=", to_version.name)]))
        if to_version.name == '10.0':
            self.start_odoo(to_version)
            self.remove_modules('upgrade')
            self.remove_modules()
            self.install_uninstall_module('l10n_it_intrastat')
            self.stop_odoo()
        self.dump_database(to_version.name)
        # if self.filestore:
        #     self.dump_filestore(to_version.name)
        print(f"Migration done from version {from_version.name} to version {to_version.name}")
        # self.disable_cron() # to be re-enabled manually after all is gone ok
        if self.from_version.name in versions:
            self.from_version = self.to_version
            self.to_version = versions[self.from_version]
            print(f"Set next version to {self.to_version}")

    # def fix_taxes(self, version):
    #     # correzione da fare sulle imposte prima della migrazione alla v.11.0 altrimenti
    #     # non può calcolare correttamente le ex-imposte parzialmente deducibili
    #     self.start_odoo(version)
    #     tax_obj = self.odoo_client.env['account.tax']
    #     for tax in tax_obj.search([
    #         ('children_tax_ids', '!=', False),
    #         ('amount_type', '=', 'group'),
    #     ]):
    #         first_child_amount = 0.0
    #         print('Fixed tax %s' % tax.name)
    #         for child_tax in tax.children_tax_ids:
    #             child_tax.amount_type = 'percent'
    #             if child_tax.amount == 0.0:
    #                 child_tax.amount = (tax.amount * 100) - first_child_amount
    #             else:
    #                 child_tax.amount = tax.amount * child_tax.amount
    #             first_child_amount = child_tax.amount
    #             print('Fixed child tax %s' % child_tax.name)
    #     self.stop_odoo()

    # def migrate_l10n_it_ddt_to_l10n_it_delivery_note(self, version):
    #     self.start_odoo(version)
    #     if self.odoo_client.env['ir.module.module'].search([
    #         ('name', '=', 'l10n_it_ddt'),
    #         ('state', '=', 'installed'),
    #     ]):
    #         self.install_uninstall_module(
    #             'l10n_it_delivery_note', install=True
    #         )
    #         self.stop_odoo()
    #         self.start_odoo(version=version,
    #                         extra_command=f'migrate_l10n_it_ddt -d {self.env.cr.dbname}')

    def sql_fixes(self, receipt):
        for part in receipt:
            bash_commands = part.get('sql_commands', [])
            for bash_command in bash_commands:
                command = [
                    "psql -p %s -d %s -c \'%s\'" % (
                        self.db_port,
                        f"{self.env.cr.dbname}_migrate_{self.to_version.name}",
                        bash_command,
                    )
                ]
                subprocess.Popen(command, shell=True).wait()
            bash_update_commands = part.get('sql_update_commands', [])
            if bash_update_commands:
                for bash_update_command in bash_update_commands:
                    upd_command = [
                        'psql -p %s -d %s -c "%s"' % (
                            self.db_port,
                            f"{self.env.cr.dbname}_migrate_{self.to_version.name}",
                            bash_update_command,
                        )
                    ]
                    subprocess.Popen(upd_command, shell=True).wait()

    def post_migration(self, version):
        # re-enable mail servers and clean db
        self.disable_mail(disable=False)
        # self.database_cleanup(version)

    def create_venv_git_version(self, version):
        openupgrader_repo_obj = self.env["openupgrader.repo"]
        version_repos = openupgrader_repo_obj.search([
            ("odoo_version", "=", version.name),
        ])
        if len(version_repos) != 1:
            raise UserError(_("Version repositories not found!"))
        self.write({
            "repo_ids": [(6, 0, version_repos.ids)],
        })
        openupgrader_config_obj = self.env["openupgrader.config"]
        config_ids = openupgrader_config_obj.search([
            ('odoo_version', '=', version.name),
        ])
        if len(config_ids) != 1:
            raise UserError(_("OpenUpgrader config not found!"))
        self.write({
            "config_ids": [(6, 0, config_ids.ids)],
        })
        # Install OpenUpgrade repository always in ./openupgrade/<version>/openupgrade/
        # Odoo is OpenUpgrade until v. 13.0, from v. 14.0 Odoo is in ./<version/odoo
        odoo_is_openupgrade = False
        if version.name in [
            '7.0', '8.0', '9.0', '10.0', '11.0', '12.0', '13.0'
        ]:
            odoo_is_openupgrade = True
        venv_path = os.path.join(self.folder, version.name)
        openupgrade_path = os.path.join(self.folder, version.name, 'openupgrade')
        odoo_path = os.path.join(self.folder, version.name, 'odoo')
        py_version = version.python_version
        # create virtualenv
        if not os.path.isdir(venv_path):
            subprocess.Popen(['mkdir -p %s' % venv_path], shell=True).wait()
            # do not recreate virtualenv as it regenerate file with bug in split()
            # ../openupgrade10.0/lib/python2.7/site-packages/pip/_internal/vcs/git.py
            subprocess.Popen([
                'virtualenv -p python%s %s' % (py_version, venv_path)],
                shell=True).wait()
        # install odoo Openupgrade repo, from v. 14.0 it contains only migration script
        if not os.path.isdir(openupgrade_path):
            subprocess.Popen([
                'cd %s && git clone --single-branch %s -b %s --depth 1 openupgrade' % (
                    openupgrade_path, self.openupgrade_repo, version.name)
            ], shell=True).wait()
        else:
            subprocess.Popen([
                'cd %s/openupgrade && git reset --hard origin/%s && git pull '
                '&& git reset --hard origin/%s' % (
                openupgrade_path, version.name, version.name
            )], shell=True).wait()
        if not odoo_is_openupgrade:
            # install odoo repo
            self.install_repo("odoo", self.odoo_repo, version.name)
        commands = [
            'bin/pip install "setuptools<58.0.0"',
            'bin/pip install -r odoo/requirements.txt',
            'bin/pip install -r repos/odoo/requirements.txt' if version.name not in [
                '8.0', '9.0', '10.0', '11.0', '12.0', '13.0'] else '',
            'cd odoo && ../bin/pip install -e . ' if version.name in [
                '8.0', '9.0', '10.0', '11.0', '12.0', '13.0'
            ] else 'cd repos/odoo && ../../bin/pip install -e . ',
        ]
        for command in commands:
            subprocess.Popen(command, shell=True).wait()
        extra_paths = ['%s/addons-extra' % odoo_path, '%s/repos' % odoo_path]
        for path in extra_paths:
            if not os.path.isdir(path):
                process = subprocess.Popen('mkdir %s' % path, shell=True)
                process.wait()
        if os.path.isfile(os.path.join(odoo_path, 'migration.log')):
            process = subprocess.Popen(
                'rm %s' % 'migration.log', shell=True)
            process.wait()

        for remote_repo in version_repos.remote_repo_ids:
            self.install_repo(remote_repo.name, remote_repo.remote_url,
                              remote_repo.remote_branch)

    def install_repo(self, repo_name, repo_url, repo_version):
        repo_path = os.path.join(self.folder, 'repos', repo_name)
        if not os.path.isdir(repo_path):
            process = subprocess.Popen([
                f'git clone --single-branch -b {repo_version} {repo_url} --depth 1 '
                f'{repo_path}'
            ], shell=True)
            process.wait()
        process = subprocess.Popen([
            f'git fetch --all && git reset --hard origin/{repo_version}'
        ], shell=True)
        process.wait()
        # copy modules to create a unique addons path
        for root, dirs, files in os.walk(repo_path):
            for d in dirs:
                if d not in ['.git', 'setup']:
                    process = subprocess.Popen([
                        f"cp -rf {repo_path}/{d} {self.folder}/addons-extra/"
                    ], shell=True)
                    process.wait()
            break

    def auto_install_modules(self, version):
        self.start_odoo(version)
        module_obj = self.odoo_client.env['ir.module.module']
        if version == '12.0':
            self.remove_modules('upgrade')
        receipt = self.env["openupgrader.config"].search([("odoo_version", "=", version)])
        for modules in receipt:
            module_list = modules.get('auto_install', False)
            if module_list:
                for module_pair in module_list:
                    module_to_check = module_pair.split(' ')[0]
                    module_to_install = module_pair.split(' ')[1]
                    if module_obj.search([
                            ('name', '=', module_to_check),
                            ('state', '=', 'installed')]):
                        self.odoo_client.env.install(module_to_install)
        self.stop_odoo()

    def uninstall_modules(self, version, before_migration=False, after_migration=False):
        version_name = version.name
        self.start_odoo(version_name)
        if version_name == '12.0':
            self.remove_modules('upgrade')
        receipt = self.env["openupgrader.config"].search([("odoo_version", "=", version_name)])
        for modules in receipt:
            if after_migration:
                modules_to_uninstall = modules.get('uninstall_after_migration_to_this_version', False)
                if modules_to_uninstall:
                    for module in modules_to_uninstall:
                        self.install_uninstall_module(module, install=False)
            if before_migration:
                modules_to_uninstall = modules.get('uninstall_before_migration_to_next_version', False)
                if modules_to_uninstall:
                    for module in modules_to_uninstall:
                        self.install_uninstall_module(module, install=False)
        self.stop_odoo()

    def delete_old_modules(self, version):
        receipt = self.env["openupgrader.config"].search([
            ("odoo_version", "=", version.name)])
        if receipt.module_to_delete_after_migration_ids:
            self.start_odoo(version.name)
            module_obj = self.odoo_client.env['ir.module.module']
            for module in receipt.module_to_delete_after_migration_ids:
                module = module_obj.search([
                    ('name', '=', module)])
                if module:
                    module_obj.unlink(module.id)
            self.stop_odoo()

    def remove_modules(self, module_state=''):
        if module_state == 'upgrade':
            state = ['to upgrade', ]
        else:
            state = ['to remove', 'to install']
        module_obj = self.odoo_client.env['ir.module.module']
        modules = module_obj.search([('state', 'in', state)])
        msg_modules = ''
        msg_modules_after = ''
        if modules:
            msg_modules = str([x.name for x in modules])
        for module in modules:
            module.button_uninstall_cancel()
        modules_after = module_obj.search(
            [('state', '=', 'to upgrade')])
        if modules_after:
            msg_modules_after = str([x.name for x in modules_after])
        print('Modules: %s' % msg_modules)
        print('Modules after: %s' % msg_modules_after)

    @staticmethod
    def uninst(module_to_uninstall, module_to_unistall_id, success):
        try:
            module_to_unistall_id.button_immediate_uninstall()
            module_to_unistall_id.unlink()
            print('Module %s uninstalled' % module_to_uninstall)
            success = 5
        except Exception as e:
            print(
                'Module %s not uninstalled for %s, trying %s/%s times.' % (
                    module_to_uninstall, str(e).replace('\n', ''), success + 1, 5)
            )
            time.sleep(10)
            success += 1
        return success

    def install_uninstall_module(self, module, install=True):
        module_obj = self.odoo_client.env['ir.module.module']
        to_remove_modules = module_obj.search(
            [('state', '=', 'to remove')])
        for module_to_remove in to_remove_modules:
            module_to_remove.button_uninstall_cancel()
        state = self.odoo_client.env.modules(module)
        if state:
            if install:
                self.odoo_client.env.install(module)
            elif state.get('installed', False) or state.get('to upgrade', False)\
                    or state.get('uninstallable'):
                module_id = module_obj.search([('name', '=', module)])
                if module_id:
                    res = 0
                    while res < 5:
                        res = self.uninst(module, module_id, res)
                else:
                    print('Module %s not found' % module)
