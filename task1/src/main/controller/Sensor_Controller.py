import os, asyncio, time

from schemas.requests.Data_Received import Data_Received
from service.Sensor_Service import Sensor_Service

class Sensor_Controller:

    def __init__(self, log, nats_client, sensor_repository):
        self.log = log 
        self.nats_client = nats_client
        self.sensor_repository = sensor_repository
        self.get_importers()
        self.running = False

    def get_importers(self): 
        self.sensor_service = Sensor_Service(self.log, self.sensor_repository)
        return 
    
    def setup_handlers(self): # Call from main (start-stop)
        asyncio.run(self.nats_client.connect(os.environ.get("NATS_SERVER_URL")))
        asyncio.run(self.nats_client.subscribe_to_channel(os.environ.get('NATS_SENSOR_CHANNEL'), self.on_sensor_data_received))
    
    def listen(self, time_to_sleep_seconds):
        self.running = False
        self.log.info("SENSOR_CONTROLLER:: Listening...")
        while not self.running:
            self.log.info(f"SENSOR_CONTROLLER:: Pushing readings to DB...")
            self.push_readings_to_db()
            time.sleep(time_to_sleep_seconds)
        asyncio.run(self.nats_client.unsuscribe_to_channel(os.environ.get('NATS_SENSOR_CHANNEL')))
        self.log.info("SENSOR_CONTROLLER:: Unsubbed to channel")
        asyncio.run(self.nats_client.disconnect())


    async def on_sensor_data_received(self, new_msg_from_sensor):
        try:
            new_msg_from_sensor = Data_Received(**new_msg_from_sensor)
            self.sensor_service.add_reading_to_queue()
        except TimeoutError as e:
            self.log.error(f"SENSOR_CONTROLLER:: Timeout while pushing read values to queue {e}")
        except ValueError as e:
            self.log.error(f"SENSOR_CONTROLLER:: ValueError: {e}")
            return
        except IOError as e:
            self.log.error(f"SENSOR_CONTROLLER:: I/O Err: {e}")
        except Exception as e:
            self.log.error(f"SENSOR_CONTROLLER:: Unhandled exception: {e}")
        return

    
    def push_readings_to_db(self):
        try:
            self.sensor_service.push_readings_to_db()
        except TimeoutError as e:
            self.log.error(f"SENSOR_CONTROLLER:: Timeout while pushing values to database {e}")
        except IOError as e:
            self.log.error(f"SENSOR_CONTROLLER:: I/O Err: {e}")
        except Exception as e:
            self.log.error(f"SENSOR_CONTROLLER:: Unhandled exception: {e}")