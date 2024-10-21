from typing import List
from flask import flash, redirect, url_for, render_template, request
from sqlalchemy import and_, not_
from app.db import db
from app.members.models import Member
from app.transactions.models import BookTransaction
from app.transactions.forms import ReturnBookForm, ReturnBookMemberForm
from app.transactions.base import transactions_bp

@transactions_bp.route('/return', methods=['GET', 'POST'])
def return_book():
    form: ReturnBookForm = ReturnBookForm()
    member_form: ReturnBookMemberForm = ReturnBookMemberForm(request.args)

    if member_form.validate():
        member_email = member_form.member_email.data
        transactions: List[BookTransaction] = db.session.execute(
            db.select(BookTransaction)
            .join(Member)
            .where(
                Member.email == member_email,
                BookTransaction.transaction == None
            )
            .order_by(BookTransaction.issue_date.desc())
        ).scalars().all()

        return render_template('transactions/return_book.html', form=member_form, transactions=transactions)


    if form.validate_on_submit():
        book_trans_id = int(form.trans_id.data.strip())
        rent_paid = bool(int(form.rent_paid.data.strip()))
        book_trans: BookTransaction = db.get_or_404(BookTransaction, book_trans_id)

        if book_trans.return_book(rent_paid):
            if not rent_paid:
                flash(f'Transaction {book_trans_id} - Book returned, rent put on member\'s due.', 'warning')
            else:
                flash(f'Transaction {book_trans_id} - Book returned, rent collected.', 'success')

        db.session.commit()
        return redirect(url_for('transactions.transaction', id=book_trans_id))
    
    return render_template('transactions/return_book.html', form=member_form)