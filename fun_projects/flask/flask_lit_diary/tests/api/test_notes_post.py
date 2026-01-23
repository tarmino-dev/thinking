# Successful Creation (201)
def test_create_note_authenticated(logged_client):
    payload = {
        "title": "New note",
        "subtitle": "Sub",
        "body": "Text"
    }

    response = logged_client.post(
        "/api/v1/notes",
        json=payload
    )

    assert response.status_code == 201

    data = response.get_json()
    assert data["title"] == "New note"


# Unauthorized (401)
def test_create_note_unauthorized(client):
    response = client.post(
        "/api/v1/notes",
        json={
            "title": "Fail",
            "subtitle": "Fail",
            "body": "Fail"
        }
    )

    assert response.status_code == 401


# Invalid JSON (400)
def test_create_note_invalid_json(logged_client):
    response = logged_client.post(
        "/api/v1/notes",
        data="not-json",
        content_type="application/json"
    )

    assert response.status_code == 400


# Missing fields (400)
def test_create_note_missing_fields(logged_client):
    response = logged_client.post(
        "/api/v1/notes",
        json={"title": "Only title"}
    )

    assert response.status_code == 400

    data = response.get_json()
    assert "missing_fields" in data
