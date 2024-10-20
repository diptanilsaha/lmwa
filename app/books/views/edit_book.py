from flask import render_template, flash, redirect, url_for
from wtforms.validators import ValidationError
from app.db import db
from app.books.base import books_bp
from app.books.models import Book
from app.books.forms import BookForm

@books_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit_book(id: int):
    book: Book = db.get_or_404(Book, id)
    form: BookForm = BookForm(obj=book, is_edit=True)

    if form.validate_on_submit():
        try:
            form.populate_book_obj(book)
            db.session.commit()
            flash(f"Book-{book.id} updated successfully.", "success")
        except:
            flash(f"Book-{book.id} could not be updated.", "danger")
            raise 
            
        return redirect(url_for('books.book_view', id=book.id))
    
    return render_template('books/edit_book.html', form=form)