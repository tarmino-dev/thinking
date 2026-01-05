def test_get_notes_returns_list(client, note):
    response = client.get("/api/v1/notes")

    assert response.status_code == 200

    data = response.get_json()
    assert "items" in data
    assert data["total"] == 1

    item = data["items"][0]
    assert item["title"] == "Test note"
    assert item["author"]["name"] == "Test User"
