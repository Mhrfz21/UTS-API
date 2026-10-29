from fastapi import APIRouter, Depends, Response, status
from app.dependencies import get_facility_service
from app.schemas.facility import FacilityCreate, FacilityUpdate, FacilityResponse
from app.services.facility_service import FacilityService

router = APIRouter(prefix="/api/v1/facilities", tags=["Facilities"])

@router.post("", response_model=FacilityResponse, status_code=status.HTTP_201_CREATED)
def create_facility(payload: FacilityCreate, service: FacilityService = Depends(get_facility_service)):
    return service.create(payload.model_dump())

@router.get("", response_model=list[FacilityResponse])
def list_facilities(service: FacilityService = Depends(get_facility_service)):
    return service.list()

@router.get("/{facility_id}", response_model=FacilityResponse)
def get_facility(facility_id: int, service: FacilityService = Depends(get_facility_service)):
    return service.get(facility_id)

@router.patch("/{facility_id}", response_model=FacilityResponse)
def update_facility(facility_id: int, payload: FacilityUpdate, service: FacilityService = Depends(get_facility_service)):
    return service.update(facility_id, payload.model_dump(exclude_unset=True))

@router.delete("/{facility_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_facility(facility_id: int, service: FacilityService = Depends(get_facility_service)):
    service.delete(facility_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
