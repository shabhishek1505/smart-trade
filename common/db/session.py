from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from common.utils.config import DB_URL

# Engine creation - single source of truth
engine = create_engine(DB_URL, echo=False, future=True)

# Session factory to create sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
