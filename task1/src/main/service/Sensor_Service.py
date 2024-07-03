from typing import Dict
from datetime import datetime

class Sensor_Service:

    def __init__(self, log, sensor_repository):
        self.log = log 
        self.sensor_repository = sensor_repository

    def add_new_reading_to_db(self, new_msg_from_sensor: Dict):
        sensor_ref = new_msg_from_sensor.sensor_ref
        sensor_id = self.sensor_repository.get_sensor_id_by_ref(sensor_ref = sensor_ref)
        if sensor_id is None:
            raise ValueError("Ref doesn't exist on DB!")
        err = self.sensor_repository.insert_new_value(
            sensor_id=sensor_id, 
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 
            values_to_insert=new_msg_from_sensor.values
        )
        if err: 
            raise IOError("Error adding new data from sensor on DB!")
        return