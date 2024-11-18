import logging
try:
    from rich.logging import RichHandler
except ImportError:
    RichHandler = None
from sys import stderr

class LoggingClass:
    # Mirror the standard logging constants
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL

    # Static variable for global access to default logger
    rootlogger = None

    # Formatting
    _log_format = "%(asctime)s %(name)s[%(process)d]: %(levelname)s: %(message)s"
    _date_format = "%Y-%m-%d %H:%M:%S"

    LOG_LEVELS = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL,
    }

    def __init__(self, loggerName: str, logFile: str = 'latest.log', consoleLevel: str | int = logging.ERROR, fileLevel: str | int = logging.INFO):
        if isinstance(consoleLevel, str):
            consoleLevel = self.LOG_LEVELS[consoleLevel.upper()]
        if isinstance(fileLevel, str):
            fileLevel = self.LOG_LEVELS[fileLevel.upper()]

        self._setup_logging(loggerName, logFile, consoleLevel, fileLevel)
    def _setup_logging(self, loggerName: str, logFile: str = 'latest.log', consoleLevel: str | int = logging.ERROR, fileLevel: str | int = logging.INFO) -> logging.Logger:
        # TODO: Consider adding a default logger name of self.__class__.__name__, or "bpe_app"

        # # If the default logger is already defined, just return that
        # if LoggingClass.rootlogger is not None:
        #     return LoggingClass.rootlogger
        
        if isinstance(consoleLevel, str):
            consoleLevel = self.LOG_LEVELS[consoleLevel.upper()]
        if isinstance(fileLevel, str):
            fileLevel = self.LOG_LEVELS[fileLevel.upper()]
            
        # Setup the common configuration
        self._logger = logging.getLogger(loggerName)
        
        file_handler = logging.FileHandler(logFile)
        file_handler.setFormatter(logging.Formatter(LoggingClass._log_format, LoggingClass._date_format))
        file_handler.setLevel(fileLevel)
        self._logger.addHandler(file_handler)

        # Set up logging to stderr, using rich to colorize the output
        if RichHandler is not None:
            console_handler = RichHandler()
        else:
            console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(LoggingClass._log_format, LoggingClass._date_format))
        console_handler.setLevel(consoleLevel)
        self._logger.addHandler(console_handler)

        if LoggingClass.rootlogger is None:
            LoggingClass.rootlogger = self._logger

        return self._logger

    @classmethod
    def info(cls, message: str, **kwargs):
        cls.getRootLogger().info(message, **kwargs)
    
    @classmethod
    def debug(cls, message: str, **kwargs):
        cls.getRootLogger().debug(message, **kwargs)

    @classmethod
    def warning(cls, message: str, **kwargs):
        cls.getRootLogger().warning(message, **kwargs)

    @classmethod
    def error(cls, message: str, **kwargs):
        cls.getRootLogger().error(message, **kwargs)

    @classmethod
    def critical(cls, message: str, **kwargs):
        cls.getRootLogger().critical(message, **kwargs)

    @classmethod
    def exception(cls, message: str, **kwargs):
        cls.getRootLogger().exception(message, **kwargs)

    @classmethod
    def getRootLogger(cls) -> logging.Logger:
        if cls.rootlogger is not None:
            return cls.rootlogger
        else:
            stderr.write("*** ERROR: The root logger(LoggingClass) has not been initialized yet.\nPlease initialize at least one LoggingClass object first.\n")
            return None
    # def getLogger(self, loggerName: str = None, autoInit: bool = True, logFile: str = 'latest.log', consoleLevel: str | int = logging.ERROR, fileLevel: str | int = logging.INFO):
    #     # TODO: Consider applying settings to the default logger when loggerName is None
    #       if isinstance(consoleLevel, str):
    #           consoleLevel = self.LOG_LEVELS[consoleLevel.upper()]
    #       if isinstance(fileLevel, str):
    #           fileLevel = self.LOG_LEVELS[fileLevel.upper()]
            
    #     if loggerName is None:
    #         return logging.getLogger()
        
    #     # For now, any loggerName will return the LoggingClass._logger if it exists
    #     if LoggingClass._logger is not None:
    #         return LoggingClass._logger

    #     if autoInit:
    #         return self._setup_logging(loggerName, logFile, consoleLevel, fileLevel)
    #     else:
    #         # print to stderr that the logger isn't initialized
    #         stderr.write(f"Logger {loggerName} is not initialized.\nPlease setup the logger first, or call getLogger(loggerName, autoInit=True) to initialize with default settings.\n")
    #         return None