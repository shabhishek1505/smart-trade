from confluent_kafka import Producer
import json
from common.dto.strategy import StrategyTriggerData
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

def send_strategy_eval_message(job_data: StrategyTriggerData):
    message = wrap_kafka_message(
        event_type="STRATEGY_TRIGGERED",
        source="strategy-scheduler",
        data=job_data.dict())

    try:
        producer.produce(
            topic=PLAN_PROCESSING_KAFKA_TOPIC,
            value=json.dumps(message,default=str),
            callback=kafka_delivery_report
        )
        producer.flush()
        logger.info(f"[Kafka] Message sent for PlanID={job_data.plan_id}, Stock={job_data.stock_symbol}")
    except Exception as e:
        logger.error(f"[Kafka] Failed to send message: {e}")
