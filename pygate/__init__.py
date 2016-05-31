__author__ = 'sasinda'
import os
import json
import logging.config


def setup_logging(
        default_path='./logging.json',
        default_level=logging.INFO,
        env_key='LOG_CFG'
):
    """Setup logging configuration
    """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)

setup_logging()

#     Actual immports to init.
from doc import *
from annotation import Annotation
from prs import rule as rule, ml as ml
from pipe import *

import export as export
import ext as ext
import utils as utils