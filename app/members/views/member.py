from flask import render_template
from app.members.base import members_bp
from app.members.models import Member
from app.db import db

@members_bp.route('/<int:id>')
def member_view(id: int):
    member: Member = db.get_or_404(Member, id)

    return render_template('members/member.html', member=member)