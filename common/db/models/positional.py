from sqlalchemy import Column, String, Float, Integer, Boolean
from common.db.session import Base

class PositionConfig(Base):
    __tablename__ = "position_config"

    stock_symbol = Column(String(20), primary_key=True)
    max_investment = Column(Float, nullable=True)
    fixed_quantity = Column(Integer, nullable=True)
    use_percentage = Column(Boolean, default=False)
    percentage_of_capital = Column(Float, nullable=True)
    