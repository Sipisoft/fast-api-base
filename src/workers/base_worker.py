from celery import celery_app
class BaseWorker:
    
    @celery_app.task
    def perform(self, options: dict):
        self.task = options

        