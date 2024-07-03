import os, asyncio

from schemas.requests.Data_Received import Data_Received
from service.Sensor_Service import Sensor_Service

class Sensor_Controller:

    def __init__(self, log, nats_client, sensor_repository):
        self.log = log 
        self.nats_client = nats_client
        self.sensor_repository = sensor_repository
        self.get_importers()

    def get_importers(self): 
        self.sensor_service = Sensor_Service(self.log, self.sensor_repository)
        return 
    
    def setup_topic_handlers(self): # Call from main (start-stop)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.nats_client.connect(os.environ.get("NATS_SERVER_URL")))
        asyncio.run(self.nats_client.subscribe_to_channel(os.environ.get('NATS_SENSOR_CHANNEL'), self.on_sensor_data_received))
        return loop
    
    def listen(self, loop):
        self.log.info("SENSOR_CONTROLLER:: Listening...")
        loop.run_forever()

    async def on_sensor_data_received(self, new_msg_from_sensor):
        try:
            new_msg_from_sensor = Data_Received(**new_msg_from_sensor)
            self.sensor_service.add_new_reading_to_db(new_msg_from_sensor)
        except ValueError as e:
            self.log.error(f"SENSOR_CONTROLLER:: ValueError: {e}")
            return
        except IOError as e:
            self.log.error(f"SENSOR_CONTROLLER:: I/O Err: {e}")
        except Exception as e:
            self.log.error(f"SENSOR_CONTROLLER:: Unhandled exception: {e}")
        return