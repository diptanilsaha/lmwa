from flask import render_template, redirect, url_for, flash
from app.books.forms import BookForm
from app.books.base import books_bp
from app.books.models import Book, BookData
from app.db import db

@books_bp.route('/add', methods=['GET', 'POST'])
def add_book():
    form: BookForm = BookForm()

    if form.validate_on_submit():
        book_data: BookData = form.prepare_bookdata()
        Book.find_or_create_book(book_data=book_data)
        db.session.commit()
        return redirect(url_for('books.books'))
    
    for error in form.errors:
        flash(error, 'danger')
    return render_template('books/add_book.html', form=form)