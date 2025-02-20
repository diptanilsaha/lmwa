import enum
import decimal
import datetime
from typing import List
from typing import TypedDict
from sqlalchemy import (
    and_,
    Integer,
    String,
    ForeignKey,
    Date,
    Table,
    Column,
    Numeric
)
import sqlalchemy
from sqlalchemy.orm import (
    Mapped, 
    mapped_column,
    relationship
)
from app.db import db
from app.utils import strip_dict_keys

book_author_table = Table(
    "book_author_table",
    db.metadata,
    Column("book_id", ForeignKey("book.id", ondelete="CASCADE"), primary_key=True),
    Column("author_id", ForeignKey("author.name", ondelete="CASCADE"), primary_key=True)
)

class Author(db.Model):
    __tablename__ = "author"
    name: Mapped[str] = mapped_column(String(50), primary_key=True)
    books: Mapped[List["Book"]] = relationship(
        secondary=book_author_table, back_populates="authors", lazy="select"
    )
    
    @staticmethod
    def find_or_create_author(author_name: str):
        author: Author = db.session.get(Author, author_name)

        if author is not None:
            return author
        
        author = Author(name=author_name)
        db.session.add(author)
        return author
    
class Publisher(db.Model):
    __tablename__ = "publisher"
    name: Mapped[str] = mapped_column(String(50), primary_key=True)
    books: Mapped[List["Book"]] = relationship(back_populates="publisher", lazy="select")
    
    @staticmethod
    def find_or_create_publisher(publisher_name: str):
        publisher: Publisher = db.session.get(Publisher, publisher_name)

        if publisher is not None:
            return publisher
        
        publisher = Publisher(name=publisher_name)
        db.session.add(publisher)
        return publisher
    
class Language(db.Model):
    __tablename__ = "language"
    code: Mapped[str] = mapped_column(String(10), primary_key=True)
    books: Mapped[List["Book"]] = relationship(back_populates="language", lazy="select")

    @staticmethod
    def find_or_create_language(lang_code: str):
        language: Language = db.session.get(Language, lang_code)

        if language is not None:
            return language
        
        language = Language(code=lang_code)
        db.session.add(language)
        return language

class BookData(TypedDict):
    bookID: str
    title: str
    authors: str
    average_rating: str
    isbn: str
    isbn13: str
    language_code: str
    num_pages: str
    ratings_count: str
    text_reviews_count: str
    publication_date: str
    publisher: str 

class Book(db.Model):
    __tablename__ = "book"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    isbn: Mapped[str] = mapped_column(String(10))
    isbn13: Mapped[str] = mapped_column(String(13))
    language_code: Mapped[str] = mapped_column(ForeignKey("language.code"))
    language: Mapped["Language"] = relationship(back_populates="books", lazy="select")
    num_pages: Mapped[int] = mapped_column(Integer)
    publication_date: Mapped[datetime.date] = mapped_column(Date)
    publisher_name: Mapped[str] = mapped_column(ForeignKey("publisher.name"))
    publisher: Mapped["Publisher"] = relationship(back_populates="books", lazy="select")
    authors: Mapped[List["Author"]] = relationship(
        secondary=book_author_table, back_populates="books", lazy="select"
    )
    average_rating: Mapped[decimal.Decimal] = mapped_column(
        Numeric(precision=3, scale=2)
    )
    ratings_count: Mapped[int] = mapped_column(Integer)
    text_reviews_count: Mapped[int] = mapped_column(Integer)
    stocks: Mapped[List["BookStock"]] = relationship(
        back_populates="book", 
        lazy="select",
        cascade="all, delete-orphan"
    )
    
    @property
    def is_available(self):
        if self.stocks:
            for stock in self.stocks:
                if stock.status == StockStatus.AVAILABLE:
                    return True
        return False
    
    @property
    def book_safe_to_delete(self):
        if self.stocks:
            for stock in self.stocks:
                if stock.status == StockStatus.TAKEN:
                    return False
        return True

    
    @property
    def total_stocks(self):
        return len(self.stocks)
    
    def have_author(self, author: str | Author):
        if type(author) == str:
            author = db.session.get(Author, author)

        return author in self.authors
    
    def add_author(self, author: Author):
        if not self.have_author(author):
            self.authors.append(author)

    @staticmethod
    def find_or_create_book(book_data: BookData):
        book_data = strip_dict_keys(book_data)
        book: Book = db.session.get(Book, book_data['bookID'])

        if book is not None:
            return book

        book = Book()
        authors = []
        for author_name in book_data["authors"].split('/'):
            author = Author.find_or_create_author(
                author_name=author_name
            )
            authors.append(author)
        language = Language.find_or_create_language(lang_code=book_data["language_code"])
        book.language_code = language.code

        publisher = Publisher.find_or_create_publisher(publisher_name=book_data["publisher"])
        book.publisher_name = publisher.name

        book.id = int(book_data['bookID'])
        book.title = book_data['title']
        book.isbn = book_data['isbn']
        book.isbn13 = book_data['isbn13']
        book.num_pages = int(book_data['num_pages'])
        book.publication_date = datetime.datetime.strptime(
            book_data['publication_date'],
            '%m/%d/%Y'
        )
        book.average_rating = decimal.Decimal(book_data['average_rating'])
        book.ratings_count = int(book_data['ratings_count'])
        book.text_reviews_count = int(book_data['text_reviews_count'])

        for author in authors:
            book.add_author(author)

        db.session.add(book)
        return book

class StockStatus(enum.Enum):
    TAKEN = 'taken'
    AVAILABLE = 'available'

class BookStock(db.Model):
    __tablename__ = "book_stock"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("book.id", ondelete="CASCADE"))
    book: Mapped["Book"] = relationship(back_populates="stocks")
    status: Mapped[StockStatus] = mapped_column(
        sqlalchemy.Enum(StockStatus),
        default=StockStatus.AVAILABLE
    )

    transactions: Mapped[List["BookTransaction"]] = relationship(
        "BookTransaction", 
        back_populates="stock",
        cascade="all, delete-orphan"
    )
    created_on: Mapped[datetime.date] = mapped_column(Date)

    @staticmethod
    def find_stock(stock_id: int, book_id: int):
        book_stock: BookStock = db.session.execute(
            db.select(BookStock)
            .where(
                and_(
                    BookStock.id == stock_id,
                    BookStock.book_id == book_id
                )
            )
        ).scalar_one_or_none()

        return book_stock
    
    @staticmethod
    def create_stock(stock_id: int, book_id: int):
        book_stock: BookStock = BookStock.find_stock(stock_id, book_id)
        
        if book_stock:
            return None # if already created.
        
        try:
            book_stock = BookStock(
                id=stock_id,
                book_id=book_id,
                created_on=datetime.date.today()
            )
            db.session.add(book_stock)
        except:
            return None # if exception occurs
        
        return book_stock
    
from app.transactions.models import BookTransaction