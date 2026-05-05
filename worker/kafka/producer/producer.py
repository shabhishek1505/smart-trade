from confluent_kafka import Producer
import json
from datetime import datetime
from common.dto.signal import StrategySignalData
from common.utils.kafka import wrap_kafka_message
import logging
from common.utils.config import KAFKA_BOOTSTRAP_SERVERS,SIGNAL_PROCESSING_KAFKA_TOPIC

logger = logging.getLogger("strategy-worker.kafka")

producer_conf = {
    "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
}
producer = Producer(producer_conf)


def produce_signal(signal_data: StrategySignalData, event_id: str):

    message = wrap_kafka_message(
        event_type="STRATEGY_SIGNAL_TRIGGERED",
        source="strategy-worker",
        data=signal_data.dict(),
        event_id=event_id)

    try:
        producer.produce(
            topic=SIGNAL_PROCESSING_KAFKA_TOPIC,
            value=json.dumps(message),
            callback=kafka_delivery_report
        )
        producer.flush()
        logger.info(f"[Kafka] Message sent for PlanID={signal_data.plan_id}, Stock={signal_data.stock_symbol}")
    except Exception as e:
        logger.error(f"[Kafka] Failed to send message: {e}")

def kafka_delivery_report(err, msg):
    if err:
        print(f"[Kafka] Delivery failed: {err}")
    else:
        print(f"[Kafka] Delivered to {msg.topic()} [{msg.partition()}] @ offset {msg.offset()}")