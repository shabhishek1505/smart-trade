from kafka import KafkaConsumer
from common.dto.kafka import KafkaEnvelopeDto
from common.utils.logger import get_logger
from common.utils.config import KAFKA_BOOTSTRAP_SERVERS, PLAN_PROCESSING_KAFKA_TOPIC, WORKER_GROUP

from strategy.factory import get_strategy
from kafka.producer import produce_signal
import json

logger = get_logger("strategy-worker")

def listen_to_strategy_queue():
    consumer = KafkaConsumer(
        PLAN_PROCESSING_KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        group_id=WORKER_GROUP
    )

    logger.info("Listening to 'strategy.plan.execute' queue...")

    for message in consumer:
        try:
            raw_event = message.value

            # Parse into Pydantic model for validation
            event = KafkaEnvelopeDto(**raw_event)

            # Extract metadata
            event_id = event.event_id
            data = event.data

            strategy_class = get_strategy(data.strategy_name)

            if not strategy_class:
                logger.error(f"Unknown strategy: {data.strategy_name}")
                continue

            strategy_instance = strategy_class(data.stock_symbol, data.params)
            signal = strategy_instance.evaluate()

            produce_signal(event.plan_id, event.trace_id, signal)

        except Exception as e:
            print(f"Error processing message: {e}")
