from typing import Annotated, Literal
from fastapi import APIRouter, Depends, Query, Response, status
from app.dependencies import get_report_service
from app.schemas.report import ReportCreate, ReportUpdate, ReportResponse, ReportHistoryResponse
from app.services.report_service import ReportService

router = APIRouter(prefix="/api/v1/reports", tags=["Reports"])

@router.post("", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
def create_report(payload: ReportCreate, service: ReportService = Depends(get_report_service)):
    return service.create(payload.model_dump())

@router.get("", response_model=list[ReportResponse])
def list_reports(
    status_filter: Annotated[Literal["reported", "in_progress", "completed"] | None, Query(alias="status")] = None,
    priority: Literal["low", "medium", "high"] | None = None,
    facility_id: int | None = Query(default=None, gt=0),
    service: ReportService = Depends(get_report_service),
):
    return service.list(status=status_filter, priority=priority, facility_id=facility_id)

@router.get("/{report_id}", response_model=ReportResponse)
def get_report(report_id: int, service: ReportService = Depends(get_report_service)):
    return service.get(report_id)

@router.patch("/{report_id}", response_model=ReportResponse)
def update_report(report_id: int, payload: ReportUpdate, service: ReportService = Depends(get_report_service)):
    return service.update(report_id, payload.model_dump(exclude_unset=True))

@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_report(report_id: int, service: ReportService = Depends(get_report_service)):
    service.delete(report_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.get("/{report_id}/histories", response_model=list[ReportHistoryResponse])
def report_histories(report_id: int, service: ReportService = Depends(get_report_service)):
    return service.histories(report_id)
