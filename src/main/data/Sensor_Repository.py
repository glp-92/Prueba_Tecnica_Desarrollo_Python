from abc import ABC, abstractmethod

class Sensor_Repository(ABC):
    """
    Interfaz repository para el tratamiento de datos del sensor. Fuerza a implementar los metodos definidos como abstractos
    """

    @abstractmethod
    def insert_new_value(self): return 

    @abstractmethod
    def get_values_by_sensor_id_pageable(self): return
    
    @abstractmethod
    def get_all_values_pageable(self): return

    @abstractmethod
    def get_sensor_id_by_ref(self): return