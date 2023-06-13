from datetime import datetime
from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, PositiveFloat, Field


class TransactionDirection(str, Enum):
    """
    Every transaction can have one of two different directions.
    debit - money is deducted from the source account & moved to the destination account
    credit - money is added to the source account & deducted from the destination account
    """
    debit = 'debit'
    credit = 'credit'


class TransactionStatus(str, Enum):
    """The state of the transaction. If a transaction has failed it did not occur & no money moved between accounts"""
    successful = 'successful'
    fail = 'fail'


class TransactionRequest(BaseModel):
    """A request to create a new transaction"""

    src_account_id: str
    dst_account_id: str
    amount: PositiveFloat
    direction: TransactionDirection


class Transaction(BaseModel):
    """Money transaction"""
    transaction_id: str = Field(alias="id")
    src_account_id: str
    dst_account_id: str
    timestamp: datetime
    amount: PositiveFloat
    direction: TransactionDirection
    status: TransactionStatus
    reason: Optional[str]

    class Config:
        orm_mode = True


class TransactionsPage(BaseModel):
    items: List[Transaction]
    page: int
    limit: int
    total_items: int
    number_of_pages: int
