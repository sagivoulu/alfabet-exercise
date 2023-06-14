from datetime import datetime
import math

from fastapi import APIRouter
from structlog import get_logger

from api_models.transations import TransactionRequest, Transaction, TransactionDirection, TransactionsPage
from dal.dal import Dal
from dal.dal_models import DalTransactionDirection, DalTransactionStatus, DalTransaction

logger = get_logger()


def get_router(dal: Dal) -> APIRouter:
    """Generated a bunch of example routes on a router, and returns the resulting router"""
    router = APIRouter()

    @router.post('/api/v1/transaction', response_model=Transaction)
    def post_transaction(transaction_request: TransactionRequest) -> DalTransaction:
        """
        Creates a new transfer & attempts to transfer the funds between the specified bank accounts.
        :param transaction_request: The details of the transfer request (the bank accounts, amount etc..)
        :return: The resulting Transaction, which includes the status specifying if
                 the transaction was successful or not
        """

        # If the transaction from account A to B of 100 units is with the direction "debit",
        # we subtract 100 units from A and add 100 units to B.
        # But if the direction is "credit" we have to do the opposite, so we will invert the amount being transferred.
        normalized_amount = transaction_request.amount
        if transaction_request.direction == TransactionDirection.credit:
            normalized_amount = normalized_amount * -1

        failure_reason = None
        try:
            dal.transfer_money(
                src_account_id=transaction_request.src_account_id,
                dst_account_id=transaction_request.dst_account_id,
                amount=normalized_amount)
            logger.debug('Money transfer was successful')
        # A ValueError is raised when there is a problem with the given parameters.
        # for example: invalid accounts, not enough funds or invalid transfer amount
        except ValueError as e:
            failure_reason = f'Transfer of funds denied. reason: {e}'
            logger.warning(failure_reason)
        except Exception as e:
            failure_reason = f'Money transfer failed due to an unexpected error: {e}'
            logger.exception(failure_reason)

        transfer_successful = failure_reason is None
        logger.info('Transaction complete', is_successful=transfer_successful, reason=failure_reason)

        dal_transaction = dal.create_transaction(
            src_account_id=transaction_request.src_account_id,
            dst_account_id=transaction_request.dst_account_id,
            amount=transaction_request.amount,
            direction=DalTransactionDirection(transaction_request.direction.value),
            status=DalTransactionStatus.successful if transfer_successful else DalTransactionStatus.fail,
            reason=failure_reason,
            timestamp=datetime.now()
        )

        return dal_transaction

    @router.get('/api/v1/transactions', response_model=TransactionsPage)
    def get_transactions(start_timestamp: datetime,
                         end_timestamp: datetime,
                         page: int = 0,
                         limit: int = 100) -> TransactionsPage:
        dal_transactions, total_count = dal.get_paginated_transactions(start_timestamp=start_timestamp,
                                                                       end_timestamp=end_timestamp,
                                                                       page=page,
                                                                       limit=limit)
        transactions = [Transaction.from_orm(dal_transaction) for dal_transaction in dal_transactions]
        transactions_page = TransactionsPage(
            items=transactions,
            page=page,
            limit=limit,
            total_items=total_count,
            number_of_pages=math.ceil(total_count / limit)
        )

        return transactions_page

    return router
