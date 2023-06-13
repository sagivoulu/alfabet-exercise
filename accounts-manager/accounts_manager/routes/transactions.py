from datetime import datetime
from typing import Iterable

from fastapi import APIRouter, Query
from structlog import get_logger

from api_models.transations import TransactionRequest, Transaction, TransactionDirection
from dal.dal import Dal
from dal.external_models import DalTransactionDirection, DalTransactionStatus, DalTransaction

logger = get_logger()


def get_router(dal: Dal) -> APIRouter:
    """Generated a bunch of example routes on a router, and returns the resulting router"""
    router = APIRouter()

    @router.post('/api/v1/transaction', response_model=Transaction)
    def post_transaction(transaction_request: TransactionRequest) -> DalTransaction:

        # If the transaction from account A to B of 100 units is with the direction "debit",
        # we subtract 100 units from A and add 100 units to B.
        # But if the direction is "credit" we have to do the opposite, so we will invert the amount being transferred.
        normalized_amount = transaction_request.amount
        if transaction_request.direction == TransactionDirection.credit:
            normalized_amount = normalized_amount * -1
        is_successful, reason = dal.transfer_money(
            src_account_id=transaction_request.src_account_id,
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

        return dal_transaction

    @router.get('/api/v1/transactions', response_model=Iterable[Transaction])
    def get_transactions(start_timestamp: datetime,
                         end_timestamp: datetime,
                         page: int = 0,
                         limit: int = 100) -> Iterable[DalTransaction]:
        dal_transactions = dal.get_paginated_transactions(start_timestamp=start_timestamp,
                                                          end_timestamp=end_timestamp,
                                                          page=page,
                                                          limit=limit)
        return dal_transactions

    return router
