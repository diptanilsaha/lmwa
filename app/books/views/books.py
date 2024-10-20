from typing import List
from flask import request, render_template
from app.db import db
from app.books.base import books_bp
from app.books.models import Book, book_author_table, Author
from app.books.forms import BookSearchForm

@books_bp.route('/')
def books():
    form: BookSearchForm = BookSearchForm(request.args)

    if form.validate():
        if form.search_by.data == 'author':
            books: List[Book] = db.session.execute(
                db.select(Book)
                .join(book_author_table)
                .join(Author)
                .where(Author.name.ilike(f"%{form.search_term.data}%"))
            ).scalars().all()
        else:
            books: List[Book] = db.session.execute(
                db.select(Book).where(Book.title.ilike(f"%{form.search_term.data}%"))
            ).scalars().all()
        return render_template('books/books.html', form=form, books=books)
    

    books: List[Book] = db.session.execute(db.select(Book)).scalars().all()
    
    return render_template('books/books.html', form=form, books=books)