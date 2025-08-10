from pydantic import BaseModel, Field
from typing import List, Literal, Optional
from typing_extensions import Annotated

SixDigits = Annotated[str, Field(pattern=r"^\d{6}$")]

class Response200(BaseModel):
    code: Literal[200] = Field(
        ...,
        description="HTTP status code indicating that the operation was successful",
        example=200
    )

class Response404(BaseModel):
    code: Literal[404] = Field(
        ...,
        description="HTTP status code indicating that resource is not found",
        example=404
    )

class Response409(BaseModel):
    code: Literal[409] = Field(
        ...,
        description="HTTP status code indicating a conflict (e.g., resource already exists)",
        example=409
    )
    
class BookCreatePayload(BaseModel):
    class Config:
        extra = "forbid"
        
    id: SixDigits = Field(
        ..., 
        description="Six-digit unique serial number of the book. Leading zeros allowed",
        example="000001"
    )
    title: str = Field(
        ..., 
        min_length=1, 
        max_length=255, 
        description="Title of the book",
        example="W pustyni i w puszczy"
    )
    author: str = Field(
        ..., 
        min_length=1, 
        max_length=255, 
        description="Author of the book",
        example="Henryk Sienkiewicz" 
    )

class BookCreateResponse200(Response200):
    bookId: str = Field(
        ...,
        description="Six-digit unique serial number of the book. Leading zeros allowed",
        example='000001'
        )
    
class BookCreateResponse409(Response409):
    error: str = Field(
        ...,
        description="Error details",
        example='Book with given id already exists'
        )

class BookDeleteResponse200(Response200):
    status: str = Field(
        ...,
        description="Information about successful operation",
        example='Success'
        )

class BookItem(BaseModel):
    author: str = Field(..., description="Author of the book", example="Henryk Sienkiewicz")
    borrowed: bool = Field(..., description="Is the book currently borrowed?")
    borrowCardId: Optional[int] = Field(None, description="Active Card id, if borrowed")
    created_at: str = Field(..., description="Creation timestamp (ISO 8601)", example="2025-08-09T12:34:56+00:00")
    id: str = Field(..., pattern=r"^\d{6}$", description="Six-digit book ID", example="000123")
    title: str = Field(..., description="Title of the book", example="W pustyni i w puszczy")

class BookDetailResponse200(BookItem, Response200):
    pass

class BookNotFound404(Response404):
    error: str = Field(..., example="Book not found")

class BooksListResponse200(Response200):
    items: List[BookItem] = Field(default_factory=list, description="Page items")
    page: int = Field(..., ge=1, description="Current page number", example=1)
    size: int = Field(..., ge=1, le=1000, description="Page size (max 1000)", example=50)
    total: int = Field(..., ge=0, description="Total number of matching books", example=1234)
    total_pages: int = Field(..., ge=0, description="Total pages", example=25)

class BookUpdatePayload(BaseModel):
    class Config:
        extra = "forbid"

    author: Optional[str] = Field(
        None,
        min_length=1, 
        max_length=255, 
        description="Author of the book",
        example="Henryk Sienkiewicz" 
    )
    id: Optional[SixDigits] = Field(
        None,
        description="Six-digit unique serial number of the book. Leading zeros allowed",
        example="000001"
    )
    title: Optional[str] = Field(
        None,
        min_length=1, 
        max_length=255, 
        description="Title of the book",
        example="W pustyni i w puszczy"
    )

class BookReturnResponse(BookDeleteResponse200):
    pass

class BookReturnResponse409(Response409):
    error: str = Field(..., example="Book is not borrowed")

class BorrowCreateResponse200(Response200):
    bookId: SixDigits = Field(..., description="6-digit book id", example="000123")
    cardId: SixDigits = Field(..., description="6-digit card id", example="000456")
    borrowed_at: str = Field(..., description="Borrow timestamp (ISO 8601)", example="2025-08-09T12:34:56+00:00")

class BorrowCreateResponse409(Response409):
    error: str = Field(..., example="Book is already borrowed")