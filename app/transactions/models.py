import enum
import datetime
import sqlalchemy
from sqlalchemy import (
    Integer,
    ForeignKey,
    Date
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)
from app.db import db
from app.members.models import Member
from config import Config

class BookTransaction(db.Model):
    __tablename__ = "book_transaction"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    stock_id: Mapped[int] = mapped_column(ForeignKey("book_stock.id", ondelete="CASCADE"))
    member_id: Mapped[int] = mapped_column(ForeignKey("member.id", ondelete="CASCADE"))
    issue_date: Mapped[datetime.date] = mapped_column(Date)
    due_date: Mapped[datetime.date] = mapped_column(Date)
    transaction: Mapped["Transaction"] = relationship(back_populates="book_transaction")

    stock: Mapped["BookStock"] = relationship(back_populates="transactions")
    member: Mapped["Member"] = relationship(back_populates="transactions")

    def __repr__(self):
        return f'<BookTransaction {self.id}>'
    
    def set_issue_and_due_date(self, issue_date: datetime.date):
        self.issue_date = issue_date
        self.due_date = issue_date + datetime.timedelta(days=Config.LOAN_PERIOD)
    
    @property
    def is_returned(self):
        return self.transaction is not None and self.stock.status == StockStatus.AVAILABLE
    
    @property
    def loan_period(self):
        return Config.LOAN_PERIOD
    
    @property
    def daily_fine(self):
        return Config.DAILY_FINE
    
    @property
    def fixed_rent(self):
        return Config.FIXED_RENT
    
    @property
    def extra_days(self):
        if not self.is_returned:
            extra = datetime.datetime.today() - self.due_date
            return extra.days
        return self.transaction.extra_days
    
    @property
    def total_fine(self):
        if not self.is_returned:
            return self.extra_days * self.daily_fine
        return self.transaction.total_fine
    
    @property
    def total_rent(self):
        if not self.is_returned:
            return self.total_fine + self.fixed_rent
        return self.transaction.total_rent

    def return_book(self, due_paid: bool = False):
        if not self.is_returned:
            try:
                Transaction.create_transaction(self, due_paid)
                self.stock.status = StockStatus.AVAILABLE
            except:
                return False
        return True
    
    def return_book_and_due_paid(self):
        self.return_book(due_paid=True)

    @property
    def is_due_paid(self):
        if self.transaction is None:
            return False
        return self.transaction.status == TransactionStatus.PAID
    
    def pay_due(self):
        if not self.is_due_paid:
            self.transaction.pay_due()
            db.session.commit()

class TransactionStatus(enum.Enum):
    PAID = "paid"
    DUE = "due"

class Transaction(db.Model):
    __tablename__ = "transaction"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    book_trans_id: Mapped[int] = mapped_column(ForeignKey("book_transaction.id", ondelete="CASCADE"))
    book_transaction: Mapped["BookTransaction"] = relationship(
        back_populates="transaction"
    )
    return_date: Mapped[datetime.date] = mapped_column(Date)
    extra_days: Mapped[int] = mapped_column(Integer)
    total_fine: Mapped[int] = mapped_column(Integer)
    total_rent: Mapped[int] = mapped_column(Integer)
    status: Mapped[TransactionStatus] = mapped_column(
        sqlalchemy.Enum(TransactionStatus),
        default=TransactionStatus.DUE   
    )

    def __repr__(self):
        return f'<Transaction {self.id}>'
    
    @staticmethod
    def create_transaction(book_trans: BookTransaction, due_paid: bool = False):
        if book_trans is None:
            raise ValueError("'book_trans' cannot be NoneType.")
        
        if type(book_trans) != BookTransaction:
            raise TypeError("'book_trans' can be only a BookTransaction object.")
        
        transaction = Transaction()
        transaction.book_transaction = book_trans

        transaction.return_date = datetime.datetime.today()
        transaction.extra_days = book_trans.extra_days

        transaction.total_fine = book_trans.total_fine

        transaction.total_rent = book_trans.total_rent

        if due_paid:
            transaction.pay_due()

        db.session.add(transaction)
        db.session.commit()

    def pay_due(self):
        self.status = TransactionStatus.PAID

from app.books.models import BookStock, StockStatus