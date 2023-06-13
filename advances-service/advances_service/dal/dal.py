from datetime import datetime, timedelta
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

    def create_advance(self, dst_account_id: str, amount: float,
                       status: dal_models.DalAdvanceStatus, start_timestamp: datetime) -> dal_models.DalAdvance:
        with self._get_session() as session:
            advance = sqlalchemy_models.Advance(
                dst_account_id=dst_account_id,
                amount=amount,
                status=status.value,
                start_timestamp=start_timestamp
            )
            session.add(advance)
            session.commit()

            dal_advance = dal_models.DalAdvance.from_orm(advance)

        return dal_advance

    def update_advance_status(self, advance_id: str, status: dal_models.DalAdvanceStatus) -> dal_models.DalAdvance:
        with self._get_session() as session:
            # Retrieve the source and destination accounts from the database with row-level locking
            advance = session.query(sqlalchemy_models.Advance).with_for_update().get(advance_id)

            advance.status = status.value

            # Commit the changes to the database
            session.commit()

            new_advance = dal_models.DalAdvance.from_orm(advance)

            return new_advance

    def create_advance_payments(self, advance: dal_models.DalAdvance,
                                number_of_payments: int = 12) -> Iterable[dal_models.DalAdvancePayment]:
        payment_amount = advance.amount / number_of_payments
        payment_due_date = advance.start_timestamp

        with self._get_session() as session:
            payments = []
            for payment_number in range(number_of_payments):

                # TODO: Remove magic number
                payment_due_date = payment_due_date + timedelta(days=7)
                payment = sqlalchemy_models.AdvancePayment(
                    advance_id=advance.advance_id,
                    payment_number=payment_number,
                    amount=payment_amount,
                    due_at=payment_due_date,
                    status=dal_models.DalAdvancePaymentStatus.not_due_yet.value
                )
                payments.append(payment)
            session.add_all(payments)
            session.commit()

            dal_payments = [dal_models.DalAdvancePayment.from_orm(payment) for payment in payments]

        return dal_payments
