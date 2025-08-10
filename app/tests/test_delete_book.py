from core.db.models.books import Books
from core.db.session import SessionLocal
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_delete_book_marks_deleted_and_handles_errors():
    book_id = "777001"
    payload = {"id": book_id, "title": "To be deleted", "author": "Someone"}
    create_resp = client.post("/books", json=payload)
    assert create_resp.status_code == 200

    delete_resp = client.delete(f"/books/{book_id}")
    assert delete_resp.status_code == 200
    body = delete_resp.json()
    assert body == {"code": 200, "status": "Success"}

    db = SessionLocal()
    try:
        book = db.query(Books).filter(Books.id == book_id).one()
        assert book.deleted_at is not None
    finally:
        db.close()

    delete_again = client.delete(f"/books/{book_id}")
    assert delete_again.status_code == 404

    error = delete_again.json()
    assert error["error"] == 'Book not found'
    assert error["code"] == 404

    bad = client.delete("/books/ABC123")
    assert bad.status_code == 422