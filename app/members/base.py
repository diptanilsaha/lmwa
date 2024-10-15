from flask import Blueprint

members_bp = Blueprint(
    "members",
    import_name=__name__,
    url_prefix='/members',
    template_folder='templates'
)