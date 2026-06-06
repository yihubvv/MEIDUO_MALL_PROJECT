from django.core.mail import send_mail
from celery_tasks.main import app

@app.task
def celery_send_email(subject, message, from_email, recipient_list, html_message):
  """
      Uses celery to handle sending email.
      Args:
          subject:
            Email subject.
          message:
            Email message.
          from_email:
            Sender.
          recipient_list:
            Send email to recipients.
          html_message:
            Sends html message.(imgs .etc)
      Returns:
          Returns 0 on success.
  """
  send_mail(
    subject=subject,
    message=message,
    from_email=from_email,
    recipient_list=recipient_list,
    html_message=html_message)