import asyncio, random, json, sys, argparse

from com.Nats import Nats_Client

"""
    python mock_publisher.py --sendtime 1 --valrange 0-1000
"""

parser = argparse.ArgumentParser(description='Programa mockup de sensor')
parser.add_argument('--sendtime', type=int, required=True, help='Frecuencia de envio (en s) de los datos del sensor')
parser.add_argument('--valrange', type=str, required=True, default="0-3000", help='Rango de valores si el sensor esta simulado')
args = parser.parse_args()

send_time = args.sendtime
valrange = args.valrange
if valrange:
    try:
        range_values = list(map(lambda v: int(v), valrange.split("-")))
        range_values = (min(range_values), max(range_values))
        if range_values[0] < 0 or range_values[1] > 65535: raise argparse.ArgumentTypeError("Out of range int16")
    except Exception as e:
        raise argparse.ArgumentTypeError('Expected range expressed by "minval-maxval"')

class Log:
    def info(self, msg):
        print(f"INFO: {msg}")

    def warning(self, msg):
        print(f"WARNING: {msg}")

    def error(self, msg):
        print(f"ERROR: {msg}")


async def send_message_loop(nats_client, delay):
    while True:
        print("Enviando mensaje al canal...")
        data = {"ref": "5286x", "values": [random.randint(range_values[0], range_values[1]) for _ in range(65)]}
        await nats_client.publish_message_to_channel("test_channel", json.dumps(data))
        await asyncio.sleep(delay)

try:
    delay_time = int(sys.argv[1])
    if delay_time > 20: raise Exception("Valor de delay demasiado alto")
except Exception as e:
    print(e)
    delay_time = 1

log = Log()
nats_publisher = Nats_Client(log, "publisher")
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.run_until_complete(nats_publisher.connect("nats://demo.nats.io:4222"))
loop.run_until_complete(nats_publisher.subscribe_to_channel("test_channel", None))
loop.run_until_complete(send_message_loop(nats_publisher, delay=delay_time))
