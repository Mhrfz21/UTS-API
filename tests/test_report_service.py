from unittest.mock import Mock
import pytest
from app.services.report_service import ReportService
from app.services.facility_service import NotFoundError

def test_service_does_not_create_report_when_facility_is_missing():
    reports = Mock()
    facilities = Mock()
    facilities.get.return_value = None
    service = ReportService(reports, facilities)
    with pytest.raises(NotFoundError, match="Fasilitas"):
        service.create({"facility_id": 404, "title": "Keyboard rusak"})
    reports.create.assert_not_called()
