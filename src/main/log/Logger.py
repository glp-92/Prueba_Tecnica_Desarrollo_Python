from logging.handlers import TimedRotatingFileHandler
import logging, os

class Logger:

    def __new__(cls, *args, **kwargs):
        return super(Logger, cls).__new__(cls)

    def __init__(self):
        return

    def build_logger(self, log_name: str, log_path: str, storage_days: int = 7, console_handler: bool = True):
        """
            Funcion que permite crear Logs

            args:
                log_name: nombre que identificara al log al que se añade la extension (log_main..)
                log_path: ruta absoluta o relativa que conduce al directorio donde se almacenaran los logs
                storage_days: el handler permite hacer autoborrado superado cierto numero de logs. Se ha ajustado para haber 1 log diario y almacenar hasta storage_days logs
                console_handler: si se desea que se imprima en terminal lo mismo que se almacena en el log

            returns:
                logger: objeto que permite escribir en el log (log.info, warning, error...)
        """
        logger = logging.getLogger(log_name)
        if (logger.hasHandlers()):
            logger.handlers.clear()
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s', datefmt = '%d/%m/%Y %H:%M:%S')
        fileHandler = TimedRotatingFileHandler(os.path.join(log_path, f"{log_name}.log"), when = 'midnight', backupCount = storage_days)
        fileHandler.setLevel(logging.DEBUG)
        fileHandler.setFormatter(formatter)
        logger.addHandler(fileHandler)
        if console_handler:
            consoleHandler = logging.StreamHandler()
            consoleHandler.setLevel(logging.DEBUG)
            logger.addHandler(consoleHandler)
        #logger.propagate = False
        return logger
    

if __name__ == '__main__':
    logger_manager = Logger()