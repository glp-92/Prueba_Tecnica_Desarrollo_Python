"""
    Args:
        mockup: sensor simulador que envia datos al topic
        sensorfreq: frecuencia de lectura de datos del sensor
        valrange: rango valores del sensor mockup si es simulado
        dburi: uri de db
    python main.py --mockupsensor=True --valrange=0-1000 --sensorfreq=1 --dburl=localhost
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
parser.add_argument('--sensorfreq', type=float, required=True, help='Frecuencia de lectura (en s) de los datos que envia el sensor')
parser.add_argument('--valrange', type=str, required=False, help='Rango de valores si el sensor esta simulado')
parser.add_argument('--dburl', type=str, required=True, help='Direccion de la base de datos')
args = parser.parse_args()

mockup_sensor = str_to_bool(args.mockupsensor)
sensorfreq = args.sensorfreq
valrange = args.valrange
if mockup_sensor:
    if valrange:
        try:
            range_values = list(map(lambda v: int(v), valrange.split("-")))
            range_values = (min(range_values), max(range_values))
            print(range_values)
            if range_values[0] < 0 or range_values[1] > 65535: raise argparse.ArgumentTypeError("Out of range int16")
        except Exception as e:
            raise argparse.ArgumentTypeError('Expected range expressed by "minval-maxval"')
db_url = args.dburl

from log.Logger import Logger
from controller.Sensor_Controller import Sensor_Controller
from data.MySQL_Sensor_Repository import MySQL_Sensor_Repository
from db.MySQL import MySQL
from com.Nats import Nats_Client

load_dotenv(os.path.join(os.path.abspath('../../'), '.env'))

class Main_Client():

    running = False

    def __init__(self):
        self.load_log()
        self.get_importers()
        self.log.info("MAIN:: System Ready")
        self.set_run_stop_signal()
        return

    def set_run_stop_signal(self):
        signal.signal(signal.SIGTSTP, self.run) # CTRL + Z calls run?
        return

    def get_importers(self): 
        self.mysql_client = MySQL(self.log, db_url=db_url)
        self.sensor_repository = MySQL_Sensor_Repository(self.log, mysql_connection=self.mysql_client.connection)
        self.nats_client = Nats_Client(self.log, client_id=os.environ.get('CLIENT_ID'))
        self.sensor_controller = Sensor_Controller(self.log, nats_client=self.nats_client, sensor_repository=self.sensor_repository)
        return 

    def run(self, sig, frame):
        signal.signal(signal.SIGTSTP, signal.SIG_IGN) # signal disconnect
        if not self.running: # Run threads
            self.sensor_controller.setup_handlers()
            self.listen_thread = None
            self.listen_thread = Thread(target=self.sensor_controller.listen, args=(sensorfreq,), daemon=True)
            self.listen_thread.start()
        else:
            # self.loop.call_soon_threadsafe(self.loop.stop)
            self.sensor_controller.running = True
            self.listen_thread.join()
            self.log.warning(f"MAIN:: Hilo de escucha detenido!")
        self.running = not self.running
        signal.signal(signal.SIGTSTP, self.run) # signal reconnect
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