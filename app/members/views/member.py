from flask import render_template, flash, redirect, url_for
from app.members.base import members_bp
from app.members.models import Member
from app.db import db

@members_bp.route('/<int:id>')
def member_view(id: int):
    member: Member = db.get_or_404(Member, id)

    return render_template('members/member.html', member=member)

@members_bp.route('/<int:id>/clear', methods=['POST'])
def member_clear_all_dues(id: int):
    member: Member = db.get_or_404(Member, id)

    member.pay_all_dues()
    db.session.commit()
    flash('All debt is paid by the member.', 'success')
    return redirect(url_for('members.member_view', id=member.id))