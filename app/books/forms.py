import datetime
from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    IntegerField,
    DateField,
    DecimalField,
    FieldList
)
from wtforms.validators import DataRequired, Length, NumberRange
from wtforms.validators import ValidationError
from app.books.models import Book, BookData, Author, Language, Publisher, BookStock
from app.db import db

class BookForm(FlaskForm):
    id = IntegerField('Book ID', validators=[DataRequired(), NumberRange(min=1)])
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    isbn = StringField('ISBN-10', validators=[DataRequired(), Length(min=10, max=10)])
    isbn13 = StringField('ISBN-13', validators=[DataRequired(), Length(min=13, max=13)])
    language_code = StringField('Language Code', validators=[DataRequired(), Length(min=3, max=3)])
    num_pages = IntegerField('Number of Pages', validators=[DataRequired(), NumberRange(min=1)])
    publication_date = DateField('Publication Date', format="%Y-%m-%d", validators=[DataRequired()])
    publisher_name = StringField('Publisher', validators=[DataRequired(), Length(max=50)])
    authors = FieldList(StringField('Author Name', validators=[DataRequired(), Length(min=1, max=50)]), min_entries=1, max_entries=10)
    average_rating = DecimalField('Average Rating', validators=[DataRequired(), NumberRange(min=1.0, max=5.0)])
    ratings_count = IntegerField('Ratings Count', validators=[DataRequired(), NumberRange(min=1)])
    text_reviews_count = IntegerField('Text Reviews Count', validators=[DataRequired(), NumberRange(min=0)])

    def __init__(self, *args, **kwargs):
        super(BookForm, self).__init__(*args, **kwargs)
        if 'obj' in kwargs:
            book: Book = kwargs['obj']
            self.authors.data = [author.name for author in book.authors] if book.authors else []

    def populate_obj(self, obj: object | Book):
        super().populate_obj(obj)

        author_names = self.authors.data
        obj.authors = []
        for author_name in author_names:
            author = Author.find_or_create_author(author_name=author_name)
            obj.add_author(author)

        obj.language_code = Language.find_or_create_language(
            lang_code=self.language_code.data.strip()
        )

        obj.publisher = Publisher.find_or_create_publisher(
            publisher_name=self.publisher_name.data.strip()
        )

    
    def validate_id(form, field):
        book: Book = db.session.get(Book, field.data)

        if book is not None:
            raise ValidationError(f'BookId already exists. [{book.title}]')
        
    def validate_publication_date(form, field):
        if field.data > datetime.datetime.today():
            raise ValidationError('Publication Date cannot be in future.')
        
    def prepare_bookdata(self) -> BookData:
        authors_entries = self.authors.data
        authors = ""
        for author in authors_entries:
            authors += author.strip() + '/'

        return BookData(
            bookID=str(self.id.data),
            title=self.title.data.strip(),
            isbn=self.isbn.data.strip(),
            isbn13=self.isbn13.data.strip(),
            language_code=self.language_code.data.strip(),
            num_pages=str(self.num_pages.data),
            publication_date=self.publication_date.data.strftime('%m/%d/%Y'),
            publisher=self.publisher_name.data.strip(),
            authors=authors[:-1],
            average_rating=str(self.average_rating.data),
            ratings_count=str(self.ratings_count.data),
            text_reviews_count=str(self.text_reviews_count.data)
        )
    
class BookStockForm(FlaskForm):
    id = IntegerField('Stock ID', validators=[DataRequired(), NumberRange(min=1)])
    book_id = IntegerField('Book ID', validators=[DataRequired(), NumberRange(min=1)])

    def validate_id(form, field):
        book_stock: BookStock = db.session.get(BookStock, field.data)

        if book_stock is not None:
            raise ValidationError(f"Stock with Stock ID '{field.data}' exists.")
        
    def validate_book_id(form, field):
        book: Book = db.session.get(Book, field.data)

        if book is None:
            raise ValidationError(f"No book with Book ID - '{field.data}' exists.")