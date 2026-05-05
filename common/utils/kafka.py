from typing import Optional
import uuid
from datetime import datetime, timezone

from sqlalchemy import UUID
from common.dto.kafka import KafkaEnvelopeDto

def wrap_kafka_message(event_type: str, source: str, data: dict, event_id: Optional[UUID] = None) -> dict:
    payload = KafkaEnvelopeDto(
        event_id=event_id or uuid.uuid4(),
        timestamp=datetime.now(timezone.utc),
        event_type=event_type,
        source=source,
        data=data,
    )
    return payload.dict()
