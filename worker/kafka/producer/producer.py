from confluent_kafka import Producer
import json
from datetime import datetime
from common.utils.kafka import wrap_kafka_message
import logging
from common.utils.config import KAFKA_BOOTSTRAP_SERVERS,SIGNAL_PROCESSING_KAFKA_TOPIC

logger = logging.getLogger("strategy-worker.kafka")

producer_conf = {
    "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
}
producer = Producer(producer_conf)


def produce_signal(plan_id, trace_id, signal_data):
    message = wrap_kafka_message({
        "plan_id": plan_id,
        "trace_id": trace_id,
        "signal": signal_data,
        "timestamp": datetime.utcnow().isoformat()
    })
    try:
        producer.produce(
            topic=SIGNAL_PROCESSING_KAFKA_TOPIC,
            value=json.dumps(message),
            callback=kafka_delivery_report
        )
        producer.flush()
        logger.info(f"[Kafka] Message sent for PlanID={plan_id}, Stock={stock_symbol}")
    except Exception as e:
        logger.error(f"[Kafka] Failed to send message: {e}")

def kafka_delivery_report(err, msg):
    if err:
        print(f"[Kafka] Delivery failed: {err}")
    else:
        print(f"[Kafka] Delivered to {msg.topic()} [{msg.partition()}] @ offset {msg.offset()}")