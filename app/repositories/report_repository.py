from __future__ import annotations
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.report import Report
from app.models.report_history import ReportHistory

class ReportRepository:
    """All database operations related to reports and their histories."""
    def __init__(self, db: Session):
        self.db = db

    def _save(self, item, commit: bool) -> None:
        """Commit immediately, or only flush so the caller can commit a whole unit of work."""
        if commit:
            self.db.commit()
        else:
            self.db.flush()
        self.db.refresh(item)

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()

    def create(self, data: dict, commit: bool = True) -> Report:
        item = Report(**data)
        self.db.add(item)
        self._save(item, commit)
        return item

    def list(self, status: str | None = None, priority: str | None = None, facility_id: int | None = None) -> list[Report]:
        query = select(Report).order_by(Report.id)
        if status:
            query = query.where(Report.status == status)
        if priority:
            query = query.where(Report.priority == priority)
        if facility_id:
            query = query.where(Report.facility_id == facility_id)
        return list(self.db.scalars(query).all())

    def get(self, report_id: int) -> Report | None:
        return self.db.get(Report, report_id)

    def update(self, item: Report, changes: dict, commit: bool = True) -> Report:
        for key, value in changes.items():
            setattr(item, key, value)
        self._save(item, commit)
        return item

    def delete(self, item: Report) -> None:
        self.db.delete(item)
        self.db.commit()

    def add_history(self, report_id: int, old_status: str | None, new_status: str, note: str | None, commit: bool = True) -> ReportHistory:
        history = ReportHistory(report_id=report_id, old_status=old_status, new_status=new_status, note=note)
        self.db.add(history)
        self._save(history, commit)
        return history

    def histories(self, report_id: int) -> list[ReportHistory]:
        return list(self.db.scalars(select(ReportHistory).where(ReportHistory.report_id == report_id).order_by(ReportHistory.id)).all())
