from core.db.models.books import Books
from core.db.session import SessionLocal
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_update_book():
    payload = {
        "author": "Henryk Sienkiewicz",
        "id": "123456",
        "title": "Quo Vadis"
    }
    response = client.post("/books", json=payload)

    assert response.status_code == 200
    assert response.json()["bookId"] == "123456"

    # update
    payload = {
        "author": "Henryk Sienkiewicz2",
        "id": "023456",
        "title": "Quo Vadis2"
    }
    update = client.put("/books/123456", json=payload)
    assert update.status_code == 200

    data = update.json()
    assert data["author"] == "Henryk Sienkiewicz2"
    assert data["borrowed"] == False
    assert data["borrowCardId"] == None
    assert data["created_at"] is not None
    assert data["id"] == "023456"
    assert data["title"] == "Quo Vadis2"


