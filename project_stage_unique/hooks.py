import logging

logger = logging.getLogger(__name__)


def pre_init_hook(env):
    logger.info("Update project task type name to be unique")
    langs = env["res.lang"].search([])
    for lang in langs:
        lang_code = lang.code
        env.cr.execute(
            f"""
            UPDATE project_task_type SET name = name || jsonb_build_object(
                '{lang_code}', (name->>'{lang_code}') || '_' || id::text
            ) WHERE id NOT IN (
                SELECT MIN(id) FROM project_task_type GROUP BY name->>'{lang_code}'
            ) AND name ? '{lang_code}'
        """
        )
