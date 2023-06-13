from datetime import datetime

from sqlalchemy import ForeignKey, CheckConstraint
from sqlalchemy import String, Float, DateTime
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


class Base(DeclarativeBase):
    pass


class BankAccount(Base):
    __tablename__ = "bank_account"
    id: Mapped[int] = mapped_column(primary_key=True)
    owner_name: Mapped[str] = mapped_column(String)
    balance: Mapped[float] = mapped_column(Float)

    __table_args__ = (
        CheckConstraint(balance >= 0, name='check_balance_not_negative'),
        {})

    def __repr__(self) -> str:
        return f"BankAccount(id={self.id!r}, owner_name={self.owner_name!r}, balance={self.balance!r})"


class Transaction(Base):
    __tablename__ = "transaction"
    id: Mapped[int] = mapped_column(primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime)
    src_account_id: Mapped[int] = mapped_column(ForeignKey("bank_account.id"))
    dst_account_id: Mapped[int] = mapped_column(ForeignKey("bank_account.id"))
    amount: Mapped[float] = mapped_column(Float)
    direction: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String)
    reason: Mapped[str] = mapped_column(String)

    def __repr__(self) -> str:
        return f"Transaction(id={self.id!r}, " \
               f"src_account_id={self.src_account_id!r}, " \
               f"dst_account_id={self.dst_account_id!r}, " \
               f"direction={self.direction!r}, " \
               f"amount={self.status!r}, " \
               f"status={self.status!r}, " \
               f"reason={self.reason!r})"
