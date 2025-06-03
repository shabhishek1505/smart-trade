from confluent_kafka import Producer
import json
from common.utils.config import KAFKA_BOOTSTRAP_SERVERS, PLAN_PROCESSING_KAFKA_TOPIC
import logging
from common.utils.kafka import wrap_kafka_message

logger = logging.getLogger("strategy-scheduler.producer")

producer_conf = {
    "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
}
producer = Producer(producer_conf)

def kafka_delivery_report(err, msg):
    if err:
        print(f"[Kafka] Delivery failed: {err}")
    else:
        print(f"[Kafka] Delivered to {msg.topic()} [{msg.partition()}] @ offset {msg.offset()}")

def send_strategy_eval_message(plan_id, strategy_id, stock_symbol):
    message = wrap_kafka_message(
        event_type="STRATEGY_TRIGGERED",
        source="strategy-scheduler",
        data={
            "plan_id": plan_id,
            "strategy_id": strategy_id,
            "stock_symbol": stock_symbol
        })

    try:
        producer.produce(
            topic=PLAN_PROCESSING_KAFKA_TOPIC,
            value=json.dumps(message),
            callback=kafka_delivery_report
        )
        producer.flush()
        logger.info(f"[Kafka] Message sent for PlanID={plan_id}, Stock={stock_symbol}")
    except Exception as e:
        logger.error(f"[Kafka] Failed to send message: {e}")
