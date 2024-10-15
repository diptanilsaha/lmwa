from flask import Blueprint

books_bp = Blueprint(
    "books",
    import_name=__name__,
    url_prefix='/books',
    template_folder='templates'
)