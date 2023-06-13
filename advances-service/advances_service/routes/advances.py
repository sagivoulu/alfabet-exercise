from datetime import datetime
import math

from fastapi import APIRouter, Query
from structlog import get_logger

from api_models.advances import AdvanceRequest, Advance
from dal.dal import Dal
from dal import external_models as dal_models

logger = get_logger()


def get_router(dal: Dal) -> APIRouter:
    """Generated a bunch of example routes on a router, and returns the resulting router"""
    router = APIRouter()

    @router.post('/api/v1/advance', response_model=Advance)
    def post_advance(advance_request: AdvanceRequest) -> Advance:
        # First we register the advance but keep it in a pending state, & only after the money transfer is complete we
        # will change the state
        dal_advance = dal.create_advance(dst_account_id=advance_request.dst_account_id,
                                         amount=advance_request.amount,
                                         status=dal_models.DalAdvanceStatus.pending_transaction,
                                         start_timestamp=datetime.now())

        # TODO: Call the accounts-manager service to create a transaction, & make sure it completes successfully

        dal_advance = dal.update_advance_status(advance_id=dal_advance.advance_id,
                                                status=dal_models.DalAdvanceStatus.active)

        _ = dal.create_advance_payments(advance=dal_advance)

        advance = Advance.from_orm(dal_advance)

        return advance

    return router
