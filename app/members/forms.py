from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, SelectField
from wtforms.validators import DataRequired, Length, Email
from wtforms.validators import ValidationError
from app.db import db
from app.members.models import Member

class MemberForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=1, max=50)])
    email = EmailField('Email Address', validators=[DataRequired(), Email()])

    def validate_email(form, field):
        member: Member = db.session.execute(
            db.select(Member).filter_by(email=field.data)
        ).scalar_one_or_none()

        if member is not None:
            raise ValidationError(f"Member with '{field.data}' email already exists.")
        
class MemberSearchForm(FlaskForm):
    class Meta:
        csrf = False

    search_by = SelectField(
        'Search by',
        validators=[DataRequired()],
        choices=[('', 'Search by'), ('id', 'Member ID'), ('name', 'Name'), ('email', 'Email Address')]
    )
    search_term = StringField('Search term', validators=[DataRequired()])