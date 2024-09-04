import aio_pika
import os
import json
import asyncio
from controllers.user_controller import authenticate_user

RABBITMQ_QUEUE = "user_auth_service"

class RPCServer:
    def __init__(self):
        self.rabbitmq_url = os.getenv("RABBITMQ_URL")
        self.connection = None
        self.channel = None
        self.queue = None

    async def setup(self):
        self.connection = await aio_pika.connect_robust(self.rabbitmq_url)
        self.channel = await self.connection.channel()
        self.queue = await self.channel.declare_queue(RABBITMQ_QUEUE)
        await self.queue.consume(self.on_request)

    async def on_request(self, message: aio_pika.IncomingMessage):
        data = json.loads(message.body)
        response = await authenticate_user(data["username"], data["password"])
        if response is False:
            response = {"error": "Invalid username or password"}
        else:
            response = {
                "username": response.username,
                "user_id": response.id,
                "role": response.role
            }
        await self.channel.default_exchange.publish(
            aio_pika.Message(
                body=json.dumps(response).encode(),
                correlation_id=message.correlation_id,
            ),
            routing_key=message.reply_to
        )
        await message.ack()

    async def start(self):
        await self.setup()
        print("RPC Server started.")
        await asyncio.Event().wait()  # Keeps the server running

    async def stop(self):
        await self.connection.close()