import json
import uuid

import aio_pika
from aio_pika import DeliveryMode, Message
from aio_pika.abc import AbstractChannel, AbstractQueue, AbstractRobustConnection
from loguru import logger

from database import RABBITMQ_URL

LIKES_QUEUE = "likes"


async def connect_rabbit() -> AbstractRobustConnection:
    rabbit_connection = await aio_pika.connect_robust(RABBITMQ_URL)
    logger.info("connected to RabbitMQ")
    return rabbit_connection


async def declare_likes_queue(channel: AbstractChannel) -> AbstractQueue:
    # durable=True: очередь переживёт рестарт брокера.
    # RabbitMQ 4.1 запрещает transient non-exclusive очереди по умолчанию.
    return await channel.declare_queue(LIKES_QUEUE, durable=True)


async def publish_like(
    channel: AbstractChannel, post_id: uuid.UUID, user_id: int
) -> None:
    message = Message(
        body=json.dumps({"post_id": str(post_id), "user_id": user_id}).encode(),
        content_type="application/json",
        delivery_mode=DeliveryMode.PERSISTENT,
        message_id=str(uuid.uuid4()),
    )

    exchange_data = channel.default_exchange
    await exchange_data.publish(message, routing_key=LIKES_QUEUE)
