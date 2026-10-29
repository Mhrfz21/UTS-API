def test_create_facility(client, facility_payload):
    response = client.post("/api/v1/facilities", json=facility_payload)
    assert response.status_code == 201
    assert response.json()["code"] == "KOM-01"

def test_duplicate_facility_code_returns_409(client, created_facility, facility_payload):
    response = client.post("/api/v1/facilities", json=facility_payload)
    assert response.status_code == 409

def test_list_facilities(client, created_facility):
    response = client.get("/api/v1/facilities")
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_get_missing_facility_returns_404(client):
    assert client.get("/api/v1/facilities/999").status_code == 404

def test_update_facility(client, created_facility):
    response = client.patch(f"/api/v1/facilities/{created_facility['id']}", json={"condition": "damaged"})
    assert response.status_code == 200
    assert response.json()["condition"] == "damaged"

def test_delete_unused_facility(client, created_facility):
    response = client.delete(f"/api/v1/facilities/{created_facility['id']}")
    assert response.status_code == 204

def test_invalid_facility_condition(client, facility_payload):
    facility_payload["condition"] = "broken-ish"
    assert client.post("/api/v1/facilities", json=facility_payload).status_code == 422

def test_cannot_delete_facility_with_report(client, created_facility, created_report):
    response = client.delete(f"/api/v1/facilities/{created_facility['id']}")
    assert response.status_code == 409

def test_patch_null_field_returns_422_not_409(client, created_facility):
    for field in ("name", "code", "room", "condition"):
        response = client.patch(f"/api/v1/facilities/{created_facility['id']}", json={field: None})
        assert response.status_code == 422

def test_empty_facility_update_returns_422(client, created_facility):
    assert client.patch(f"/api/v1/facilities/{created_facility['id']}", json={}).status_code == 422

def test_whitespace_only_facility_fields_rejected(client, facility_payload):
    facility_payload["name"] = "   "
    assert client.post("/api/v1/facilities", json=facility_payload).status_code == 422

def test_facility_code_is_case_insensitive_unique(client, created_facility, facility_payload):
    facility_payload["code"] = "kom-01"
    assert client.post("/api/v1/facilities", json=facility_payload).status_code == 409

def test_update_facility_code_conflict_with_other(client, created_facility, facility_payload):
    other = client.post("/api/v1/facilities", json={**facility_payload, "code": "KOM-02"}).json()
    response = client.patch(f"/api/v1/facilities/{other['id']}", json={"code": "kom-01"})
    assert response.status_code == 409
