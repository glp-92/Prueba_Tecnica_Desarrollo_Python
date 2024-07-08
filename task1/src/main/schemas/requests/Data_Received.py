from typing import List
import json 
from datetime import datetime


class Data_Received:

    def __init__(self, **kwargs):
        self.sensor_ref = kwargs.get('ref')
        self.values = kwargs.get('values')
        self.timestamp = datetime.now().isoformat()
        self.validate_fields()

    def validate_fields(self):

        def validate_id():
            if not self.sensor_ref or not isinstance(self.sensor_ref, str):
                raise ValueError("bad id received")

        def validate_values():
            if not self.values or not isinstance(self.values, List) or len(self.values) > 65:
                raise ValueError("bad data format for values")
            if False in [isinstance(value, int) for value in self.values]:
                raise ValueError("data format invalid")
            if list(filter(lambda value: value >= 65535, self.values)) != []: # Algun valor por encima del desborde
                raise ValueError("bad value range")
            
        validate_id()
        validate_values()

    def to_string(self):
        return json.dumps({'id': self.sensor_ref, 'values': self.values, 'timestamp': self.timestamp})
    
    def model_dump(self):
        return {'id': self.sensor_ref, 'values': self.values, 'timestamp': self.timestamp}





if __name__ == '__main__':
    data = {
        "values": [2,1,3],
        "ref": 1
    }
    new_data = Data_Received(**data).model_dump()
    print(new_data)