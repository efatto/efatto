from . import models
import logging

logger = logging.getLogger(__name__)


def pre_init_hook(env):
    logger.info("Update project task type name to be unique")
    env.cr.execute(
        """
        UPDATE project_task_type SET name = name || jsonb_build_object(
            'en_US', (name->>'en_US') || '_' || id::text
        ) WHERE id NOT IN (
            SELECT MIN(id) FROM project_task_type GROUP BY name->>'en_US'
        ) AND name ? 'en_US'
    """
    )
    # Also handle cases where en_US might be missing but name exists as a string
    # (legacy) though in Odoo 18 it should already be jsonb
    env.cr.execute(
        """
        UPDATE project_task_type SET name = jsonb_build_object(
            'en_US', (name#>>'{}') || '_' || id::text
        )
        WHERE id NOT IN (
            SELECT MIN(id) FROM project_task_type GROUP BY name#>>'{}'
        ) AND jsonb_typeof(name) != 'object'
    """
    )
