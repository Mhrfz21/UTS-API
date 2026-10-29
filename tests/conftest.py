import os
import tempfile
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.database import Base, get_db
from app.main import app

@pytest.fixture()
def client():
    # In-memory SQLite is isolated for each test and avoids touching labcare.db.
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()

@pytest.fixture()
def facility_payload():
    return {"name": "Komputer Lab 1", "code": "KOM-01", "room": "Lab A", "condition": "good"}

@pytest.fixture()
def created_facility(client, facility_payload):
    response = client.post("/api/v1/facilities", json=facility_payload)
    assert response.status_code == 201
    return response.json()

@pytest.fixture()
def report_payload(created_facility):
    return {
        "facility_id": created_facility["id"],
        "title": "Keyboard tidak berfungsi",
        "description": "Beberapa tombol keyboard tidak merespons saat digunakan.",
        "category": "hardware",
        "priority": "medium",
    }

@pytest.fixture()
def created_report(client, report_payload):
    response = client.post("/api/v1/reports", json=report_payload)
    assert response.status_code == 201
    return response.json()
