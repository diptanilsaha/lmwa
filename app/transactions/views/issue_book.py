from flask import flash, url_for, redirect, render_template, request, abort
from app.db import db
from app.transactions.base import transactions_bp
from app.books.models import BookStock
from app.members.models import Member
from app.transactions.models import BookTransaction
from app.transactions.forms import BookIssueForm

@transactions_bp.route('/issue', methods=['GET', 'POST'])
def issue_book():
    form: BookIssueForm = BookIssueForm()

    if form.validate_on_submit():
        stock_id = form.stock_id.data
        member_email = form.member_email.data.strip()
        return redirect(url_for('transactions.confirm_issue_book', stock_id=stock_id, member_email=member_email))
    
    return render_template('transactions/issue_book.html', form=form, confirm=False, action_url=url_for('transactions.issue_book'))

@transactions_bp.route('/issue/confirm', methods=['GET', 'POST'])
def confirm_issue_book():

    if request.method == 'POST':
        form: BookIssueForm = BookIssueForm(request.form)
        
        if form.validate_on_submit():
            book_transaction: BookTransaction = BookTransaction.issue_book(
                form.stock_id.data, form.member_email.data
            )
            if not book_transaction:
                flash(f'Stock is unavailable or member have outstanding dues.', 'danger')
                return redirect(url_for('transactions.issue_book'))
            db.session.commit()
            flash(f'"{book_transaction.stock.book.title}" rented to {book_transaction.member.name}.', 'success')
            return redirect(url_for('transactions.transaction', id=book_transaction.id))
        
    form: BookIssueForm = BookIssueForm(request.args)
        
    stock_id = form.stock_id.data
    member_email = form.member_email.data

    if not stock_id:
        abort(404)

    if not member_email:
        abort(404)

    book_stock: BookStock = db.get_or_404(BookStock, stock_id)
    member: Member = db.session.execute(
        db.select(Member).filter_by(email=member_email)
    ).scalar_one_or_none()

    if not member:
        abort(404)

    return render_template(
        'transactions/issue_book.html', 
        form=form, 
        confirm=True, 
        book_stock=book_stock, 
        member=member, 
        action_url=url_for('transactions.confirm_issue_book')
    )