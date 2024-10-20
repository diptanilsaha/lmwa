from flask import Flask, redirect, url_for
from config import Config
from app.db import db, migrate
from app.books.base import books_bp
from app.members.base import members_bp
from app.transactions.base import transactions_bp
from app.members.models import Member
from app.transactions.models import BookTransaction, Transaction
from app.books.models import Author, Publisher, Book, Language, BookStock

def create_app(debug: bool = False, config_class: Config = Config) -> Flask:
    app = Flask(
        __name__,
        static_folder='app/static',
        template_folder='app/templates'
    )
    app.debug = debug
    app.config.from_object(config_class)

    init_db(app)
    register_blueprints(app)

    @app.shell_context_processor
    def make_shell_context():
        return {
            'db': db,
            'Author': Author,
            'Book': Book,
            'BookStock': BookStock,
            'BookTransaction': BookTransaction,
            'Language': Language,
            'Member': Member,
            'Publisher': Publisher,
            'Transaction': Transaction
        }

    @app.route('/')
    def index():
        return redirect(url_for('books.books'))

    return app


def init_db(app: Flask):
    from app.db import db, migrate
    from sqlalchemy import event
    
    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        @event.listens_for(db.engine, "connect")
        def enable_foreign_keys(dbapi_connection, connection_record):
            if db.engine.dialect.name == "sqlite":
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.close()


def register_blueprints(app: Flask):
    app.register_blueprint(books_bp)
    app.register_blueprint(members_bp)
    app.register_blueprint(transactions_bp)