import functools
import logging

from odoo.tools.config import config as system_base_config

logger = logging.getLogger(__name__)


def running(func):
    @functools.wraps(func)
    def wrap(*args, **kwargs):
        if not system_base_config.get("running_env"):
            system_base_config["running_env"] = "test"
        server_running_state = system_base_config.get("running_env")
        if server_running_state in ["prod", "migr"]:
            result = func(*args, **kwargs)
        else:
            logger.info(
                f"Server state != prod or migr, ignored {func.__name__} function"
            )
            result = False
        return result

    return wrap
