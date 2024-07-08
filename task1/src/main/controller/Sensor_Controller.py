import os, asyncio, json

from schemas.requests.Data_Received import Data_Received


class Sensor_Controller:

    def __init__(self, log, nats_client, sensor_service):
        self.log = log 
        self.nats_client = nats_client
        self.sensor_service = sensor_service
        self.get_importers()

    def get_importers(self):
        return 
    
    def setup_topic_handlers(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.nats_client.connect(os.environ.get('NATS_SERVER_URL')))
        self.loop.run_until_complete(self.nats_client.subscribe_to_channel(os.environ.get('NATS_SENSOR_CHANNEL'), self.on_sensor_data_received))
    
    def start(self):
        async def listen():
            self.log.info("SENSOR_CONTROLLER:: Begining loop...")
            while not self.stop_event.is_set():
                await asyncio.sleep(0.1) # Avoid cpu overload
            self.log.info("SENSOR_CONTROLLER:: Exiting loop...")
            await self.nats_client.unsubscribe_to_channel(os.environ.get('NATS_SENSOR_CHANNEL'))
            await self.nats_client.disconnect()
        self.stop_event = asyncio.Event()
        self.loop.run_until_complete(listen())

    def stop(self):
        self.stop_event.set()
        return

    async def on_sensor_data_received(self, new_msg_from_sensor):
        try:
            self.log.info(f"SENSOR_CONTROLLER:: Received new sensor read")
            new_msg_from_sensor = Data_Received(**json.loads(new_msg_from_sensor.data.decode()))
            self.sensor_service.add_reading_to_queue(new_msg_from_sensor)
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