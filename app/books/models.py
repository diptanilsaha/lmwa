import enum
import datetime
from typing import List
from sqlalchemy import (
    Integer,
    String,
    ForeignKey,
    Date,
    Table,
    Column
)
import sqlalchemy
from sqlalchemy.orm import (
    Mapped, 
    mapped_column,
    relationship
)
from app.db import db
from app.transactions.models import BookTransaction

book_author_table = Table(
    "book_author_table",
    db.metadata,
    Column("book_id", ForeignKey("book.id"), primary_key=True),
    Column("author_id", ForeignKey("author.id"), primary_key=True)
)

class Author(db.Model):
    __tablename__ = "author"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    books: Mapped[List["Book"]] = relationship(
        secondary=book_author_table, back_populates="authors"
    )

    def __repr__(self):
        return f'<Author {self.name}>'
    
class Publisher(db.Model):
    __tablename__ = "publisher"
    name: Mapped[str] = mapped_column(String(50), primary_key=True)
    books: Mapped[List["Book"]] = relationship(back_populates="publisher")

    def __repr__(self):
        return f'<Publisher {self.name}>'
    
class Language(db.Model):
    __tablename__ = "language"
    code: Mapped[str] = mapped_column(String(2), primary_key=True)
    language: Mapped[str] = mapped_column(String(20))
    books: Mapped[List["Book"]] = relationship(back_populates="language")

    def __repr__(self):
        return f'<Language {self.code}>'    

class Book(db.Model):
    __tablename__ = "book"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    isbn: Mapped[str] = mapped_column(String(10))
    isbn13: Mapped[str] = mapped_column(String(13))
    language_code: Mapped[str] = mapped_column(ForeignKey("language.code"))
    language: Mapped["Language"] = relationship(back_populates="books")
    num_pages: Mapped[int] = mapped_column(Integer)
    publication_date: Mapped[datetime.date] = mapped_column(Date)
    publisher_name: Mapped[str] = mapped_column(ForeignKey("publisher.name"))
    publisher: Mapped["Publisher"] = relationship(back_populates="books")
    authors: Mapped[List["Author"]] = relationship(
        secondary=book_author_table, back_populates="books"
    )
    stocks: Mapped[List["BookStock"]] = relationship(back_populates="book")

    def __repr__(self):
        return f'<Book {self.id}>'
    
    @property
    def is_available(self):
        for stock in self.stocks:
            if stock.status == StockStatus.TAKEN:
                return False
        return True
    
    @property
    def total_stocks(self):
        return len(self.stocks)

class StockStatus(enum.Enum):
    TAKEN = 'taken'
    AVAILABLE = 'available'

class BookStock(db.Model):
    __tablename__ = "book_stock"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("book.id"))
    book: Mapped["Book"] = relationship(back_populates="stocks")
    status: Mapped[StockStatus] = mapped_column(
        sqlalchemy.Enum(StockStatus),
        default=StockStatus.AVAILABLE
    )

    members_rented: Mapped[List["BookTransaction"]] = relationship(
        back_populates="books_rented"
    )

    def __repr__(self):
        return f'<BookStock {self.id}>'