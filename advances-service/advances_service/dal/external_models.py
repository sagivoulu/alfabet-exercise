"""
These are models that are exposed out of the dal layer. Internally the DAL layer will use the appropriate models based
on the database & code used to interact with it.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, PositiveFloat, Field, NonNegativeInt


class DalAdvanceStatus(str, Enum):
    pending_transaction = 'pending_transaction'
    active = 'active'
    paid = 'paid'
    overdue = 'overdue'


class DalAdvance(BaseModel):
    advance_id: str = Field(alias="id")
    dst_account_id: str
    amount: PositiveFloat
    start_timestamp: datetime
    status: DalAdvanceStatus

    class Config:
        orm_mode = True


class DalAdvancePaymentStatus(str, Enum):
    not_due_yet = "not_due_yet"
    pending_processing = "pending_processing"
    paid = "paid"
    failed = "failed"


class DalAdvancePayment(BaseModel):
    advance_id: str
    payment_number: NonNegativeInt
    amount: PositiveFloat
    due_at: datetime
    status: DalAdvancePaymentStatus

    class Config:
        orm_mode = True
