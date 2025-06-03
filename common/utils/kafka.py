import uuid
from datetime import datetime, timezone

def wrap_kafka_message(event_type: str, source: str, data: dict) -> dict:
    return {
        "event_id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type,
        "source": source,
        "data": data,
    }
