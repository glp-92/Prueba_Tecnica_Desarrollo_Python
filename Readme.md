# Prueba Tecnica desarrollo Software Python

## Enunciado de la tarea

**TAREA 1: Aplicación Python para lectura de datos de un sensor**

Se pretende evaluar la capacidad del candidato para desarrollar una aplicación escrita en Python que lea
los datos de un sensor infrarrojo, los publique cada “n” segundos, atienda peticiones para iniciar y parar
la captura de datos de dicho sensor y almacene la información en una base de datos de tipo SQL.

Notas: Para este ejercicio, el sensor de infrarrojo es ficticio, pero se prevé que en el futuro cercano se lean
datos reales de un sensor, el cual entrega una lista de 64 valores enteros sin signo de 16 bits de resolución.

### Descripción de la tarea

Se debe crear una aplicación escrita en Python que se conecte a un servidor de mensajería (local) y ofrezca
las capacidades descritas anteriormente:
- Lectura de datos del sensor cada “n” segundos
- Posibilidad de iniciar o parar la captura de datos del sensor (y la publicación de datos asociada)
- Almacenamiento de las capturas en una base de datos de tipo SQL

### Restricciones

- El protocolo de mensajería a emplear es [NATS](https://nats.io/) , de tal manera
que para desarrollar la aplicación se debe emplear la librería oficial [nats.py](https://github.com/nats-io/nats.py).
- La aplicación debe contener al menos los siguientes argumentos de manera que por línea de
comandos (a la hora de ejecutar la aplicación) se pueda controlar estos parámetros:
  - Tipo de sensor a emplear: mockup o real
  - Frecuencia de lectura del sensor (en segundos)
  - Rango de valores (mínimo y máximo) generados por el sensor infrarrojo cuando es de tipo
mockup
  - URI de conexión con la base de datos SQL

### Puntos a evaluar

- Legibilidad de código: uso de nombres descriptivos de variables y funciones
- Desarrollo de código limpio y conciso
- Modularidad y organización de código
- Documentación y comentarios asociados al código
- Calidad del “logging” de la aplicación
- Uso de convenciones de código y guías de estilo
- Cobertura de código con test
- Buen uso del control de versiones e historial de cambios

## Solucion propuesta

Se ha supuesto incierto el tiempo en que el sensor publica mensajes en el canal. El consumidor almacenará en una cola las lecturas que el sensor esté publicando y se volcarán en la base de datos cada X ms (tiempo definido en la entrada de argumentos)

Si el sensor es mockup, al iniciar el main se iniciara una instancia de un publisher que enviará mensajes al topic para ser leído por el cliente.

### Estructura del programa

- cfg => contiene ficheros de configuracion de ser necesarios
- log => directorio donde se almacenan los logs de programa
- src => modulos de la aplicacion principal
  - main => contiene los módulos del programa principal.
    - main.py => ejecución principal. Contempla y valida los argumentos de entrada. Importa las dependencias y las inyecta en módulos de lógica atendiendo al principio de inversión de dependencia (en lugar de importar los módulos en las clases que se necesiten, se pasan por parámetros en la inicialización, favorenciendo la trazabilidad del programa). Crea el log, la configuración y lanza los ciclos de programa.
    - util => directorio que contiene utilidades (modulo de lectura / escritura de ficheros)
    - log => directorio que contiene la declaración del logger
    - exceptions => para excepciones personalizadas de existir
    - db => contiene la declaración de la clase de conexión a base de datos
    - data => contiene los repositorios de datos, funciones que abstraen el acceso a los datos independientemente del cliente de BBDD (si se migra base de datos, se cambia el contenido de las funciones y el cliente, pero los nombres permaneceran intactos)
    - controller => en diseño web en arquitectura limpia contiene los endpoints y las llamadas a la logica del programa. En este caso contendrá la lógica de las ejecuciones que se desee realizar
  - test => contendrá pruebas de integración (el ciclo se cumple con las interacciones de forma esperada). Las pruebas unitarias, de haberlas se ejecutarán en cada módulo por separado.
- .env => en .gitignore para evitar leaks de informacion. Contiene variables de entorno que se estimen oportunas. Si el usuario del equipo se compromete, estas variables serán visibles a un posible atacante.

### Consideraciones

- Se debe validar el formato y longitud de la lectura de datos por parte del consumidor antes de añadir la información a la base de datos (código malicioso contenido en los mensajes, overflow)
- Otras validaciones de entrada se omitirán por limitaciones de tiempo (lectura de fichero de entorno, configuracion)
- La detención y ejecución del programa, al no ser indicado el método, se producirá con señales producidas a través de entrada de teclado.

## Setup

1. Se emplea `Anaconda` como gestor de librerias => `conda create -n natsclient python=3.10 anaconda`.
2. Activar entorno en bash dentro de la raiz del programa => `conda activate natsclient`
3. Instalar librerias que emplea la aplicacion `pip install -r requirements.txt`
