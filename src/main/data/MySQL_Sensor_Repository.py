from typing import List
import json, math
from mysql.connector import Error

from Sensor_Repository import Sensor_Repository

class MySQL_Sensor_Repository(Sensor_Repository):
    """
    Class that inherits repository interface, must specify abstract methods
    """

    def __init__(self, cfg, log, mysql_connection):
        self.cfg = cfg 
        self.log = log
        self.mysql_connection = mysql_connection

    def get_cfg_data(self): return 

    def get_importers(self): return

    def insert_new_value(self, sensor_id: int, timestamp, values_to_insert: List):
        cursor = self.mysql_connection.cursor()
        query = 'INSERT INTO data (sensor_id, timestamp, read_values) VALUES (%s, %s, %s)'
        try:
            values_json = json.dumps(values_to_insert, separators=(',', ':'))
            cursor.execute(query, (sensor_id, timestamp, values_json))
            self.mysql_connection.commit()
            self.log.info(f"SENSOR_REPO:: Values inserted on DB")
        except Error as e:
            self.mysql_connection.rollback()
            self.log.error(f"SENSOR_REPO:: Error while inserting values on DB: {e}")
        finally:
            cursor.close()

    def get_values_by_sensor_id_pageable(self, sensor_id, page, values_per_page):

        def get_total_values_account(cursor):
            try:
                query = "SELECT COUNT(*) AS values_count FROM data d JOIN sensors s ON d.sensor_id = s.id WHERE s.id = %s"
                cursor.execute(query, (sensor_id,))
                result = cursor.fetchone()
                if result:
                    return result['values_count']
            except Error as e:
                self.log.error(f"SENSOR_REPO:: Error while retrieving total values account: {e}")
            return 0
        
        cursor = self.mysql_connection.cursor(dictionary=True)
        total_values_account = get_total_values_account(cursor)
        total_pages = math.ceil(total_values_account / float(values_per_page)) # Si hay 2.1 paginas, debe marcar 3
        offset = (page - 1) * values_per_page
        # query = "SELECT * FROM data ORDER BY timestamp DESC LIMIT %s OFFSET %s"
        query = "SELECT d.id, d.timestamp, d.read_values FROM data d JOIN sensors s ON d.sensor_id = s.id WHERE s.id = %s ORDER BY d.timestamp DESC LIMIT %s OFFSET %s"
        try:
            cursor.execute(query, (sensor_id, values_per_page, offset))
            results = cursor.fetchall()
            return results, total_pages
        except Error as e:
            self.log.error(f"SENSOR_REPO:: Error retrieving values: {e}")
            return [], total_pages
        finally:
            cursor.close()

    
    def get_all_values_pageable(self, page, values_per_page):

        def get_total_values_account(cursor):
            try:
                cursor.execute("SELECT COUNT(*) AS values_count FROM data")
                result = cursor.fetchone()
                if result:
                    return result['values_count']
            except Error as e:
                self.log.error(f"SENSOR_REPO:: Error while retrieving total values account: {e}")
            return 0
        
        cursor = self.mysql_connection.cursor(dictionary=True)
        total_values_account = get_total_values_account(cursor)
        total_pages = math.ceil(total_values_account / float(values_per_page)) # Si hay 2.1 paginas, debe marcar 3
        offset = (page - 1) * values_per_page
        query = "SELECT * FROM data ORDER BY timestamp DESC LIMIT %s OFFSET %s"
        try:
            cursor.execute(query, (values_per_page, offset))
            results = cursor.fetchall()
            return results, total_pages
        except Error as e:
            self.log.error(f"SENSOR_REPO:: Error retrieving values: {e}")
            return [], total_pages
        finally:
            cursor.close()





if __name__ == '__main__':
    import sys, os, datetime, random
    path = os.path.abspath('./src/main')
    sys.path.append(path)
    from db.MySQL import MySQL

    class Log:
        def __init__(self): return 
        def info(self, msg): print(msg)
        def error(self, msg): print(msg)
    cfg = {
        'db': {
            'url': 'localhost',
            'user': 'uvigo',
            'password': 'test@password',
            'db_name': 'pruebatecnicauvigo'
        }
    }
    db = MySQL(cfg, Log())
    db.connect()
    err = db.setup()
    if err: sys.exit()

    try:
        mysql_repository = MySQL_Sensor_Repository(cfg, Log(), db.connection)
    except TypeError as e:
        print(f"No se han definido los metodos abstractos de la interfaz: {e}")
        sys.exit()

    
    values = [random.randint(0, 65535) for _ in range(2)] # 16 bit
    sensor_id = 1
    timestamp = datetime.datetime.now()
    timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')

    mysql_repository.insert_new_value(sensor_id=sensor_id, timestamp=timestamp, values_to_insert=values)
    values, total_pages = mysql_repository.get_values_by_sensor_id_pageable(sensor_id=1, page=1, values_per_page=5)
    print(values, total_pages, "size", len(values))