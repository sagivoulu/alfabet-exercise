from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, PositiveFloat


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

    src_account_id: str
    dst_account_id: str
    datetime: datetime
    amount: PositiveFloat
    direction: TransactionDirection
    status: TransactionStatus
    reason: Optional[str]
