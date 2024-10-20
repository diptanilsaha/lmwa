import datetime
from flask import flash, render_template, redirect, url_for
from app.db import db
from app.books.models import BookStock
from app.books.base import books_bp
from app.books.forms import BookStockForm, Book

@books_bp.route('/<int:id>/add', methods=['GET', 'POST'])
def add_stock(id: int):
    book: Book = db.get_or_404(Book, id)
    form: BookStockForm = BookStockForm()

    if form.validate_on_submit():
        book_stock = BookStock(
            id = form.id.data,
            book_id = id,
            created_on = datetime.date.today()
        )
        db.session.add(book_stock)
        db.session.commit()
        flash(f'Stock - {book_stock.id} created successfully.', 'success')
        return redirect(url_for('books.book_view', id=id))
    
    return render_template('books/add_stock.html', form=form, book=book)