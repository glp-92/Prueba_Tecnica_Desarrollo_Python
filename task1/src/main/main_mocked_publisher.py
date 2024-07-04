import sys, os, signal, time
from dotenv import load_dotenv

from log.Logger import Logger
from controller.Sensor_Controller import Sensor_Controller
from data.MySQL_Sensor_Repository import MySQL_Sensor_Repository
from db.MySQL import MySQL
from com.Nats import Nats_Client

load_dotenv(os.path.join(os.path.abspath('../../'), '.env'))



class Main_Client():

    db_url = 'localhost'

    def __init__(self):
        self.load_log()
        self.get_importers()
        self.log.info("MAIN:: Init System")
        signal.signal(signal.SIGINT, self.run) # CTRL + C calls run??
        

    def get_importers(self): 
        self.mysql_client = MySQL(self.log, db_url=self.db_url)
        self.sensor_repository = MySQL_Sensor_Repository(self.log, mysql_connection=self.mysql_client.connection)
        self.nats_client = Nats_Client(self.log, client_id=os.environ.get('CLIENT_ID'))
        self.sensor_controller = Sensor_Controller(self.log, nats_client=self.nats_client, sensor_repository=self.sensor_repository)
        return 

    def run(self, sig, frame):
        loop = self.sensor_controller.setup_topic_handlers()
        self.sensor_controller.listen(loop=loop)
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
            storage_days=os.environ.get("LOG_STORAGE_DAYS"),
            console_handler=True,
        )
        sys.excepthook = log_errors
        return
    
    
    
    
    
main = Main_Client()
while True:
    time.sleep(0.1) # thread not exhausted