from flask import flash, url_for, redirect, render_template
from app.db import db
from app.transactions.base import transactions_bp
from app.transactions.models import BookTransaction
from app.transactions.forms import CollectRentForm

@transactions_bp.route('/collectRent', methods=['POST'])
def collect_rent():
    form: CollectRentForm = CollectRentForm()

    if form.validate_on_submit():
        trans_id: int = int(form.trans_id.data)
        book_trans: BookTransaction = db.get_or_404(BookTransaction, trans_id)

        if book_trans.is_due_paid:
            flash(f'Rent already paid for Transaction - {book_trans.id}', 'warning')
            return redirect(url_for('transactions.transaction', id=trans_id))
        
        book_trans.pay_due()
        db.session.commit()
        flash(f'Rent paid for Transaction - {book_trans.id} successfully.', 'success')
        return redirect(url_for('transactions.transaction', id=trans_id))