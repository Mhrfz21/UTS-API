from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

FacilityCondition = Literal["good", "damaged", "maintenance"]

class FacilityCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    name: str = Field(min_length=2, max_length=100)
    code: str = Field(min_length=2, max_length=30, pattern=r"^[A-Za-z0-9_-]+$")
    room: str = Field(min_length=1, max_length=100)
    condition: FacilityCondition = "good"

    @field_validator("code")
    @classmethod
    def normalize_code(cls, value: str) -> str:
        return value.upper()

class FacilityUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    name: str | None = Field(default=None, min_length=2, max_length=100)
    code: str | None = Field(default=None, min_length=2, max_length=30, pattern=r"^[A-Za-z0-9_-]+$")
    room: str | None = Field(default=None, min_length=1, max_length=100)
    condition: FacilityCondition | None = None

    @field_validator("code")
    @classmethod
    def normalize_code(cls, value: str | None) -> str | None:
        return value.upper() if value else value

    @model_validator(mode="after")
    def validate_changes(self):
        if not self.model_fields_set:
            raise ValueError("Minimal satu field harus dikirim")
        for key in self.model_fields_set:
            if getattr(self, key) is None:
                raise ValueError(f"Field '{key}' tidak boleh null")
        return self

class FacilityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    code: str
    room: str
    condition: FacilityCondition
