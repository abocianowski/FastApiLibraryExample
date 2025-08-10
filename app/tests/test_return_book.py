from core.db.models.books import Books
from core.db.session import SessionLocal
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_return_book():
    # add book
    payload = {
        "author": "Henryk Sienkiewicz",
        "id": "000007",
        "title": "Quo Vadis"
    }
    response = client.post("/books", json=payload)

    assert response.status_code == 200
    assert response.json()["bookId"] == "000007"

    # test return not borrowed book
    return_book = client.post(f"/books/000007/return/712538", json=payload)
    assert return_book.status_code == 409
    data = return_book.json()
    assert data["error"] == "Book is not borrowed"


    # borrow book
    response = client.post(f"/books/000007/borrow/712538")
    assert response.status_code == 200

    # return book
    return_book2 = client.post(f"/books/000007/return/712538", json=payload)
    assert return_book2.status_code == 200
    data = return_book2.json()
    assert data["status"] == "Success"