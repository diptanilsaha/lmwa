from flask import render_template, flash, redirect, url_for
from app.db import db
from app.books.models import Book
from app.books.forms import ImportBookForm
from app.books.base import books_bp
from app.utils import get_books_from_api

@books_bp.route('/import', methods=['GET', 'POST'])
def import_books():
    form: ImportBookForm = ImportBookForm()

    if form.validate_on_submit():
        number_of_entries = form.no_of_books.data
        title = form.title.data

        books_data = get_books_from_api(title, number_of_entries)
        return render_template(
            'books/import.html',
            form=form,
            confirm=True, 
            books_data=books_data,
            action_url=url_for('books.confirm_import_books')
        )
    
    return render_template('books/import.html', confirm=False, form=form, action_url=url_for('books.import_books'))

@books_bp.route('/import/confirm', methods=['POST'])
def confirm_import_books():
    form: ImportBookForm = ImportBookForm()

    if form.validate_on_submit():
        number_of_entries = form.no_of_books.data
        title = form.title.data

        books_data = get_books_from_api(title, number_of_entries)

        books = [Book.find_or_create_book(book) for book in books_data ]
        db.session.commit()
        flash('Books imported successfully.', 'success')
        return redirect(url_for('books.books'))