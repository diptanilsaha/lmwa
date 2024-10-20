from flask import render_template, flash, redirect, url_for
from app.db import db
from app.members.models import Member
from app.members.forms import MemberForm
from app.members.base import members_bp

@members_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit_member(id: int):
    member: Member = db.get_or_404(Member, id)
    form: MemberForm = MemberForm(obj=member)

    if form.validate_on_submit():
        form.populate_obj(member)
        db.session.commit()
        flash(f'Member - {member.id} got updated successfully.', 'warning')
        return redirect(url_for('members.member_view', id=member.id))
    
    return render_template('members/edit_member.html', form=form, member=member)