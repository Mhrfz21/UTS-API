from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator

ReportCategory = Literal["hardware", "software", "network", "other"]
ReportPriority = Literal["low", "medium", "high"]
ReportStatus = Literal["reported", "in_progress", "completed"]

class ReportCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    facility_id: int = Field(gt=0)
    title: str = Field(min_length=5, max_length=100)
    description: str = Field(min_length=10, max_length=2000)
    category: ReportCategory
    priority: ReportPriority = "medium"

class ReportUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    title: str | None = Field(default=None, min_length=5, max_length=100)
    description: str | None = Field(default=None, min_length=10, max_length=2000)
    category: ReportCategory | None = None
    priority: ReportPriority | None = None
    status: ReportStatus | None = None
    assigned_to: str | None = Field(default=None, max_length=100)  # null = batalkan penugasan
    note: str | None = Field(default=None, max_length=1000)

    @model_validator(mode="after")
    def at_least_one_change(self):
        if not self.model_fields_set:
            raise ValueError("Minimal satu field harus dikirim")
        for key in self.model_fields_set:
            if key not in {"note", "assigned_to"} and getattr(self, key) is None:
                raise ValueError(f"Field '{key}' tidak boleh null")
        if self.model_fields_set == {"note"}:
            raise ValueError("Minimal satu field selain note harus dikirim")
        return self

class ReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    facility_id: int
    title: str
    description: str
    category: ReportCategory
    priority: ReportPriority
    status: ReportStatus
    assigned_to: str | None
    created_at: datetime

class ReportHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    report_id: int
    old_status: str | None
    new_status: ReportStatus
    note: str | None
    changed_at: datetime
