from core.db.models.books import Books
from core.db.session import SessionLocal
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_add_book():
    payload = {
        "author": "Henryk Sienkiewicz",
        "id": "000002",
        "title": "Quo Vadis"
    }
    response = client.post("/books", json=payload)

    assert response.status_code == 200
    assert response.json()["bookId"] == "000002"

    db = SessionLocal()
    book = db.query(Books).filter_by(id="000002").first()
    assert book is not None
    assert book.title == "Quo Vadis"
    assert book.author == "Henryk Sienkiewicz"

def test_add_book_existing_number():
    payload = {
        "author": "Henryk Sienkiewicz",
        "id": "000002",
        "title": "Quo Vadis"
    }
    response = client.post("/books", json=payload)

    assert response.status_code == 409
    assert response.json()["error"] == "Book with given id already exists"
