from datetime import datetime
from typing import Optional, Tuple, Iterable

from pydantic import PositiveFloat
import structlog
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_

from dal import external_models as dal_models
from dal.sqlalchemy.configuration import get_sqlalchemy_engine
from dal.sqlalchemy import models as sqlalchemy_models


logger = structlog.get_logger()


class Dal:

    __session_maker = None
    __session = None

    def _get_session(self) -> Session:
        """
        Generates a session object, needed to interact with the database
        :return: Session instance
        """
        if not self.__session_maker and not self.__session:
            raise ValueError('The session maker is missing. are you sure you initiated the database connection?')

        if self.__session:
            return self.__session

        self.__session = self.__session_maker()

        return self.__session

    def initiate_connection(self, connection_string: str) -> None:
        """
        Setup all required connections to the database. This function must be called at least once before using the db
        :param connection_string: The connection string to the databse we are connecting to.
            The format is SQLAlchemy format
        :return: None
        """

        logger.debug('Creating sql alchemy engine')
        engine = get_sqlalchemy_engine(connection_string)
        logger.debug('creating all model schemas in database')
        sqlalchemy_models.Base.metadata.create_all(engine)
        logger.debug('model schemas created in database')

        self.__session_maker = sessionmaker(bind=engine)

    def transfer_money(self, src_account_id: str, dst_account_id: str, amount: float) -> None:
        """
        Attempts to transfer money between the given bank accounts, & throws an error if the transfer failed.
        Note: this function does not create a Transaction record, it has to be created separately
        :param src_account_id: The ID of the account to take the funds from
        :param dst_account_id: The ID of the account to grant the funds to
        :param amount: The amount of funds to transfer (can be negative value)
        :return: None
        """

        # TODO: If the transaction failed because there was a db change,
        #  run it again after waiting a random amount of time. after X attempts return a failure

        with self._get_session() as session:
            # Begin a database transaction
            session.begin()

            # Retrieve the source and destination accounts from the database with row-level locking
            src_account = session.query(sqlalchemy_models.BankAccount).with_for_update().get(src_account_id)
            dst_account = session.query(sqlalchemy_models.BankAccount).with_for_update().get(dst_account_id)

            # TODO: Raise custom exceptions for known errors such as insufficient funds
            if src_account is None:
                raise ValueError(f"Source account with ID {src_account_id} does not exist")
            if dst_account is None:
                raise ValueError(f"Destination account with ID {dst_account_id} does not exist")
            if src_account_id == dst_account_id:
                raise ValueError(f"Source and destination accounts must be different accounts")
            if amount > 0 and src_account.balance < amount:
                raise ValueError("Insufficient funds in the source account")
            if amount < 0 and dst_account.balance < amount * -1:
                raise ValueError("Insufficient funds in the destination account")

            # Perform the transaction
            src_account.balance -= amount
            dst_account.balance += amount

            # Commit the changes to the database
            session.commit()

            logger.debug(f"Transaction completed: {amount} units transferred "
                         f"from account {src_account_id} to account {dst_account_id}")
            logger.debug(f"Source account balance: {src_account.balance}")
            logger.debug(f"Destination account balance: {dst_account.balance}")

    def create_transaction(
            self,
            src_account_id: str,
            dst_account_id: str,
            timestamp: datetime,
            amount: PositiveFloat,
            direction: dal_models.DalTransactionDirection,
            status: dal_models.DalTransactionStatus,
            reason: Optional[str] = None) -> dal_models.DalTransaction:
        """
        Creates a Transaction record in the database & returns it.
        Note: This function does not transfer the funds, this has to be done separately.

        :param src_account_id: The source account id of the transaction
        :param dst_account_id: The destination account id of the transaction
        :param timestamp: The timestamp of when the transaction took place
        :param amount: The amount (positive value) transferred
        :param direction: The direction of the money transfer
            (See documentation of DalTransactionDirection enum for more detailed explanation)
        :param status: The state of the transfer, basically if it was successful or not
        :param reason: The reason why the transfer failed. needed only if the transfer failed
        :return: The created Transaction record
        """
        
        with self._get_session() as session:
            transaction = sqlalchemy_models.Transaction(
                src_account_id=src_account_id,
                dst_account_id=dst_account_id,
                timestamp=timestamp,
                amount=amount,
                direction=direction.value,
                status=status.value,
                reason=reason if reason else ""
            )
            session.add(transaction)
            session.commit()

            dal_transaction = dal_models.DalTransaction.from_orm(transaction)

        return dal_transaction

    def get_paginated_transactions(self, start_timestamp: datetime,
                                   end_timestamp: datetime,
                                   page: int = 0,
                                   limit: int = 100) -> Tuple[Iterable[dal_models.DalTransaction], int]:
        """
        Searches for all transaction matching the given parameters, & returns them within the specified pagination
        :param start_timestamp: The earliest timestamp of transaction to include.
            Transactions can happen exactly at this time or later.
        :param end_timestamp: The latest timestamp of transaction to include.
            Only transaction that happened before this timestamp are included.
        :param page: The number of the paged results to return (first page is 0)
        :param limit: The maximum amount of elements to show in every page
        :return: (Transactions, number_of_transactions) A tuple containing:
            * The Iterable of all the matching transactions in the page
            * The total number of transactions in every page (used to know how many more pages are there)
        """

        start_slice = page * limit
        end_slice = start_slice + limit
        with self._get_session() as session:
            # A query that returns all transactions within the given time rang
            all_matching_transactions_query = session.query(sqlalchemy_models.Transaction)\
                .filter(and_(sqlalchemy_models.Transaction.timestamp >= start_timestamp,
                             sqlalchemy_models.Transaction.timestamp < end_timestamp))

            # Get all matching transactions within the desired page
            all_transactions = all_matching_transactions_query\
                .order_by(sqlalchemy_models.Transaction.timestamp).slice(start=start_slice, stop=end_slice).all()

            # Count the total number of matching transactions without pagination
            total_amount_of_transactions = all_matching_transactions_query.count()
            return all_transactions, total_amount_of_transactions
