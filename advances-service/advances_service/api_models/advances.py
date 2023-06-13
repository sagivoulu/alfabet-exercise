from datetime import datetime
from enum import Enum

from pydantic import BaseModel, PositiveFloat


class AdvanceStatus(str, Enum):
    """The state of the advance payment"""
    active = 'active'
    paid = 'paid'
    overdue = 'overdue'


class AdvanceRequest(BaseModel):
    """A request to get an advance payment"""

    dst_account_id: str
    amount: PositiveFloat


class Advance(BaseModel):
    """Money advance"""
    advance_id: str
    dst_account_id: str
    amount: PositiveFloat
    start_timestamp: datetime
    status: AdvanceStatus

    class Config:
        orm_mode = True
