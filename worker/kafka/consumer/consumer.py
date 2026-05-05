from confluent_kafka import Consumer
from threading import Thread
import logging

from common.utils.config import KAFKA_BOOTSTRAP_SERVERS

logger = logging.get_logger("kafka-consumer")

def consume_kafka(topic: str, handler_fn, group_id: str = "strategy-worker"):
    kafka_conf = {
        'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
        'group.id': group_id,
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': True,
    }

    consumer = Consumer(kafka_conf)
    consumer.subscribe([topic])

    def listen():
        logger.info(f"[Kafka] Listening on topic: {topic}")
        while True:
            try:
                msg = consumer.poll(1.0)
                if msg is None:
                    continue
                if msg.error():
                    logger.error(f"[Kafka] Error: {msg.error()}")
                    continue

                message_value = msg.value().decode("utf-8")
                logger.info(f"[Kafka] Received: {message_value}")
                handler_fn(eval(message_value))  # ⚠️ Use `json.loads()` if sending JSON
            except Exception as e:
                logger.exception(f"[Kafka] Failed to process message: {e}")

    # Run in background thread
    Thread(target=listen, daemon=True).start()
