import asyncio 
import nats
from nats.errors import NoServersError#, ConnectionClosedError, TimeoutError


class Nats_Client:
    """
        Can produce and consume messages from a topic
    """


    class Connection_Status:
        """
            Retrieve and update connection status
            args:
                connected_to_server: True if connected, False if not connected
                listening_channels: dictionary specifying topics that are currently listening the client
                    {
                        subscription: suscription state
                    }
        """

        def __init__(self, connected_to_server: bool = False, listening_channels: dict = {}):
            self.connected_to_server = connected_to_server 
            self.listening_channels = listening_channels
            return
        

    def __init__(self, log, client_id: str):
        self.log = log
        self.client_id = client_id
        self.setup()
        return 


    def setup(self): 
        """
            channel_subscriptions: dict that contains channel subscriptions, key => channel name / value => suscription entity
        """
        self.nc = None
        self.connection_status = self.Connection_Status()
        return 


    async def connect(self, server_url: str):
        """
            await for server connection, multiple functions for logging
        """

        async def on_disconnected():
            self.log.warning(f'NATS_CLIENT_{self.client_id}:: Disconnected!')
        
        async def on_reconnected():
            self.log.info(f'NATS_CLIENT_{self.client_id}:: Reconnection successful!')

        async def on_close_conn():
            self.log.warning(f'NATS_CLIENT_{self.client_id}:: Connection closed!')

        async def on_error(e):
            self.log.error(f'NATS_CLIENT_{self.client_id}:: Error on server: {e}')

        try:
            self.nc = await nats.connect(
                server_url,
                error_cb = on_error,
                reconnected_cb = on_reconnected,
                disconnected_cb = on_disconnected,
                closed_cb = on_close_conn,
                name = self.client_id
            )
            self.connection_status.connected_to_server = True
            self.log.info(f'NATS_CLIENT_{self.client_id}:: Client successfully connected!')
        except NoServersError as e:
            self.connection_status.connected_to_server = False
            self.nc = None
            self.log.error(f'NATS_CLIENT_{self.client_id}:: Error on connecting server: {e}')
        return
    

    async def disconnect(self):
        """
            gracefully disconnects from server waiting for message completion
        """
        if self.nc.is_closed: return
        await self.nc.drain()
        self.connection_status.connected_to_server = False
        return


    async def subscribe_to_channel(self, channel_name: str, on_msg_recv_callback: callable):
        """
            Subscribe to a channel if client is connected to server and is not already subbed to the same channel, registered by connection_status
            args:
                channel_name: str of the name of the subbed channel
                on_msg_recv_callback: function called when a msg is received on the channel
        """
        if not self.connection_status.connected_to_server:
            self.log.error(f'NATS_CLIENT_{self.client_id}:: Client is not connected, cannot subscribe to channels')
            return
        if channel_name in self.connection_status.listening_channels:
            self.log.warning(f'NATS_CLIENT_{self.client_id}:: Already subscribed to channel {channel_name}')
            return
        subscription = await self.nc.subscribe(channel_name, cb=on_msg_recv_callback)
        await self.nc.flush()
        self.connection_status.listening_channels[channel_name] = {'subscription': subscription}
        self.log.info(f'NATS_CLIENT_{self.client_id}:: Successfully connected to channel {channel_name}')


    async def unsubscribe_to_channel(self, channel_name: str):
        await self.connection_status.listening_channels[channel_name]['subscription'].unsubscribe()
        del self.connection_status.listening_channels[channel_name]
        return
    
    
    async def publish_message_to_channel(self, channel_name: str, message: str):
        """
            Send a message to a channel
        """
        if not self.connection_status.connected_to_server:
            self.log.error(f'NATS_CLIENT_{self.client_id}:: Client is not connected, cannot send messages')
            return
        if not self.connection_status.listening_channels[channel_name]:
            self.log.error(f'NATS_CLIENT_{self.client_id}:: Trying to send a message to a not subbed channel!')
            return
        self.log.info(f'NATS_CLIENT_{self.client_id}:: Publishing message "{message}" to channel {channel_name}')
        await self.nc.publish(channel_name, message.encode())
        self.log.info(f'NATS_CLIENT_{self.client_id}:: Message "{message}" published to channel {channel_name} successfully!')





if __name__ == '__main__':
    from concurrent.futures import ProcessPoolExecutor

    class Log:
        def info(self, msg): print(f"INFO: {msg}")
        def warning(self, msg): print(f"WARNING: {msg}")
        def error(self, msg): print(f"ERROR: {msg}")

    async def on_message_received(msg):
        print(f"Mensaje recibido: {msg.data.decode()}")

    def run_publisher():
        async def send_message_loop(nats_client):
            while True:
                print("Enviando mensaje al canal...")
                await nats_client.publish_message_to_channel('test_channel', 'hi')
                await asyncio.sleep(2)
        log = Log()
        nats_publisher = Nats_Client({}, log, "publisher")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(nats_publisher.connect("nats://demo.nats.io:4222"))
        loop.run_until_complete(nats_publisher.subscribe_to_channel('test_channel', None))
        loop.run_until_complete(send_message_loop(nats_publisher))

    def run_listener():
        log = Log()
        nats_listener = Nats_Client({}, log, "consumer")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(nats_listener.connect("nats://demo.nats.io:4222"))
        loop.run_until_complete(nats_listener.subscribe_to_channel('test_channel', on_message_received))
        loop.run_forever()

    with ProcessPoolExecutor(2) as executor:
        executor.submit(run_listener)
        executor.submit(run_publisher)