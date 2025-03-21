import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# logger.setLevel(logging.DEBUG)

# set and configure console logging handler
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# format
format_str = "%(asctime)s %(levelname)s %(message)s"
formatter = logging.Formatter(format_str)
ch.setFormatter(formatter)

logger.addHandler(ch)
