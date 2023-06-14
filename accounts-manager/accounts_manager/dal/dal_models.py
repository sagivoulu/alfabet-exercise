"""
These are models that are exposed out of the dal layer. Internally the DAL layer will use the appropriate models based
on the database & code used to interact with it.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, PositiveFloat, Field


class DalTransactionDirection(str, Enum):
    debit = "debit"
    credit = "credit"


class DalTransactionStatus(str, Enum):
    successful = 'successful'
    fail = 'fail'


class DalTransaction(BaseModel):
    transaction_id: str = Field(alias="id")
    src_account_id: str
    dst_account_id: str
    timestamp: datetime
    amount: PositiveFloat
    direction: DalTransactionDirection
    status: DalTransactionStatus
    reason: Optional[str]

    class Config:
        orm_mode = True
