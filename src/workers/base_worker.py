from celery_app import celery_app
class BaseWorker:
    
    @celery_app.task
    def perform(self, options: dict):
        self.task = options

        