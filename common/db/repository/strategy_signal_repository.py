from common.db.models import StrategySignal
from common.db.repository.base_repository import BaseRepository

class StrategySignalRepository(BaseRepository[StrategySignal]):
    def __init__(self, db):
        super().__init__(db, StrategySignal)
