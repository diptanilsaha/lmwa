from flask import Blueprint

transactions_bp = Blueprint(
    "transactions",
    import_name=__name__,
    url_prefix='/transactions',
    template_folder='templates'
)