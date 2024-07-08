"""
    Args:
        mockup: sensor simulador que envia datos al topic
        sensorfreq: frecuencia de lectura de datos del sensor
        valrange: rango valores del sensor mockup si es simulado
        dburi: uri de db
    python main.py  --mockupsensor True --sampletime 5 --dburl localhost
"""
import sys, os, signal, time, argparse
from dotenv import load_dotenv
from threading import Thread

def str_to_bool(value):
    if isinstance(value, bool): return value
    if value.lower() in ('yes', 'true', 't', 'y', '1'): return True
    elif value.lower() in ('no', 'false', 'f', 'n', '0'): return False
    else: raise argparse.ArgumentTypeError('Boolean value expected.')

parser = argparse.ArgumentParser(description='Programa principal:: Predicción de precio de vivienda')
parser.add_argument('--mockupsensor', type=str, required=True, help='True para simular un sensor que envia datos')
parser.add_argument('--sampletime', type=float, required=True, help='Frecuencia de lectura (en s) de los datos que envia el sensor')
parser.add_argument('--valrange', type=str, required=False, help='Rango de valores si el sensor esta simulado')
parser.add_argument('--dburl', type=str, required=True, help='Direccion de la base de datos')
args = parser.parse_args()

mockup_sensor = str_to_bool(args.mockupsensor)
sampletime = args.sampletime
valrange = args.valrange
if mockup_sensor:
    if valrange:
        try:
            range_values = list(map(lambda v: int(v), valrange.split("-")))
            range_values = (min(range_values), max(range_values))
            if range_values[0] < 0 or range_values[1] > 65535: raise argparse.ArgumentTypeError("Out of range int16")
        except Exception as e:
            raise argparse.ArgumentTypeError('Expected range expressed by "minval-maxval"')
db_url = args.dburl

from log.Logger import Logger
from controller.Sensor_Controller import Sensor_Controller
from data.MySQL_Sensor_Repository_Impl import MySQL_Sensor_Repository_Impl
from db.MySQL import MySQL
from com.Nats import Nats_Client
from scheduler_tasks.Push_To_DB_Records import Push_To_DB_Records
from service.Sensor_Service import Sensor_Service

load_dotenv(os.path.join(os.path.abspath('../../'), '.env'))

class Main_Client():

    push_to_db_task_thread = None
    topic_listener_thread = None

    def __init__(self):
        self.load_log()
        self.get_importers()
        self.log.info("MAIN:: System Ready")
        return

    def get_importers(self): 
        self.mysql_client = MySQL(self.log, db_url=db_url)
        self.sensor_repository = MySQL_Sensor_Repository_Impl(self.log, mysql_connection=self.mysql_client.connection)
        self.nats_client = Nats_Client(self.log, client_id=os.environ.get('CLIENT_ID'))
        self.sensor_service = Sensor_Service(self.log, self.sensor_repository)
        self.sensor_controller = Sensor_Controller(self.log, nats_client=self.nats_client, sensor_service=self.sensor_service)
        self.push_to_db_records = Push_To_DB_Records(self.log, sensor_service=self.sensor_service, push_frequency=sampletime)
        return 

    def run(self):
        signal.signal(signal.SIGTSTP, signal.SIG_IGN) # signal disconnect

        def run_topic_listener():
            self.sensor_controller.setup_topic_handlers()
            self.sensor_controller.start()

        def run_push_to_db_cycle():
            self.push_to_db_records.setup_signal_handlers()
            self.push_to_db_records.start()
        
        self.push_to_db_task_thread = Thread(target=run_push_to_db_cycle, daemon=True)
        self.push_to_db_task_thread.start()
        self.topic_listener_thread = Thread(target=run_topic_listener, daemon=True)
        self.topic_listener_thread.start()
        return
    
    def stop(self):
        self.push_to_db_records.stop()
        self.push_to_db_task_thread.join()
        self.push_to_db_task_thread = None # Reusable thread var
        self.sensor_controller.stop()
        self.topic_listener_thread.join()
        self.topic_listener_thread = None # Reusable thead varç
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


if __name__ == "__main__":
    main = Main_Client()
    main.run()
    while True:
        time.sleep(0.1) # thread not exhausted