from sqlalchemy.exc import IntegrityError
from app.repositories.facility_repository import FacilityRepository
from app.repositories.report_repository import ReportRepository

class NotFoundError(Exception):
    pass

class ConflictError(Exception):
    pass

class FacilityService:
    def __init__(self, facilities: FacilityRepository, reports: ReportRepository):
        self.facilities = facilities
        self.reports = reports

    def create(self, data: dict):
        if self.facilities.get_by_code(data["code"]):
            raise ConflictError("Kode fasilitas sudah digunakan")
        try:
            return self.facilities.create(data)
        except IntegrityError as exc:
            raise ConflictError("Kode fasilitas sudah digunakan") from exc

    def list(self):
        return self.facilities.list()

    def get(self, facility_id: int):
        item = self.facilities.get(facility_id)
        if item is None:
            raise NotFoundError("Fasilitas tidak ditemukan")
        return item

    def update(self, facility_id: int, changes: dict):
        item = self.get(facility_id)
        if "code" in changes:
            existing = self.facilities.get_by_code(changes["code"])
            if existing and existing.id != facility_id:
                raise ConflictError("Kode fasilitas sudah digunakan")
        try:
            return self.facilities.update(item, changes)
        except IntegrityError as exc:
            raise ConflictError("Kode fasilitas sudah digunakan") from exc

    def delete(self, facility_id: int):
        item = self.get(facility_id)
        if self.reports.list(facility_id=facility_id):
            raise ConflictError("Fasilitas yang sudah memiliki laporan tidak dapat dihapus")
        self.facilities.delete(item)
