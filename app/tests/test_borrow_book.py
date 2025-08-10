from core.db.models.books import Books
from core.db.session import SessionLocal
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_borrow_book():
    book_id = "005001"
    payload = {
        "author": "Henryk Sienkiewicz",
        "id": book_id,
        "title": "Quo Vadis"
    }
    response = client.post("/books", json=payload)
    assert response.status_code == 200
    assert response.json()["bookId"] == book_id

    card_id = "357192"
    response = client.post(f"/books/{book_id}/borrow/{card_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["code"] == 200
    assert data["bookId"] == book_id
    assert data["cardId"] == card_id
    assert data["borrowed_at"] is not None

    # borrow borrowed book
    r2 = client.post(f"/books/{book_id}/borrow/{card_id}")
    assert r2.status_code == 409
    err = r2.json()
    assert err["error"] == 'Book is already borrowed'

    # check 404 - book not found
    r2 = client.post(f"/books/000123/borrow/{card_id}")
    assert r2.status_code == 404
    err = r2.json()
    assert err["error"] == 'Book not found'

    # check 404 - card not found
    r3 = client.post(f"/books/{book_id}/borrow/000789")
    assert r3.status_code == 404
    err = r3.json()
    assert err["error"] == 'Library card not found'