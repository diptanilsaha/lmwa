from sqlalchemy import and_
from flask import abort, render_template
from app.db import db
from app.books.models import BookStock
from app.books.base import books_bp

@books_bp.route('/<int:bid>/<int:sid>')
def stock(bid: int, sid :int):
    book_stock: BookStock = db.session.execute(
        db.select(BookStock)
        .where(
            and_(
                BookStock.id == sid,
                BookStock.book_id == bid
            )
        )
    ).scalar_one_or_none()

    if not book_stock:
        abort(404)

    return render_template('books/stock.html', book_stock=book_stock)

    