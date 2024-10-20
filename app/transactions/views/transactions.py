from typing import List
from flask import render_template, request
from sqlalchemy import and_, between
from app.db import db
from app.transactions.base import transactions_bp
from app.transactions.models import BookTransaction, Transaction
from app.transactions.forms import TransactionFilterForm

@transactions_bp.route('/')
def transactions():
    form: TransactionFilterForm = TransactionFilterForm(request.args)

    if form.validate():
        if form.issue_return_due.data == 'issue':
            transactions: List[BookTransaction] = db.session.execute(
                db.select(BookTransaction)
                .where(
                    and_(
                        between(
                            BookTransaction.issue_date,
                            form.from_date.data,
                            form.to_date.data
                        )
                    )
                )
                .order_by(BookTransaction.issue_date.desc())
            ).scalars().all()
        elif form.issue_return_due.data == 'due':
            transactions: List[BookTransaction] = db.session.execute(
                db.select(BookTransaction)
                .where(
                    and_(
                        between(
                            BookTransaction.due_date,
                            form.from_date.data,
                            form.to_date.data
                        )
                    )
                )
                .order_by(BookTransaction.issue_date.desc())
            ).scalars().all()
        else:
            transactions: List[BookTransaction] = db.session.execute(
                db.select(BookTransaction)
                .join(Transaction)
                .where(
                    and_(
                        between(
                            Transaction.return_date,
                            form.from_date.data,
                            form.to_date.data
                        )
                    )
                )
                .order_by(Transaction.return_date.desc())
            ).scalars().all()

        return render_template('transactions/transactions.html', transactions=transactions, form=form)
    
    transactions: List[BookTransaction] = db.session.execute(db.select(BookTransaction)).scalars().all()

    return render_template('transactions/transactions.html', transactions=transactions, form=form)