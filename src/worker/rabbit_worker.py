import asyncio
import json
import uuid

from aio_pika.abc import AbstractIncomingMessage

from broker import LIKES_QUEUE, connect_rabbit
from database import async_local_session
from database.database_classes import DataBaseCRUD


async def handle_like(message: AbstractIncomingMessage) -> None:
    async with message.process(requeue=False):
        payload = json.loads(message.body)
        post_id = uuid.UUID(payload["post_id"])
        user_id = int(payload["user_id"])

        async with async_local_session() as session:
            if not await DataBaseCRUD.can_like(session, post_id, user_id):
                return

            await DataBaseCRUD.add_like(session, post_id, user_id)


async def main() -> None:
    rabbit_connection = await connect_rabbit()
    rabbit_channel = await rabbit_connection.channel()
    await rabbit_channel.set_qos(prefetch_count=10)
    queue = await rabbit_channel.declare_queue(LIKES_QUEUE, durable=True)
    await queue.consume(lambda msg: handle_like(msg))

    try:
        await asyncio.Event().wait()
    finally:
        await rabbit_connection.close()


if __name__ == "__main__":
    asyncio.run(main())
