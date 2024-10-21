from flask import render_template
from app.db import db
from app.transactions.models import BookTransaction
from app.transactions.forms import ReturnBookForm, CollectRentForm
from app.transactions.base import transactions_bp

@transactions_bp.route('/<int:id>/')
def transaction(id: int):
    rbform: ReturnBookForm = ReturnBookForm()
    crform: CollectRentForm = CollectRentForm()
    transaction: BookTransaction = db.session.get(BookTransaction, id)

    return render_template('transactions/transaction.html', transaction=transaction, rbform=rbform, crform=crform)