import aio_pika
import asyncio
import uuid
import os

class PatchUserRpcClient:
    def __init__(self):
        self.rabbitmq_url = os.getenv("RABBITMQ_URL")
        self.exchange_name = os.getenv("RABBITMQ_EXCHANGE")
        self.connection = None
        self.channel = None
        self.callback_queue = None
        self.response = None
        self.corr_id = None

    async def setup(self):
        self.connection = await aio_pika.connect_robust(self.rabbitmq_url)
        self.channel = await self.connection.channel()
        self.callback_queue = await self.channel.declare_queue('', exclusive=True)
        await self.callback_queue.consume(self.on_response)

    async def call(self, data):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        await self.channel.default_exchange.publish(
            aio_pika.Message(
                body=data.encode(),
                correlation_id=self.corr_id,
                reply_to=self.callback_queue.name,
            ),
            routing_key='patching_user_service'
        )
        while self.response is None:
            await asyncio.sleep(0.1)
        return self.response

    async def on_response(self, message: aio_pika.IncomingMessage):
        if self.corr_id == message.correlation_id:
            self.response = message.body.decode()
            await message.ack()

    async def close(self):
        await self.connection.close()