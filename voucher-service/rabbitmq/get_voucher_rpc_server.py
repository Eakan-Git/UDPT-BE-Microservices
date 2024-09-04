import aio_pika
import os
import json
import asyncio
from controllers.voucher_controller import get_voucher

RABBITMQ_QUEUE = "get_voucher_service"

class GetVoucherRPCServer:
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
        print("Received a request to get voucher")
        data = json.loads(message.body)
        voucher_id = data.get("voucher_id")
        if not isinstance(voucher_id, int) or voucher_id < 1:
            response = {
                "error": "Invalid voucher_id"
            }
        else:
            response = await get_voucher(voucher_id)
            if response is None:
                response = {
                    "error": "Voucher not found"
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
        print("Get voucher RPC Server started.")
        await asyncio.Event().wait()  # Keeps the server running

    async def stop(self):
        await self.connection.close()