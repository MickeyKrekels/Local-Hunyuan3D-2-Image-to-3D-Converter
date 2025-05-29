import logging

class Logger:
    """
    A refined application logger class for consistent logging across the project.
    Provides methods for info, warning, and error logging.
    """
    def __init__(self, name=__name__):
        """
        Initialize the AppLogger instance.

        Args:
            name (str): The name of the logger, typically __name__ from the caller.
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s')
        handler.setFormatter(formatter)
        if not self.logger.handlers:
            self.logger.addHandler(handler)

    def get_logger(self):
        """
        Get the underlying logger instance.

        Returns:
            logging.Logger: The configured logger instance.
        """
        return self.logger

    def info(self, message):
        """
        Log an informational message.

        Args:
            message (str): The message to log.
        """
        self.logger.info(message)

    def warning(self, message):
        """
        Log a warning message.

        Args:
            message (str): The warning message to log.
        """
        self.logger.warning(message)

    def error(self, message):
        """
        Log an error message.

        Args:
            message (str): The error message to log.
        """
        self.logger.error(message)
