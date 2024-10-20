from typing import List
from flask import render_template, request
from app.members.base import members_bp
from app.members.models import Member
from app.members.forms import MemberSearchForm
from app.db import db

@members_bp.route('/')
def members():
    form: MemberSearchForm = MemberSearchForm(request.args)

    if form.validate():
        if form.search_by.data == 'id':
            members: List[Member] = db.session.execute(
                db.select(Member)
                .filter_by(id=form.search_term.data.strip())
            ).scalars().all()
        elif form.search_by.data == 'email':
            members: List[Member] = db.session.execute(
                db.select(Member)
                .filter_by(email=form.search_term.data.strip())
            ).scalars().all()
        else:
            members: List[Member] = db.session.execute(
                db.select(Member)
                .where(Member.name.ilike(f"%{form.search_term.data.strip()}%"))
            ).scalars().all()
        return render_template('members/members.html', form=form, members=members)
    
    members: List[Member] = db.session.execute(db.select(Member)).scalars().all()
    return render_template('members/members.html', form=form, members=members)