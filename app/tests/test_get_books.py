from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_books_list():
    author = "List Author"
    book_id = "999999"
    title = "Book in list"
    payload = {
        "author": author,
        "id": book_id,
        "title": title
    }
    create_resp = client.post("/books?page=1&size=50", json=payload)
    assert create_resp.status_code == 200

    resp = client.get("/books/")
    assert resp.status_code == 200

    data = resp.json()
    assert data["page"] == 1
    assert data["size"] == 50

    items = data["items"]
    assert isinstance(items, list)
    assert len(items) > 0

    found = next((b for b in items if b["id"] == book_id), None)
    assert found is not None
    assert found["title"] == title
    assert found["author"] == author