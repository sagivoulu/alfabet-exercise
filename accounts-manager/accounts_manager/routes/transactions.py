from datetime import datetime

from fastapi import APIRouter
from structlog import get_logger

from api_models.transations import TransactionRequest, Transaction, TransactionStatus, TransactionDirection
from dal.dal import Dal
from dal.external_models import DalTransactionDirection, DalTransactionStatus

logger = get_logger()


def get_router(dal: Dal) -> APIRouter:
    """Generated a bunch of example routes on a router, and returns the resulting router"""
    router = APIRouter()

    @router.post('/api/v1/transaction', response_model=Transaction)
    def long_request(transaction_request: TransactionRequest) -> Transaction:
        # TODO: Check the direction & reverse src & dst if needed (or transfer a negative amount)

        # If the transaction from account A to B of 100 units is with the direction "debit",
        # we subtract 100 units from A and add 100 units to B.
        # But if the direction is "credit" we have to do the opposite, so we will invert the amount being transferred.
        normalized_amount = transaction_request.amount
        if transaction_request.direction == TransactionDirection.credit:
            normalized_amount = normalized_amount * -1
        is_successful, reason = dal.transfer_money(src_account_id=transaction_request.src_account_id,
                                            dst_account_id=transaction_request.dst_account_id,
                                            amount=normalized_amount)

        logger.info('Transaction complete', is_successful=is_successful, reason=reason)

        dal_transaction = dal.create_transaction(
            src_account_id=transaction_request.src_account_id,
            dst_account_id=transaction_request.dst_account_id,
            amount=transaction_request.amount,
            direction=DalTransactionDirection(transaction_request.direction.value),
            status=DalTransactionStatus.successful if is_successful else DalTransactionStatus.fail,
            reason=reason,
            timestamp=datetime.now()
        )

        # TODO: Actually perform the transaction
        result = Transaction.from_orm(dal_transaction)
        return result

    return router
