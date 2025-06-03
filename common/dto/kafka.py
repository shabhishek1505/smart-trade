from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from datetime import datetime
from typing import Literal, Dict, Any

class KafkaEnvelopeDto(BaseModel):
    event_id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    event_type: Literal["STRATEGY_TRIGGERED", "ORDER_EXECUTED"]
    source: str
    data: Dict[str, Any]
