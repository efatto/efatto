-- the healthcheck URL usually embeds the check token: drop it, so copies of the
-- database do not report their backups to the production monitoring service
DELETE FROM ir_config_parameter
 WHERE key = 'auto_backup_healthcheck.url';
