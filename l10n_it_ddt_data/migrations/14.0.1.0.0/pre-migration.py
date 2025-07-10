from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    if not version:
        return
    # Remove xmlids before uninstalling the module
    to_remove_xmlids = [
        "l10n_it_ddt_data.ddt_type_ddt_accredito",
        "l10n_it_ddt_data.ddt_type_ddt_clavorazione",
        "l10n_it_ddt_data.ddt_type_ddt_comodato",
        "l10n_it_ddt_data.ddt_type_ddt_creso",
        "l10n_it_ddt_data.ddt_type_ddt_cresoforn",
        "l10n_it_ddt_data.ddt_type_ddt_criparazione",
        "l10n_it_ddt_data.ddt_type_ddt_criparazione_garanzia",
        "l10n_it_ddt_data.ddt_type_ddt_csostituzione_garanzia",
        "l10n_it_ddt_data.ddt_type_ddt_ctrasferimento",
        "l10n_it_ddt_data.ddt_type_ddt_cvendita",
        "l10n_it_ddt_data.ddt_type_ddt_cvisione",
        "l10n_it_ddt_data.ddt_type_ddt_installazione",
        "l10n_it_ddt_data.ddt_type_ddt_noleggio",
        "l10n_it_ddt_data.ddt_type_ddt_omaggio",
        "l10n_it_ddt_data.ddt_type_ddt_reso_clavorazione",
        "l10n_it_ddt_data.ddt_type_ddt_reso_criparazione",
        "l10n_it_ddt_data.ddt_type_ddt_reso_cvisione",
        "l10n_it_ddt_data.ddt_type_ddt_reso_noleggio",
        "l10n_it_ddt_data.ddt_type_ddt_resocriparazione_garanzia",
        "l10n_it_ddt_data.ddt_type_ddt_sostituzione",
    ]
    openupgrade.delete_records_safely_by_xml_id(
        env,
        to_remove_xmlids,
    )
