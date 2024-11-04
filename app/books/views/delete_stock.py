from sqlalchemy import and_
from flask import abort, redirect, flash, url_for
from app.db import db
from app.books.models import BookStock, StockStatus
from app.books.base import books_bp

@books_bp.route('/<int:bid>/DeleteStock/<int:sid>', methods=['POST'])
def delete_stock(bid: int, sid :int):
    book_stock: BookStock = BookStock.find_stock(stock_id=sid, book_id=bid)

    if not book_stock:
        abort(404)

    stock_id: int = book_stock.id
    book_id: int = book_stock.book_id

    if book_stock.status == StockStatus.TAKEN:
        flash(f"Stock ID - {stock_id} is currently rented.", "danger")
        return redirect(url_for('books.stock', bid=book_id, sid=stock_id))

    db.session.delete(book_stock)
    db.session.commit()
    flash(f"Stock ID - {stock_id} deleted successfully.", "success")
    return redirect(url_for('books.book_view', id=book_id))