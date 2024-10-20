import datetime
from flask import render_template, flash, redirect, url_for
from app.members.base import members_bp
from app.members.models import Member
from app.members.forms import MemberForm
from app.db import db

@members_bp.route('/add', methods=['GET', 'POST'])
def add_member():
    form: MemberForm = MemberForm()

    if form.validate_on_submit():
        member = Member(
            name = form.name.data.strip(),
            email = form.email.data.strip(),
            joining_date = datetime.date.today()
        )
        db.session.add(member)
        db.session.commit()
        flash(f'Member - {member.id} created successfully.', 'success')
        return redirect(url_for('members.members'))
    
    return render_template('members/add_member.html', form=form)