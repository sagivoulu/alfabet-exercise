from datetime import datetime
from typing import Optional, Tuple

from pydantic import PositiveFloat
import structlog
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError

# from dal.external_models import DalTransactionDirection, DalTransaction, DalTransactionStatus
from dal import external_models as dal_models
from dal.sqlalchemy.configuration import get_sqlalchemy_engine
from dal.sqlalchemy import models as sqlalchemy_models


logger = structlog.get_logger()


class Dal:

    __session_maker = None
    __session = None

    def _get_session(self) -> Session:
        if not self.__session_maker and not self.__session:
            raise ValueError('The session maker is missing. are you sure you initiated the database connection?')

        if self.__session:
            return self.__session

        self.__session = self.__session_maker()

        return self.__session

    def initiate_connection(self, connection_string: str):
        logger.debug('Creating sql alchemy engine')
        engine = get_sqlalchemy_engine(connection_string)
        logger.debug('creating all model schemas in database')
        sqlalchemy_models.Base.metadata.create_all(engine)
        logger.debug('model schemas created in database')

        self.__session_maker = sessionmaker(bind=engine)

    def transfer_money(self, src_account_id: str, dst_account_id: str, amount: float) -> Tuple[bool, str]:

        # TODO: If the transaction failed because there was a db change,
        #  run it again after waiting a random amount of time. after X attempts return a failure

        with self._get_session() as session:
            transfer_successful = False
            failure_reason = ''
            try:
                # Begin a database transaction
                session.begin()

                # Retrieve the source and destination accounts from the database with row-level locking
                src_account = session.query(sqlalchemy_models.BankAccount).with_for_update().get(src_account_id)
                dst_account = session.query(sqlalchemy_models.BankAccount).with_for_update().get(dst_account_id)

                if src_account is None:
                    raise ValueError(f"Source account with ID {src_account_id} does not exist")
                if dst_account is None:
                    raise ValueError(f"Destination account with ID {dst_account_id} does not exist")
                if amount > 0 and src_account.balance < amount:
                    raise ValueError("Insufficient funds in the source account")
                if amount < 0 and dst_account.balance < amount * -1:
                    raise ValueError("Insufficient funds in the destination account")

                # Perform the transaction
                src_account.balance -= amount
                dst_account.balance += amount

                # Commit the changes to the database
                session.commit()

                transfer_successful = True

                logger.debug(f"Transaction completed: {amount} units transferred "
                             f"from account {src_account_id} to account {dst_account_id}")
                logger.debug(f"Source account balance: {src_account.balance}")
                logger.debug(f"Destination account balance: {dst_account.balance}")

            except IntegrityError as e:
                # Rollback the transaction in case of any error
                session.rollback()
                logger.exception("An error occurred during the transaction:", error=str(e))

                failure_reason = f'Internal error: {str(e)}'
            except ValueError as e:
                session.rollback()
                logger.exception("An error occurred during the transaction:", error=str(e))

                failure_reason = f'{str(e)}'
            except Exception as e:
                session.rollback()
                logger.exception("An error occurred during the transaction:", error=str(e))

                failure_reason = f'Internal unexpected error: {str(e)}'

            return transfer_successful, failure_reason

    def create_transaction(
            self,
            src_account_id: str,
            dst_account_id: str,
            timestamp: datetime,
            amount: PositiveFloat,
            direction: dal_models.DalTransactionDirection,
            status: dal_models.DalTransactionStatus,
            reason: Optional[str] = None) -> dal_models.DalTransaction:
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