from flask import redirect, flash, url_for
from app.db import db
from app.books.base import books_bp
from app.books.models import Book

@books_bp.route('/<int:id>/delete', methods=['POST'])
def delete_book(id: int):
    book: Book = db.get_or_404(Book, id)
    book_id: int = book.id

    if not book.book_safe_to_delete:
        flash(f"Book ID - {book_id} cannot be deleted as stocks are rented.", "danger")
    else:
        db.session.delete(book)
        db.session.commit()
        flash(f"Book ID - {book_id} deleted successfully.", "success")
    return redirect(url_for('books.books'))