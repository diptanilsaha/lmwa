from flask import render_template
from app.books.base import books_bp
from app.db import db
from app.books.models import Book

@books_bp.route('/<int:id>')
def book_view(id: int):
    book: Book = db.get_or_404(Book, id)

    return render_template('books/book.html', book=book)