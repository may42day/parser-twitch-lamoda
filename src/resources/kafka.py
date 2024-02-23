import asyncio
import aiokafka
import pickle

from src.config import settings


async def run_kafka():
    """
    Kafka consumer handler.

    Parses function with its args from message and execute it.
    """

    consumer = aiokafka.AIOKafkaConsumer(
        "parsing-topic", bootstrap_servers=settings.kafka_bootstrap_servers
    )
    await consumer.start()
    try:
        async for msg in consumer:
            message_data = pickle.loads(msg.value)

            function = message_data["function"]
            args = message_data["args"]
            kwargs = message_data["kwargs"]

            if asyncio.iscoroutinefunction(function):
                try:
                    await function(*args, **kwargs)
                except Exception as e:
                    print(
                        f"function: {function}, args: {args}, kwargs: {kwargs}, error: {e}"
                    )

            else:
                function(*args, **kwargs)

    finally:
        await consumer.stop()


async def producer_send_one(function, *args, **kwargs):
    """
    Function to send message by Kafka producer.

    Send function with args as message to kafka broker.
    """

    producer = aiokafka.AIOKafkaProducer(
        bootstrap_servers=settings.kafka_bootstrap_servers
    )

    message_data = {
        "function": function,
        "args": args,
        "kwargs": kwargs,
    }
    message = pickle.dumps(message_data)

    await producer.start()
    try:
        await producer.send_and_wait("parsing-topic", message)
    finally:
        await producer.stop()
