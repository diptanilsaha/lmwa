from flask_wtf import FlaskForm
from wtforms import IntegerField, EmailField, SelectField, DateField, HiddenField
from wtforms.validators import DataRequired, NumberRange, Email
from wtforms.validators import ValidationError
from app.db import db
from app.books.models import BookStock, StockStatus
from app.members.models import Member

class BookIssueForm(FlaskForm):
    stock_id = IntegerField('Stock ID', validators=[DataRequired(), NumberRange(min=1)])
    member_email = EmailField('Member Email Address', validators=[DataRequired(), Email()])

    def validate_stock_id(form, field):
        stock: BookStock = db.session.get(BookStock, field.data)

        if stock is None:
            raise ValidationError('Stock not found.')
        
        if stock.status == StockStatus.TAKEN:
            raise ValidationError('Stock is not available.')

        
    def validate_member_email(form, field):
        member: Member = db.session.execute(db.select(Member).filter_by(email=field.data)).scalar_one_or_none()

        if member is None:
            raise ValidationError('Member not found.')
        
        if not member.is_allowed_to_rent_book:
            raise ValidationError('Member is not allowed to rent book.')
        
class TransactionFilterForm(FlaskForm):
    class Meta:
        csrf = False

    issue_return_due = SelectField(
        'Issue/Due/Return',
        validators=[DataRequired()],
        choices=[
            ('', 'Select'),
            ('issue', 'Issue Date'),
            ('due', 'Due Date'),
            ('return', 'Return Date')
        ]
    )
    from_date = DateField('From Date', validators=[DataRequired()])
    to_date = DateField('To Date', validators=[DataRequired()])

    def validate_from_date(form, field):
        if field.data > form.to_date.data:
            raise ValidationError('From Date can\'t be greater than To Date.')
        
    def validate_to_date(form, field):
        if field.data < form.from_date.data:
            raise ValidationError('To Date can\'t be lesser than From Date.')
        
class ReturnBookMemberForm(FlaskForm):
    class Meta:
        csrf = False

    member_email = EmailField('Member Email', validators=[DataRequired()])

class ReturnBookForm(FlaskForm):
    trans_id = HiddenField()
    rent_paid = HiddenField()

class CollectRentForm(FlaskForm):
    trans_id = HiddenField()