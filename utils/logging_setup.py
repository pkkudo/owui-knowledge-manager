import logging


def setup_logger(name):
    """
    Sets up a logger with a given name, and whether to set debug level logging.

    Args:
        name: The name of the logger.
        debug: Boolean to enable DEBUG level logging or not (defaults to INFO)

    Returns:
        A logger instance.
    """

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # set and configure console logging handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # format
    format_str = "%(asctime)s %(levelname)s %(message)s"
    formatter = logging.Formatter(format_str)
    ch.setFormatter(formatter)

    logger.addHandler(ch)

    return logger


# Example usage (optional - can be used directly in other modules)
if __name__ == "__main__":
    logger = setup_logger(__name__)
    logger.debug("This is a debug message.")
    logger.info("This is an info message.")
    logger.warning("This is a warning message.")
    logger.error("This is an error message.")
