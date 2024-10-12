import logging
import os

def setup_logger(name=None):
    # Use the provided name or the name of the file calling the logger
    if name is None:
        name = os.path.basename(__file__)
    
    # Create a custom logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Create handlers
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)  # Logs INFO level to the console

    file_handler = logging.FileHandler('app.log')
    file_handler.setLevel(logging.DEBUG)  # Logs all levels to the file

    # Create formatters and add them to handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger