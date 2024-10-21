import enum
import datetime
import sqlalchemy
from sqlalchemy.ext.hybrid import hybrid_property
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
    transaction: Mapped["Transaction"] = relationship(
        back_populates="book_transaction", 
        lazy="select",
        cascade="all, delete-orphan"
    )

    stock: Mapped["BookStock"] = relationship(back_populates="transactions", lazy="select")
    member: Mapped["Member"] = relationship(back_populates="transactions", lazy="select")

    def __repr__(self):
        return f'<BookTransaction {self.id}>'
    
    @staticmethod
    def issue_book(stock_id: int, member_email: str):
        stock: BookStock = db.session.get(BookStock, stock_id)
        if stock.status == StockStatus.TAKEN:
            return None
        
        member: Member = db.session.execute(
            db.select(Member).filter_by(email=member_email)
        ).scalar_one()
        if not member.is_allowed_to_rent_book:
            return None

        book_transaction: BookTransaction = BookTransaction(
            stock = stock,
            member_id = member.id
        )
        book_transaction.set_issue_and_due_date(datetime.date.today())
        book_transaction.stock.status = StockStatus.TAKEN
        db.session.add(book_transaction)
        return book_transaction
    
    def set_issue_and_due_date(self, issue_date: datetime.date):
        self.issue_date = issue_date
        self.due_date = issue_date + datetime.timedelta(days=Config.LOAN_PERIOD)
    
    @hybrid_property
    def is_returned(self):
        return self.transaction is not None
    
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
            extra = datetime.date.today() - self.due_date
            if extra.days < 0:
                return 0
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
            transaction: Transaction = Transaction.create_transaction(self, due_paid)
            if not transaction:
                return False
            self.stock.status = StockStatus.AVAILABLE
            return True
        return False
    
    def return_book_and_due_paid(self):
        self.return_book(due_paid=True)

    @property
    def is_due_paid(self):
        if not self.is_returned:
            return None
        return self.transaction.status == TransactionStatus.PAID
    
    def pay_due(self):
        if not self.is_returned:
            return False
        if not self.is_due_paid:
            self.transaction.pay_due()
            return True

class TransactionStatus(enum.Enum):
    PAID = "paid"
    DUE = "due"

class Transaction(db.Model):
    __tablename__ = "transaction"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    book_trans_id: Mapped[int] = mapped_column(ForeignKey("book_transaction.id", ondelete="CASCADE"))
    book_transaction: Mapped["BookTransaction"] = relationship(
        back_populates="transaction", lazy="select"
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
        
        if book_trans.transaction:
            return
        
        transaction = Transaction(
            book_trans_id = book_trans.id,
            return_date = datetime.date.today(),
            extra_days = book_trans.extra_days,
            total_fine = book_trans.total_fine,
            total_rent = book_trans.total_rent
        )

        if due_paid:
            transaction.pay_due()

        db.session.add(transaction)
        return transaction

    def pay_due(self):
        self.status = TransactionStatus.PAID

from app.books.models import BookStock, StockStatus