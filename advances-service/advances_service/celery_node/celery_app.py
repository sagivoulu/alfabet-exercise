from celery.app import Celery

from settings import Settings

settings = Settings()

celery_app = Celery('advance_service_node', broker=settings.redis_url, backend=settings.redis_url)


@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(60, find_due_advance_payments.s(), name='find_due_advance_payments every 60 seconds')


@celery_app.task
def find_due_advance_payments():
    # TODO: Get all advance payments where their due date has passed & are still marked as not_due_yet
    #           (order by advance & payment number)
    #       for each of these payments
    #           call the process_due_payment task on it & don't wait for the result
    #           change the payments status to pending_processing
    pass


@celery_app.task
def process_due_payment(advance_id: str, payment_number: int):
    # TODO: make sure that the payment is still in pending_processing status, otherwise don't continue the func
    #       Deduct the payment from the account via the accounts-manager API
    #       update the payment status to paid / failed depending on if the deduction worked

    # TODO: If the deduction failed, create another payment in the same time as the next payment.
    #       If there is no next payment, set the next payment to a week from this payment
    pass
