from datetime import datetime

from sqlalchemy import ForeignKey, CheckConstraint, PrimaryKeyConstraint
from sqlalchemy import String, Float, DateTime, Integer
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


class Base(DeclarativeBase):
    pass


class Advance(Base):
    __tablename__ = "advance"
    id: Mapped[int] = mapped_column(primary_key=True)
    dst_account_id: Mapped[int] = mapped_column(String)
    amount: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String)
    start_timestamp: Mapped[datetime] = mapped_column(DateTime)

    __table_args__ = (
        CheckConstraint(amount > 0, name='amount_not_negative'),
        {})

    def __repr__(self) -> str:
        return f"Advance(id={self.id!r}, " \
               f"amount={self.amount!r}, " \
               f"dst_account_id={self.dst_account_id!r}, " \
               f"status={self.status!r})"


class AdvancePayment(Base):
    __tablename__ = "advance_payment"
    advance_id: Mapped[int] = mapped_column(ForeignKey("advance.id"))
    payment_number: Mapped[int] = mapped_column(Integer)
    due_at: Mapped[datetime] = mapped_column(DateTime)
    amount: Mapped[Float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String)

    __table_args__ = (
        PrimaryKeyConstraint(advance_id, payment_number),
        {})

    def __repr__(self) -> str:
        return f"AdvancePayment(advance_id={self.advance_id!r}, " \
               f"payment_number={self.payment_number!r}, " \
               f"due_at={self.due_at!r}, " \
               f"amount={self.amount!r}, " \
               f"status={self.status!r})"
