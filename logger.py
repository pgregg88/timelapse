import logging
from logger import setup_logging

def setup_logging(log_path):
    # Create a logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # Create a file handler and set its log level to INFO
    fh = logging.FileHandler(log_path)
    fh.setLevel(logging.INFO)
    
    # Create a stream handler and set its log level to INFO
    sh = logging.StreamHandler()
    sh.setLevel(logging.INFO)

    # Create a formatter and add it to the handler
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    fh.setFormatter(formatter)
    sh.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(sh)

    return logger
