from core.db.base_class import Base
from sqlalchemy import Column, CheckConstraint, ForeignKey, DateTime, Index, Integer, String, text

class Borrowing(Base):
    __tablename__ = "borrowings"
    __table_args__ = (
        CheckConstraint("returned_at IS NULL OR borrowed_at <= returned_at", name="ck_borrow_time_order"),
        Index(
            "ux_borrowings_book_active",
            "book_id",
            unique=True,
            postgresql_where="returned_at IS NULL"  # <--- partial unique index
        ),
    )
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    book_id = Column(String(6), ForeignKey("books.id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False)
    card_id = Column(String(6), ForeignKey("cards.id", ondelete="RESTRICT"), nullable=False)
    borrowed_at = Column(DateTime, nullable=False, server_default=text("NOW()"))
    returned_at = Column(DateTime, nullable=True)

class Books(Base):
    __tablename__ = "books"
    __table_args__ = (
        CheckConstraint("length(id) = 6 AND id ~ '^[0-9]+$'", name="ck_book_id_format"),
        CheckConstraint("deleted_at IS NULL OR created_at <= deleted_at", name="ck_book_time_order"),
        Index("idx_books_title", "title"),
        Index("idx_books_author", "author"),
    )
    id = Column(String(6), primary_key=True, index=True, nullable=False)
    title  = Column(String(255), nullable=False)
    author = Column(String(100), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=text("NOW()"))
    deleted_at = Column(DateTime, nullable=True)

class Cards(Base):
    __tablename__ = "cards"
    __table_args__ = (
        CheckConstraint("length(id) = 6 AND id ~ '^[0-9]+$'", name="ck_card_number_id_format"),
    )
    id = Column(String(6), primary_key=True, index=True, nullable=False)