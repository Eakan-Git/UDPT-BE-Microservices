import aio_pika
import os
import json
import asyncio
from controllers.activity_controller import get_activity_by_id

RABBITMQ_QUEUE = "get_activity_service"

class GetActivityRPCServer:
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
        print("Received a request to get activity by id")
        data = json.loads(message.body)
        activity_id = data.get("activity_id")
        if not isinstance(activity_id, int) or activity_id < 1:
            response = {
                "error": "Invalid activity id"
            }
        else:
            response = await get_activity_by_id(activity_id)
            if response is None:
                response = {
                    "error": "Activity not found"
                }
            else:
                response = json.loads(response.json())
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
        print("Get activity RPC Server started.")
        await asyncio.Event().wait()  # Keeps the server running

    async def stop(self):
        await self.connection.close()