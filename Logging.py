import logging

def setup_logging():
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # Set global logging level to DEBUG for all handlers

    # Remove existing handlers from the logger (if any)
    for handler in logger.handlers[:]:  # Make a copy of the list before iterating
        logger.removeHandler(handler)

    # Define log format
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    # Create file handler for detailed logs
    file_handler = logging.FileHandler('app.log')
    file_handler.setLevel(logging.DEBUG)  # Set log level for file handler
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
