import sys, os 
from dotenv import load_dotenv

from util.json_utils import load_json_file
from log.Logger import Logger

load_dotenv(os.path.join(os.path.abspath('./'), '.env'))


class Main_Client():

    def __init__(self):
        self.load_cfg()
        self.load_log()
        self.get_cfg_data()
        self.get_importers()
        self.setup()
        self.log.info("MAIN:: Init System")
        self.run()
        return 
    
    def get_cfg_data(self): return 

    def get_importers(self): return 
    
    def setup(self): return

    def run(self): return
    
    def load_cfg(self):
        cfg_path = os.environ.get("CFG_PATH")
        self.cfg = load_json_file(cfg_path)
        if self.cfg is None:
            sys.exit(f"Error: Not found cfg on {cfg_path}!")
        return

    def load_log(self):

        def log_errors(exc_type, exc_value, exc_traceback):
            """
                Logging unhandled exceptions
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
                print(f"Error building log dir => {e}")
        self.log = log_manager.build_logger(
            "main_log",
            log_dir,
            storage_days=self.cfg.get('log').get('log_storage_days'),
            console_handler=True,
        )
        sys.excepthook = log_errors
        return
    
    
    
    
    
main = Main_Client()