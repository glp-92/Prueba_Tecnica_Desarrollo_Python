from typing import Dict
from datetime import datetime
from queue import Queue

class Sensor_Service:

    def __init__(self, log, sensor_repository):
        self.log = log 
        self.sensor_repository = sensor_repository
        self.sensor_read_queue = Queue()

    def add_reading_to_queue(self, reading_data):
        """
            Add a reading on dict format to a queue
        """
        self.sensor_read_queue.put(reading_data, timeout=0.1)
        return
    
    def push_readings_to_db(self):
        """
            Push all sensor values to database
        """
        queue_len, i = self.sensor_read_queue.qsize(), 1
        while not self.sensor_read_queue.empty():
            self.log.info(f"SENSOR_SERVICE:: Adding sensor readings to DB. {i} - {queue_len}")
            self.add_new_reading_to_db(self.sensor_read_queue.get(timeout=0.1))     
            i += 1   
        return

    def add_new_reading_to_db(self, new_msg_from_sensor: Dict):
        sensor_ref = new_msg_from_sensor.sensor_ref
        sensor_id = self.sensor_repository.get_sensor_id_by_ref(sensor_ref = sensor_ref)
        if sensor_id is None:
            raise ValueError("Ref doesn't exist on DB!")
        err = self.sensor_repository.insert_new_value(
            sensor_id=sensor_id, 
            timestamp=new_msg_from_sensor.timestamp, 
            values_to_insert=new_msg_from_sensor.values
        )
        if err: 
            raise IOError("Error adding new data from sensor on DB!")
        return