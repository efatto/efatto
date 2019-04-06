from openupgradelib import openupgrade


def account_templates(env):
    # ## re-run 9.0 migration for renamed chart ##
    # assign a chart template to configured companies in order not to
    # have the localization try to generate a new chart of accounts
    cr = env.cr
    account_templates = env['account.chart.template'].search([])
    configurable_template = env.ref('account.configurable_chart_template')
    account_templates -= configurable_template
    cr.execute('select distinct company_id from account_account where active')
    for company in env['res.company'].browse([i for i, in cr.fetchall()]):
        if company.chart_template_id:  # pragma: no cover
            # probably never happens, but we need to be sure not to overwrite
            # this anyways
            continue
        if len(account_templates) == 1:  # pragma: no cover
            # if there's only one template, we can be quite sure that's the
            # right one
            company.write({
                'chart_template_id': account_templates.id,
                # 'transfer_account_id': account_templates.transfer_account_id.id
            })
            continue


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    account_templates(env)