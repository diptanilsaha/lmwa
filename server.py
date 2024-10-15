from flask import Flask, render_template
from config import Config
from app.books.base import books_bp
from app.members.base import members_bp
from app.transactions.base import transactions_bp

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

    @app.route('/')
    def index():
        return render_template('base.html')

    return app


def init_db(app: Flask):
    from app.db import db, migrate
    
    db.init_app(app)
    migrate.init_app(app)


def register_blueprints(app: Flask):
    app.register_blueprint(books_bp)
    app.register_blueprint(members_bp)
    app.register_blueprint(transactions_bp)