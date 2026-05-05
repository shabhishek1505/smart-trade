from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from datetime import datetime
from common.db.base import Base


class UserSettings(Base):
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)

    # UI Preferences
    theme = Column(String(20), default="light")  # light, dark
    language = Column(String(10), default="en")

    # Notification Preferences
    notifications_enabled = Column(Boolean, default=True)
    signal_notifications = Column(Boolean, default=True)
    trade_notifications = Column(Boolean, default=True)
    price_alerts = Column(Boolean, default=False)

    # Trading Preferences
    default_broker = Column(String(50), default="angel_one")
    auto_execute = Column(Boolean, default=False)  # Auto-execute signals

    # Timezone
    timezone = Column(String(50), default="UTC")

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "theme": self.theme,
            "language": self.language,
            "notifications_enabled": self.notifications_enabled,
            "signal_notifications": self.signal_notifications,
            "trade_notifications": self.trade_notifications,
            "price_alerts": self.price_alerts,
            "default_broker": self.default_broker,
            "auto_execute": self.auto_execute,
            "timezone": self.timezone,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
