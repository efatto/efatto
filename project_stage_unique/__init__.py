from . import models
import logging

logger = logging.getLogger(__name__)


def pre_init_hook(cr):
    logger.info("Update project task type name to be unique")
    # This work for source term, translation terms are not considered.
    cr.execute(
        """
        UPDATE project_task_type SET name = CONCAT(name, '_', id) WHERE
            id not in (SELECT min(id) from project_task_type group by name)
    """
    )
