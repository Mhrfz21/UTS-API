from app.repositories.facility_repository import FacilityRepository
from app.repositories.report_repository import ReportRepository
from app.services.facility_service import NotFoundError, ConflictError

ALLOWED_TRANSITIONS = {
    "reported": {"in_progress"},
    "in_progress": {"completed"},
    "completed": set(),
}

class ReportService:
    def __init__(self, reports: ReportRepository, facilities: FacilityRepository):
        self.reports = reports
        self.facilities = facilities

    def create(self, data: dict):
        if self.facilities.get(data["facility_id"]) is None:
            raise NotFoundError("Fasilitas untuk laporan tidak ditemukan")
        try:
            item = self.reports.create({**data, "status": "reported"}, commit=False)
            self.reports.add_history(item.id, None, "reported", "Laporan dibuat", commit=False)
            self.reports.commit()
        except Exception:
            self.reports.rollback()
            raise
        return item

    def list(self, status: str | None = None, priority: str | None = None, facility_id: int | None = None):
        return self.reports.list(status=status, priority=priority, facility_id=facility_id)

    def get(self, report_id: int):
        item = self.reports.get(report_id)
        if item is None:
            raise NotFoundError("Laporan tidak ditemukan")
        return item

    def update(self, report_id: int, changes: dict):
        item = self.get(report_id)
        changes = dict(changes)  # do not mutate the caller's dict
        new_status = changes.pop("status", None)
        note = changes.pop("note", None)
        status_changed = bool(new_status) and new_status != item.status
        if note and not status_changed:
            raise ConflictError("Field note hanya dapat digunakan saat mengubah status")
        if status_changed and new_status not in ALLOWED_TRANSITIONS[item.status]:
            raise ConflictError(f"Perubahan status dari '{item.status}' ke '{new_status}' tidak diizinkan")
        # Field changes, new status and its history are saved in one transaction.
        try:
            old_status = item.status
            if status_changed:
                changes["status"] = new_status
            updated = self.reports.update(item, changes, commit=False) if changes else item
            if status_changed:
                self.reports.add_history(updated.id, old_status, new_status, note, commit=False)
            self.reports.commit()
        except Exception:
            self.reports.rollback()
            raise
        return updated

    def delete(self, report_id: int):
        item = self.get(report_id)
        self.reports.delete(item)

    def histories(self, report_id: int):
        self.get(report_id)
        return self.reports.histories(report_id)
