import asyncio, random, json, sys

from com.Nats import Nats_Client


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
        data = {"ref": "5286x", "values": [random.randint(0, 100) for _ in range(65)]}
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
