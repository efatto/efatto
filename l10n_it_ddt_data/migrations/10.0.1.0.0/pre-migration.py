# -*- coding: utf-8 -*-

from openupgradelib import openupgrade


xmlid_renames = [
    ('stock_ddt_data.ddt_type_ddt_creso',
     'l10n_it_ddt_data.ddt_type_ddt_creso'),
    ('stock_ddt_data.ddt_type_ddt_cresoforn',
     'l10n_it_ddt_data.ddt_type_ddt_cresoforn'),
    ('stock_ddt_data.ddt_type_ddt_cvisione',
     'l10n_it_ddt_data.ddt_type_ddt_cvisione'),
    ('stock_ddt_data.ddt_type_ddt_reso_cvisione',
     'l10n_it_ddt_data.ddt_type_ddt_reso_cvisione'),
    ('stock_ddt_data.ddt_type_ddt_accredito',
     'l10n_it_ddt_data.ddt_type_ddt_accredito'),
    ('stock_ddt_data.ddt_type_ddt_sostituzione',
     'l10n_it_ddt_data.ddt_type_ddt_sostituzione'),
    ('stock_ddt_data.ddt_type_ddt_clavorazione',
     'l10n_it_ddt_data.ddt_type_ddt_clavorazione'),
    ('stock_ddt_data.ddt_type_ddt_reso_clavorazione',
     'l10n_it_ddt_data.ddt_type_ddt_reso_clavorazione'),
    ('stock_ddt_data.ddt_type_ddt_criparazione',
     'l10n_it_ddt_data.ddt_type_ddt_criparazione'),
    ('stock_ddt_data.ddt_type_ddt_reso_criparazione',
     'l10n_it_ddt_data.ddt_type_ddt_reso_criparazione'),
    ('stock_ddt_data.ddt_type_ddt_criparazione_garanzia',
     'l10n_it_ddt_data.ddt_type_ddt_criparazione_garanzia'),
    ('stock_ddt_data.ddt_type_ddt_resocriparazione_garanzia',
     'l10n_it_ddt_data.ddt_type_ddt_resocriparazione_garanzia'),
    ('stock_ddt_data.ddt_type_ddt_csostituzione_garanzia',
     'l10n_it_ddt_data.ddt_type_ddt_csostituzione_garanzia'),
    ('stock_ddt_data.ddt_type_ddt_omaggio',
     'l10n_it_ddt_data.ddt_type_ddt_omaggio'),
    ('stock_ddt_data.ddt_type_ddt_comodato',
     'l10n_it_ddt_data.ddt_type_ddt_comodato'),
    ('stock_ddt_data.ddt_type_ddt_installazione',
     'l10n_it_ddt_data.ddt_type_ddt_installazione'),
    ('stock_ddt_data.ddt_type_ddt_noleggio',
     'l10n_it_ddt_data.ddt_type_ddt_noleggio'),
    ('stock_ddt_data.ddt_type_ddt_reso_noleggio',
     'l10n_it_ddt_data.ddt_type_ddt_reso_noleggio'),
    ('stock_ddt_data.ddt_type_ddt_ctrasferimento',
     'l10n_it_ddt_data.ddt_type_ddt_ctrasferimento'),
]


def migrate(cr, version):
    # This is not decorated with @openupgrade.migrate as the module is being
    # installed and thus, the migration script should be run unconditionally
    openupgrade.rename_xmlids(cr, xmlid_renames)
