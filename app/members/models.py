import datetime
from typing import List
from sqlalchemy import (
    Integer,
    String,
    Date
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)
from app.db import db
from config import Config

class Member(db.Model):
    __tablename__ = "member"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(256), unique=True)
    joining_date: Mapped[datetime.date] = mapped_column(Date)

    transactions: Mapped[List["BookTransaction"]] = relationship(
        "BookTransaction", back_populates="member"
    )

    @property
    def no_of_books_currently_rented(self):
        count = 0
        for book in self.transactions:
            if not book.is_returned:
                count += 1
        return count
    
    @property
    def total_dues(self):
        dues = 0
        for book in self.transactions:
            if not book.is_due_paid:
                dues += book.total_rent
        return dues
    
    @property
    def is_allowed_to_rent_book(self):
        return self.no_of_books_currently_rented <= Config.NO_OF_BOOKS_RENTED_AT_A_TIME \
            and self.total_dues < Config.PERMITTED_AMOUNT_OF_DUES
    
    def pay_all_dues(self):
        for book in self.transactions:
            if not book.is_due_paid:
                book.pay_due()
        db.session.commit()

    def __repr__(self):
        return f'<Member {self.email}>'
    
    def validate_email(self, email):
        members = db.session.execute(db.select(Member).filter_by(email=email)).scalars()

        return len(members) == 0 