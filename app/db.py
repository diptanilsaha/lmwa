from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import event

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
migrate = Migrate()

@event.listens_for(db.engine, "connect")
def enable_foreign_keys(dbapi_connection, connection_record):
    if db.engine.dialect.name == "sqlite":
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()