# worker/consumer/signal_consumer.py

from common.db.session import SessionLocal
from common.dto.kafka import KafkaEnvelopeDto
from common.dto.signal import StrategySignalData
from common.utils.config import SIGNAL_PROCESSING_KAFKA_TOPIC
from worker.kafka.consumer.consumer import consume_kafka
from worker.services.signal_service import SignalService
import logging

logger = logging.getLogger("signal-consumer")

def start_signal_consumer():
    def handler(msg: dict):
        try:
            payload = KafkaEnvelopeDto(**msg)
            data = StrategySignalData(**payload.data)

            with SessionLocal() as db:
                service = SignalService(db)
                service.execute_signal(data)

        except Exception as e:
            logger.error(f"[ERROR] Failed to process message: {e}", exc_info=True)

    consume_kafka(SIGNAL_PROCESSING_KAFKA_TOPIC, handler)
