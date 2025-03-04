import logging


def setup_logging():
    """
    Setups logging configuration.
    """
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger = logging.getLogger("transactions-storage")
    logger.setLevel(logging.INFO)
    logger.addHandler(console_handler)

    return logger


logger = setup_logging()
