from common.dto.kafka import KafkaEnvelopeDto
from common.dto.strategy import StrategyTriggerData
from common.utils.logger import init_logger
from common.utils.config import KAFKA_BOOTSTRAP_SERVERS, PLAN_PROCESSING_KAFKA_TOPIC, WORKER_GROUP

from strategy.factory import get_strategy
from kafka.producer import produce_signal
import json

from worker.kafka.consumer.consumer import consume_kafka

logger = init_logger("strategy-worker")

def start_strategy_plan_consumer():
    def handler(msg: dict):
        try:
            payload = KafkaEnvelopeDto(**msg)
            data = StrategyTriggerData(**payload.data)
            execute_strategy(payload.event_id, data)
        except Exception as e:
            logger.error(f"Failed to process message: {e}")

    consume_kafka(PLAN_PROCESSING_KAFKA_TOPIC, handler)

def execute_strategy(event_id:str, data: StrategyTriggerData):
    try:
        strategy_class = get_strategy(data.strategy_name)

        if not strategy_class:
            logger.error(f"Unknown strategy: {data.strategy_name}")

        strategy_instance = strategy_class(data.stock_symbol, data.params)
        signal = strategy_instance.evaluate()

        produce_signal(signal, event_id)

    except Exception as e:
        print(f"Error processing message: {e}")
