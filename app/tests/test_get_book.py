from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_book():
    # add book
    author = "Test Author"
    book_id = "009901"
    title = "Test GET Book"
    payload = {
        "id": book_id,
        "title": title,
        "author": author
    }

    create_resp = client.post("/books", json=payload)
    assert create_resp.status_code == 200

    # get book
    resp = client.get(f"/books/{book_id}")
    assert resp.status_code == 200

    data = resp.json()

    assert data["code"] == 200
    assert data["author"] == author
    assert data["borrowed"] in (False, 0)
    assert data["borrowCardId"] is None
    assert "created_at" in data
    assert data["id"] == book_id
    assert data["title"] == title

def test_get_book_not_found():
    resp = client.get(f"/books/555555")
    assert resp.status_code == 404
    data = resp.json()
    assert data["code"] == 404
    assert data["error"] == "Book not found"