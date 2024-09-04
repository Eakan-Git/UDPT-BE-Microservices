import aio_pika
import os
import json
import asyncio
from controllers.user_controller import update_user

RABBITMQ_QUEUE = "patching_user_service"

class PatchUserRPCServer:
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
        print("Received a request to patch user")
        msg = json.loads(message.body)
        user_id = msg.get("user_id")
        patch_data = msg.get("patch_data")
        if not isinstance(user_id, int) or user_id < 1:
            response = {
                "error": "Invalid user id"
            }
        else:
            response = await update_user(user_id, patch_data)
            if response is None:
                response = {
                    "error": "User not found"
                }
            else:
                response = {
                    "message": "User updated successfully"
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
        print("Patching user RPC Server started.")
        await asyncio.Event().wait()  # Keeps the server running

    async def stop(self):
        await self.connection.close()