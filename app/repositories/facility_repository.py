from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.facility import Facility

class FacilityRepository:
    """All database operations related to facilities."""
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: dict) -> Facility:
        item = Facility(**data)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def list(self) -> list[Facility]:
        return list(self.db.scalars(select(Facility).order_by(Facility.id)).all())

    def get(self, facility_id: int) -> Facility | None:
        return self.db.get(Facility, facility_id)

    def get_by_code(self, code: str) -> Facility | None:
        return self.db.scalar(select(Facility).where(Facility.code == code))

    def update(self, item: Facility, changes: dict) -> Facility:
        for key, value in changes.items():
            setattr(item, key, value)
        self.db.commit()
        self.db.refresh(item)
        return item

    def delete(self, item: Facility) -> None:
        self.db.delete(item)
        self.db.commit()
