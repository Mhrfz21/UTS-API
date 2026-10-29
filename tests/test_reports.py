def test_create_report(client, report_payload):
    response = client.post("/api/v1/reports", json=report_payload)
    assert response.status_code == 201
    assert response.json()["status"] == "reported"

def test_report_title_too_short_returns_422(client, report_payload):
    report_payload["title"] = "PC"
    assert client.post("/api/v1/reports", json=report_payload).status_code == 422

def test_report_unknown_facility_returns_404(client, report_payload):
    report_payload["facility_id"] = 999
    assert client.post("/api/v1/reports", json=report_payload).status_code == 404

def test_list_reports(client, created_report):
    response = client.get("/api/v1/reports")
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_filter_reports_by_status(client, created_report):
    response = client.get("/api/v1/reports?status=reported")
    assert response.status_code == 200
    assert all(item["status"] == "reported" for item in response.json())

def test_update_report_priority(client, created_report):
    response = client.patch(f"/api/v1/reports/{created_report['id']}", json={"priority": "high"})
    assert response.status_code == 200
    assert response.json()["priority"] == "high"

def test_status_can_move_to_in_progress_and_history_is_recorded(client, created_report):
    response = client.patch(
        f"/api/v1/reports/{created_report['id']}",
        json={"status": "in_progress", "note": "Sedang diperiksa teknisi"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "in_progress"
    histories = client.get(f"/api/v1/reports/{created_report['id']}/histories")
    assert histories.status_code == 200
    assert len(histories.json()) == 2
    assert histories.json()[1]["new_status"] == "in_progress"

def test_cannot_move_completed_report_back_to_reported(client, created_report):
    report_id = created_report["id"]
    assert client.patch(f"/api/v1/reports/{report_id}", json={"status": "in_progress"}).status_code == 200
    assert client.patch(f"/api/v1/reports/{report_id}", json={"status": "completed"}).status_code == 200
    response = client.patch(f"/api/v1/reports/{report_id}", json={"status": "reported"})
    assert response.status_code == 409

def test_get_missing_report_returns_404(client):
    assert client.get("/api/v1/reports/999").status_code == 404

def test_delete_report(client, created_report):
    response = client.delete(f"/api/v1/reports/{created_report['id']}")
    assert response.status_code == 204

def test_empty_update_returns_422(client, created_report):
    response = client.patch(f"/api/v1/reports/{created_report['id']}", json={})
    assert response.status_code == 422

def test_invalid_priority_returns_422(client, report_payload):
    report_payload["priority"] = "urgent-ish"
    assert client.post("/api/v1/reports", json=report_payload).status_code == 422

def test_whitespace_only_title_rejected(client, report_payload):
    report_payload["title"] = "        "
    assert client.post("/api/v1/reports", json=report_payload).status_code == 422

def test_assignment_can_be_set_and_cleared(client, created_report):
    url = f"/api/v1/reports/{created_report['id']}"
    assert client.patch(url, json={"assigned_to": "Budi"}).json()["assigned_to"] == "Budi"
    response = client.patch(url, json={"assigned_to": None})
    assert response.status_code == 200
    assert response.json()["assigned_to"] is None

def test_cannot_skip_status_and_nothing_changes(client, created_report):
    url = f"/api/v1/reports/{created_report['id']}"
    response = client.patch(url, json={"status": "completed", "priority": "high"})
    assert response.status_code == 409
    current = client.get(url).json()
    assert current["status"] == "reported" and current["priority"] == "medium"

def test_note_without_status_change_returns_409(client, created_report):
    response = client.patch(f"/api/v1/reports/{created_report['id']}", json={"priority": "low", "note": "x"})
    assert response.status_code == 409

def test_update_fields_and_status_together_records_one_history(client, created_report):
    url = f"/api/v1/reports/{created_report['id']}"
    response = client.patch(url, json={"assigned_to": "Budi", "status": "in_progress", "note": "Mulai"})
    assert response.status_code == 200
    body = response.json()
    assert body["assigned_to"] == "Budi" and body["status"] == "in_progress"
    histories = client.get(f"{url}/histories").json()
    assert [(h["old_status"], h["new_status"]) for h in histories] == [(None, "reported"), ("reported", "in_progress")]
    assert histories[1]["note"] == "Mulai"

def test_filter_reports_by_priority_and_facility(client, created_report):
    assert len(client.get("/api/v1/reports?priority=medium").json()) == 1
    assert client.get("/api/v1/reports?priority=high").json() == []
    assert len(client.get(f"/api/v1/reports?facility_id={created_report['facility_id']}").json()) == 1
