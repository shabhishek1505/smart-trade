from typing import Type, TypeVar, Generic, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound

T = TypeVar("T")

class BaseRepository(Generic[T]):
    def __init__(self, db: Session, model: Type[T]):
        self.db = db
        self.model = model

    def get(self, id: int) -> Optional[T]:
        return self.db.query(self.model).get(id)

    def get_all(self) -> List[T]:
        return self.db.query(self.model).all()

    def add(self, obj: T) -> T:
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, id: int) -> bool:
        obj = self.get(id)
        if obj:
            self.db.delete(obj)
            self.db.commit()
            return True
        return False

    def find_by(self, **kwargs) -> Optional[T]:
        return self.db.query(self.model).filter_by(**kwargs).first()

    def filter_by(self, **kwargs) -> List[T]:
        return self.db.query(self.model).filter_by(**kwargs).all()
