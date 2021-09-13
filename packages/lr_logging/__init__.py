import os

from lr_logging.exceptions import *
from lr_logging.responses import *


def get_cloudlogbase_config() -> str:
    """Returns the log definition config file

    To be passed into the initialisation of spine-aws-common classes to provide
    log message definitions"""
    cwd: str = os.path.dirname(__file__)
    return os.path.join(cwd, "list_reconciliation_logs.cfg")
