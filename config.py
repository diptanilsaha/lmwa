import os
from dotenv import load_dotenv

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(ROOT_DIR, 'db.sqlite3')
    SQLALCHEMY_TRACK_MODIFICATION = False
    LOAN_PERIOD = os.getenv('LOAN_PERIOD') # In days
    FIXED_RENT = os.getenv('FIXED_RENT') # In rupees
    DAILY_FINE = os.getenv('DAILY_FINE') # In rupees
    NO_OF_BOOKS_RENTED_AT_A_TIME = os.getenv('NO_OF_BOOKS_RENTED_AT_A_TIME') # Count of books can be rented at a time.
    PERMITTED_AMOUNT_OF_DUES = os.getenv('PERMITTED_AMOUNT_OF_DUES') # In Rupees: Rs. 500 /-