from mysql import connector
from mysql.connector import Error
import os

class MySQL:
    """
    Se crea un usuario diferente a root con permisos exclusivos a la base de datos que se va a utilizar
        mysql -u admin -p (enter admin pwd)
        CREATE DATABASE pruebatecnicauvigo;
        CREATE USER 'uvigo'@'localhost' IDENFITIED BY 'test@password';
        GRANT ALL PRIVILEGES ON pruebatecnicauvigo.* to 'uvigo'@'localhost';

    Se crea un identificador para el sensor de esta aplicacion
        INSERT INTO `sensors` (`ref`) VALUES ('5286x');
    """

    def __init__(self, log, db_url):
        self.log = log
        self.db_url = db_url
        self.get_cfg_data()
        self.connect()
        # err = self.setup() # llamada desde el main para controlar el error y cerrar el programa

    def get_cfg_data(self):
        self.db_name = os.environ.get('DB_NAME')

    def connect(self):
        try:
            self.connection = connector.connect(
                host=self.db_url, 
                user=os.environ.get('DB_USR'),
                password=os.environ.get('DB_PWD')
            )
            if self.connection.is_connected():
                self.log.info(f"DB:: connection to MySQL database successful!")
            else: 
                self.connection = None
        except Error as e:
            self.log.error(f"DB:: Error connecting to MySQL: {e}")
        return

    def setup(self):

        def create_database_if_not_exists(cursor):
            err = 0
            try:
                cursor.execute(f'CREATE DATABASE IF NOT EXISTS {self.db_name}')
                self.log.info(f"DB:: database access correct")
            except Error as e:
                err = 1
                self.log.error(f"DB:: Error creating database: {e}")
            return err

        def create_tables_if_not_exists(cursor):
            """
            No necesitan commit transaccional al ser operaciones sobre los esquemas
            """
            err = 0
            try:
                cursor.execute(f'USE {self.db_name}')
                cursor.execute(f'CREATE TABLE IF NOT EXISTS sensors ( \
                    id INT AUTO_INCREMENT PRIMARY KEY, \
                    ref VARCHAR(255) NOT NULL \
                )')
                self.log.info(f"DB:: table sensors access correct")
                cursor.execute(f'CREATE TABLE IF NOT EXISTS data ( \
                    id INT AUTO_INCREMENT PRIMARY KEY, \
                    read_values VARCHAR(512) NOT NULL, \
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP, \
                    sensor_id INT NOT NULL, \
                    FOREIGN KEY (sensor_id) REFERENCES sensors(id) \
                )')
                self.log.info(f"DB:: table data access correct")
            except Error as e:
                err = 1
                self.log.error(f'DB:: Error creating tables: {e}')
            return err 
        
        cursor = self.connection.cursor()
        err = create_database_if_not_exists(cursor)
        if not err: err = create_tables_if_not_exists(cursor)
        cursor.close()
        return err


if __name__ == '__main__':
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