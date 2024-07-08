import asyncio


class Push_To_DB_Records:

    def __init__(self, log, sensor_service, push_frequency):
        self.log = log
        self.sensor_service = sensor_service
        self.push_frequency = push_frequency

    def setup_signal_handlers(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def start(self):
        async def push_to_db_cycle():
            self.log.info("PUSH_TO_DB_RECORDS:: Begining loop...")
            while not self.stop_event.is_set():
                self.push_readings_to_db()
                await asyncio.sleep(self.push_frequency)
            self.log.info("PUSH_TO_DB_RECORDS:: Exiting loop...")
        self.stop_event = asyncio.Event()
        self.loop.run_until_complete(push_to_db_cycle())

    def stop(self):
        self.stop_event.set()

    def push_readings_to_db(self):
        try:
            self.sensor_service.push_readings_to_db()
        except TimeoutError as e:
            self.log.error(f"PUSH_TO_DB_RECORDS:: Timeout while pushing values to database {e}")
        except IOError as e:
            self.log.error(f"PUSH_TO_DB_RECORDS:: I/O Err: {e}")
        except Exception as e:
            self.log.error(f"PUSH_TO_DB_RECORDS:: Unhandled exception: {e}")