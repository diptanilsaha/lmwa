import datetime
from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    IntegerField,
    DateField,
    DecimalField,
    FieldList,
    SelectField,
    FormField
)
from wtforms.validators import DataRequired, Length, NumberRange
from wtforms.validators import ValidationError
from app.books.models import Book, BookData, Author, Language, Publisher, BookStock
from app.db import db

class AuthorForm(FlaskForm):
    class Meta:
        csrf = False
    name = StringField('Author Name', validators=[DataRequired(), Length(min=1, max=50)])

class BookForm(FlaskForm):
    id = IntegerField('Book ID', validators=[DataRequired(), NumberRange(min=1)])
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    isbn = StringField('ISBN-10', validators=[DataRequired(), Length(min=10, max=10)])
    isbn13 = StringField('ISBN-13', validators=[DataRequired(), Length(min=13, max=13)])
    language_code = StringField('Language Code', validators=[DataRequired(), Length(min=2, max=10)])
    num_pages = IntegerField('Number of Pages', validators=[DataRequired(), NumberRange(min=1)])
    publication_date = DateField('Publication Date', format="%Y-%m-%d", validators=[DataRequired()])
    publisher_name = StringField('Publisher', validators=[DataRequired(), Length(max=50)])
    authors = FieldList(FormField(form_class=AuthorForm, default=Author), min_entries=1, max_entries=10)
    average_rating = DecimalField('Average Rating', validators=[DataRequired(), NumberRange(min=1.0, max=5.0)])
    ratings_count = IntegerField('Ratings Count', validators=[DataRequired(), NumberRange(min=1)])
    text_reviews_count = IntegerField('Text Reviews Count', validators=[DataRequired(), NumberRange(min=0)])

    def __init__(self, is_edit=False, *args, **kwargs):
        super(BookForm, self).__init__(*args, **kwargs)
        self.is_edit = is_edit
        if 'obj' in kwargs:
            book: Book = kwargs['obj']
            self.book = book

    def populate_book_obj(self, obj: object | Book):
        obj.id = self.id.data
        obj.title = self.title.data.strip()
        obj.isbn = self.isbn.data.strip()
        obj.isbn13 = self.isbn13.data.strip()
        obj.publication_date = self.publication_date.data
        obj.average_rating = self.average_rating.data
        obj.ratings_count = self.ratings_count.data
        obj.text_reviews_count = self.text_reviews_count.data

        language = Language.find_or_create_language(
            lang_code=self.language_code.data.strip()
        )
        obj.language_code = language.code

        publisher = Publisher.find_or_create_publisher(
            publisher_name=self.publisher_name.data.strip()
        )
        obj.publisher_name = publisher.name

        obj.authors = [
            Author.find_or_create_author(author_name=author.data['name'].strip())
            for author in self.authors.entries
        ]

    
    def validate_id(form, field):
        book: Book = db.session.get(Book, field.data)

        if not form.is_edit:
            if book is not None:
                raise ValidationError(f'BookId already exists. [{book.title}]')
            
        if form.is_edit:
            if field.data != form.book.id and book is not None:
                raise ValidationError(f'BookId already exists. [{book.title}]')

        
    def validate_publication_date(form, field):
        if field.data > datetime.date.today():
            raise ValidationError('Publication Date cannot be in future.')
        
    def prepare_bookdata(self) -> BookData:
        authors_entries = self.authors.entries
        authors = ""
        for author in authors_entries:
            authors += author.data['name'].strip() + '/'

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

class BookSearchForm(FlaskForm):
    class Meta:
        csrf = False
        
    search_by = SelectField(
        'Search by',
        validators=[DataRequired()],
        choices=[('', 'Search By'), ('title', 'Book Name'), ('author', 'Author')]
    )
    search_term = StringField('Search term', validators=[DataRequired()])