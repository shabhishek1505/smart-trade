from common.db.models import Position
from common.db.repository.base_repository import BaseRepository

class PositionRepository(BaseRepository[Position]):
    def __init__(self, db):
        super().__init__(db, Position)