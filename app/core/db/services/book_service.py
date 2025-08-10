from core.db.models.books import Books, Borrowing, Cards
from core.db.exception import ApiHTTPException
from datetime import datetime, timezone
from schemas.books import (
    BookItem, BookCreateResponse200, BookCreatePayload, BookDeleteResponse200, BookDetailResponse200, BookItem, 
    BooksListResponse200, BookUpdatePayload, BorrowCreateResponse200
)
from sqlalchemy import func, select, text, update
from sqlalchemy.orm import Session
from typing import List, Optional

MAX_PAGE_SIZE = 1000

def add_book(payload:BookCreatePayload, db: Session):
    with db.begin():
        row = db.execute(
            text("""
                INSERT INTO books (id, title, author)
                VALUES (:id, :title, :author)
                ON CONFLICT (id) DO NOTHING
                RETURNING id
            """),
            {"id": payload.id, "title": payload.title, "author": payload.author},
        ).mappings().one_or_none()
        if row is None:
            raise ApiHTTPException(409, "Book with given id already exists")

        book_id = row["id"]
        return BookCreateResponse200(code=200, bookId=book_id)

def borrow_book(book_id: str, card_id: str, db: Session) -> BorrowCreateResponse200:
    with db.begin():
        book = (
            db.query(Books)
              .filter(Books.id == book_id, Books.deleted_at.is_(None))
              .with_for_update()
              .one_or_none()
        )

        if book is None:
            raise ApiHTTPException(404, "Book not found")
        
        card_exists = db.query(Cards.id).filter(Cards.id == card_id).one_or_none()
        if card_exists is None:
            raise ApiHTTPException(404, "Library card not found")
        
        row = db.execute(
            text("""
                INSERT INTO borrowings (book_id, card_id, borrowed_at)
                SELECT :book_id, :card_id, NOW()
                WHERE NOT EXISTS (
                    SELECT 1 FROM borrowings
                    WHERE book_id = :book_id AND returned_at IS NULL
                )
                RETURNING id, borrowed_at
            """),
            {"book_id": book_id, "card_id": card_id},
        ).mappings().one_or_none()
        if row is None:
            raise ApiHTTPException(409, "Book is already borrowed")

    return BorrowCreateResponse200(
        bookId = book_id,
        borrowed_at = row["borrowed_at"].isoformat(),
        cardId = card_id,
        code = 200
    )

def delete_book(book_id: str, db:Session) -> BookDeleteResponse200:
    with db.begin():
        result = db.execute(
            update(Books)
            .where(Books.id == book_id, Books.deleted_at.is_(None))
            .values(deleted_at=datetime.utcnow())
            .returning(Books.id)
        ).scalar_one_or_none()

        if result is None:
            raise ApiHTTPException(404, "Book not found")

    return BookDeleteResponse200(
        code=200,
        status="Success"
    )

def get_book_by_id(book_id: str, db: Session) -> BookItem:
    query = (
        select(
            Books,
            Borrowing.id.label("borrow_id"),
            Borrowing.card_id.label("card_id"),
        )
        .outerjoin(
            Borrowing,
            (Borrowing.book_id == Books.id) & (Borrowing.returned_at.is_(None)),
        )
        .where((Books.id == book_id) & (Books.deleted_at is not None))
    )
    row = db.execute(query).one_or_none()
    if row is None:
        raise ApiHTTPException(404, "Book not found")

    book, borrow_id, card_id = row

    return BookDetailResponse200(
        author=book.author,
        borrowed=borrow_id is not None,
        borrowId=borrow_id,
        cardId=card_id,
        code = 200,
        created_at=book.created_at.isoformat(),
        id=book.id,
        title=book.title
    )

def list_books(db: Session, page: int = 1, size: int = 50) -> BooksListResponse200:
    page = max(1, page)
    size = max(1, min(size, MAX_PAGE_SIZE))
    offset = (page - 1) * size

    total = db.execute(
        select(func.count()).select_from(Books).where(Books.deleted_at.is_(None))
    ).scalar_one()

    stmt = (
        select(
            Books,
            Borrowing.card_id.label("card_id"),
        )
        .outerjoin(
            Borrowing,
            (Borrowing.book_id == Books.id) & (Borrowing.returned_at.is_(None)),
        )
        .where(Books.deleted_at.is_(None))
        .order_by(Books.id.asc())
        .limit(size)
        .offset(offset)
    )
    rows = db.execute(stmt).all()
    items: List[BookItem] = []
    for book, card_id in rows:
        items.append(
            BookItem(
                id=book.id,
                title=book.title,
                author=book.author,
                created_at=book.created_at.isoformat(),
                borrowed=card_id is not None,
                borrowCardId=card_id,
            )
        )

    total_pages = (total + size - 1) // size if size > 0 else 0

    return BooksListResponse200(
        code = 200,
        items=items,
        page=page,
        size=size,
        total=total,
        total_pages=total_pages        
    )

def return_book(book_id: str, card_id: str, db: Session):
    with db.begin():
        book = (
            db.query(Books)
            .filter(Books.id == book_id, Books.deleted_at.is_(None))
            .one_or_none()
        )
        if book is None:
            raise ApiHTTPException(404,"Book not found")

        card = db.query(Cards).filter(Cards.id == card_id).one_or_none()
        if card is None:
            raise ApiHTTPException(404, "Library card not found")
        
        borrowing = (
            db.query(Borrowing)
            .filter(Borrowing.book_id == book_id, Borrowing.returned_at.is_(None))
            .with_for_update()  # block active record for update
            .one_or_none()
        )
        if borrowing is None:
            raise ApiHTTPException(409, "Book is not borrowed")
        
        if borrowing.card_id != card_id:
            raise ApiHTTPException(409, "Book is borrowed by a different card")
        
        now = datetime.now(timezone.utc)
        borrowing.returned_at = now
        borrowing.returned_by = card_id

        return {
            "code": 200,
            "status": 'Success'
        }

def update_book(db: Session, book_id: int, payload: BookUpdatePayload) -> BookItem:
    with db.begin():
        row = (
            db.query(Books, Borrowing.card_id)
            .outerjoin(
                Borrowing,
                (Borrowing.book_id == Books.id) & (Borrowing.returned_at.is_(None))
            )
            .filter(Books.id == book_id, Books.deleted_at.is_(None))
            .one_or_none()
        )
        if row is None:
            raise ApiHTTPException(404, "Book not found")

        book: Books = row[0]
        card_id: Optional[str] = row[1]

        new_id = payload.id.strip() if getattr(payload, "id", None) else None
        if new_id and new_id != book_id:
            exists = (
                db.query(func.count())
                .select_from(Books)
                .filter(Books.id == new_id)  # use also deleted books (it must be unique)
                .scalar()
            )
            if exists:
                raise ApiHTTPException(409, "Book with given id already exists")
            book.id = new_id

        if getattr(payload, "author", None) is not None:
            book.author = payload.author

        if getattr(payload, "title", None) is not None:
            book.title = payload.title

        db.flush()

        return BookItem(
            author = book.author,
            borrowed = card_id is not None,
            borrowCardId = card_id,
            code=200,
            created_at=book.created_at.isoformat(),
            id=book.id,
            title=book.title
        )