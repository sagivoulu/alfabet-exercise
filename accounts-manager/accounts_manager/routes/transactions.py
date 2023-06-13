from datetime import datetime

from fastapi import APIRouter
from structlog import get_logger

from api_models.transations import TransactionRequest, Transaction, TransactionStatus

logger = get_logger()


def get_router() -> APIRouter:
    """Generated a bunch of example routes on a router, and returns the resulting router"""
    router = APIRouter()

    @router.post('/api/v1/transaction')
    def long_request(transaction_request: TransactionRequest) -> Transaction:
        # TODO: Actually perform the transaction
        result = Transaction(
            src_account_id=transaction_request.src_account_id,
            dst_account_id=transaction_request.dst_account_id,
            direction=transaction_request.direction,
            amount=transaction_request.amount,
            status=TransactionStatus.successful,
            datetime=datetime.now()
        )
        return result

    return router
