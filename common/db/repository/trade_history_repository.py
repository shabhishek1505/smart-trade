from common.db.models import TradeHistory
from common.db.repository.base_repository import BaseRepository

class TradeHistoryRepository(BaseRepository[TradeHistory]):
    def __init__(self, db):
        super().__init__(db, TradeHistory)