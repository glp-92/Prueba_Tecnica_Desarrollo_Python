import sys, os 
from dotenv import load_dotenv

from util.json_utils import load_json_file
from log.Logger import Logger

load_dotenv(os.path.join(os.path.abspath('./'), '.env'))


class Main_Client():

    def __init__(self):
        self.load_cfg()
        self.load_log()
        self.setup()
        self.log.info("MAIN:: Systema inicializado")
        self.run()
        return 
    
    def setup(self): return

    def run(self): return
    
    def load_cfg(self):
        cfg_path = os.environ.get("CFG_PATH")
        self.cfg = load_json_file(cfg_path)
        if self.cfg is None:
            sys.exit(f"Error: Fichero de configuracion no encontrado en ruta {cfg_path}!")
        return

    def load_log(self):

        def log_errors(exc_type, exc_value, exc_traceback):
            """
                Log de las excepciones no controladas que puedan detener la ejecucion del programa
            """
            if issubclass(exc_type, KeyboardInterrupt):
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return
            self.log.error(
                "UNCAUGHT EXCEPTION", exc_info=(exc_type, exc_value, exc_traceback)
            )

        log_manager = Logger()
        log_dir = os.environ.get("LOG_DIR")
        if not os.path.exists(log_dir):
            try:
                os.makedirs(f"{log_dir}")
            except Exception as e:
                print(f"Error en creacion de directorio de logs => {e}")
        self.log = log_manager.build_logger(
            "main_log",
            log_dir,
            storage_days=self.cfg.get('log').get('log_storage_days'),
            console_handler=True,
        )
        sys.excepthook = log_errors
        return
    
    
    
    
    
main = Main_Client()