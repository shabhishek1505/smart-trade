import uuid
from datetime import datetime, timezone
from common.dto.kafka import KafkaEnvelopeDto

def wrap_kafka_message(event_type: str, source: str, data: dict) -> dict:
    payload = KafkaEnvelopeDto(
        event_id=uuid.uuid4(),
        timestamp=datetime.now(timezone.utc),
        event_type=event_type,
        source=source,
        data=data,
    )
    return payload.dict()
