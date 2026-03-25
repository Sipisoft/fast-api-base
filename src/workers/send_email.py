from workers.base_worker import BaseWorker


class SendEmailWorker(BaseWorker):
    

    def perform(self, options: dict):
        self.task = options
        super().perform(options)