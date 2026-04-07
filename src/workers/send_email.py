from src.workers.base_worker import BaseWorker
from src.workers.tasks import send_password_reset_email_task

class SendEmailWorker(BaseWorker):
    

    def perform(self, options: dict):
        self.task = options
        super().perform(options)



def trigger_password_reset_email(account, account_type, new_password):
    send_password_reset_email_task.delay(str(account.id), account_type, new_password)