from psycopg2 import sql

from . import models
import logging

logger = logging.getLogger(__name__)


def pre_init_hook(cr):
    logger.info("Update project task type name to be unique")
    # This work for source and translation terms
    # cr.execute("SELECT code FROM res_lang WHERE active=true")
    # lang_codes = [x[0] for x in cr.fetchall()]
    # UPDATE project_task_type
    # SET name = jsonb_set(
    #     name,
    #     '{en_US}',
    #     '"mieao"'::jsonb) where name @> '{"en_US": "miea"}'::jsonb;
    # for lang_code in lang_codes:
    # set the uniqueness only on the default language
    # es. funzionante:
    # update utm_source set name = jsonb_set(
    # name, '{en_US}', '"Novità fattura elettronica 2021 (copia1)"') where id = 8;
    # es. lettura: select name->'en_US' from utm_source; (non funziona con -->)
    lang_code = "en_US"
    new_name_field = sql.SQL("{field}-->{key}").format(
        field=sql.Literal("name"), key=sql.Literal(lang_code)
    )
    field_position = sql.SQL(f"{{{lang_code}}}")
    query = sql.SQL(
        """
            UPDATE project_task_type
                SET name = jsonb_set(
                    name,
                    '{en_US}',
                    CONCAT(
                        ''"', name->'en_US', '_', id, '"''
                    )
                )
                WHERE id not in (
                    SELECT min(id) from project_task_type group by name-->'en_US'
                )
        """
    ).format(
        new_name_field=new_name_field,
        field_name=sql.Identifier("name"),
        field_position=field_position,
    )
    cr.execute(query)
