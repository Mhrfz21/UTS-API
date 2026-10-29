from fastapi import Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.repositories.facility_repository import FacilityRepository
from app.repositories.report_repository import ReportRepository
from app.services.facility_service import FacilityService
from app.services.report_service import ReportService

def get_facility_service(db: Session = Depends(get_db)) -> FacilityService:
    return FacilityService(FacilityRepository(db), ReportRepository(db))

def get_report_service(db: Session = Depends(get_db)) -> ReportService:
    return ReportService(ReportRepository(db), FacilityRepository(db))
