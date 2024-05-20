from celery import shared_task

@shared_task
def notify(form_id):
    print('task executed')