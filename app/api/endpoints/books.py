from core.db.services import book_service
from api.deps import get_db
from schemas.books import (
    BookCreateResponse200, BookCreateResponse409, BookCreatePayload, BookDetailResponse200,
    BookItem, BookDeleteResponse200, BooksListResponse200, BookNotFound404, BookUpdatePayload,
    BookReturnResponse, BookReturnResponse409, BorrowCreateResponse200, BorrowCreateResponse409)
from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session

router = APIRouter(prefix="/books", tags=["Books"])

@router.post(
        '/',
        description="Create a new book (6-digit string ID allowed, including leading zeros).",
        response_description="Book has been added",
        response_model=BookCreateResponse200,
        responses={
            409: {
                "description": "Book with given id already exists",
                "model": BookCreateResponse409
            }
    }
)
async def add_book(
    payload: BookCreatePayload,
    db: Session = Depends(get_db)
):
    return book_service.add_book(payload, db)

@router.post(
    '/{book_id}/borrow/{card_id}',
    description="Borrow a book for a given library card (6-digit ids)",
    response_description="Borrowing created",
    response_model=BorrowCreateResponse200,
    responses={
        404: {"description": "Book or card not found", "model": BookNotFound404},
        409: {"description": "Book is deleted or already borrowed", "model": BorrowCreateResponse409},
    }
)
async def borrow_book(
    book_id: str = Path(..., pattern=r"^\d{6}$", description="6-digit book id", example="000001"),
    card_id: str = Path(..., pattern=r"^\d{6}$", description="6-digit card id", example="245781"),
    db: Session = Depends(get_db)
):
    return book_service.borrow_book(book_id=book_id, card_id=card_id, db=db)

@router.delete(
    '/{book_id}',
    description="Delete book by book id",
    response_description="Information about successful operation",
    response_model=BookDeleteResponse200,
    responses = {
        404: {"description": "Book not found", "model": BookNotFound404},
    }
)
async def delete_book(
    book_id: str = Path(..., pattern=r"^\d{6}$", description="6-digit book id", example="000001"),
    db: Session = Depends(get_db)
):
    return book_service.delete_book(book_id=book_id, db=db)

@router.get(
    '/',
    description="List all books (non-deleted) with pagination. Max 1000 items per request.",
    response_description="Paginated list of books",
    response_model=BooksListResponse200
)
async def get_books(
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    size: int = Query(50, ge=1, le=1000, description="Page size (max 1000)"),
    db: Session = Depends(get_db)
):
    return book_service.list_books(db=db, page=page, size=size)

@router.get(
    '/{book_id}',
    description = "Get single book deatails including current borrow status (if any)",
    response_description = 'Book details',
    response_model = BookDetailResponse200,
    responses = {
        404: {"description": "Book not found", "model": BookNotFound404},
    }
)
async def get_book(
    book_id: str = Path(..., pattern=r"^\d{6}$", description="6-digit book id", example="000001"),
    db: Session = Depends(get_db)
):
    return book_service.get_book_by_id(book_id=book_id, db=db)

@router.post(
    '/{book_id}/return/{card_id}',
    description="Return a book using a library card (6-digit ids).",
    response_description="Return completed",
    response_model=BookReturnResponse,
    responses={
        404: {"description": "Book or card not found", "model": BookNotFound404},
        409: {"description": "Book is not borrowed or borrowed by another card", "model": BookReturnResponse409}
    },
)
async def return_book(
    book_id: str = Path(..., pattern=r"^\d{6}$", description="6-digit book id", example="000001"),
    card_id: str = Path(..., pattern=r"^\d{6}$", description="6-digit card id", example="245781"),
    db: Session = Depends(get_db),
):
    return book_service.return_book(book_id=book_id, card_id=card_id, db=db)

@router.put(
    "/{book_id}",
    description="Update book fields; optionally change 6-digit book id (unique is required)",
    response_description="Updated book",
    response_model=BookItem,
    responses={
        409: {"description": "Book with given id already exists", "model": BookCreateResponse409},
    }
)
async def update_book(
    book_id: str = Path(..., pattern=r"^\d{6}$", description="Current 6-digit book id", example="000001"),
    payload: BookUpdatePayload = ...,
    db: Session = Depends(get_db),
):
    return book_service.update_book(db=db, book_id=book_id, payload=payload)

