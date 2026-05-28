import os

from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meiduo_mall.settings')

app = Celery('celery_tasks')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('celery_tasks.config')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks(['celery_tasks.sms','celery_tasks.email'])


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')