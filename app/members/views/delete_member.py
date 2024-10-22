from flask import redirect, flash, url_for
from app.db import db
from app.members.models import Member
from app.members.base import members_bp

@members_bp.route('/<int:id>/delete', methods=['POST'])
def delete_member(id: int):
    member: Member = db.get_or_404(Member, id)
    member_id = member.id

    if member.no_of_books_currently_rented:
        flash(f'Member - {member_id} have to return book before deletion.', 'danger')
    else:
        db.session.delete(member)
        db.session.commit()
        flash(f'Member - {member_id} deleted successfully.', 'success')
    return redirect(url_for('members.members'))