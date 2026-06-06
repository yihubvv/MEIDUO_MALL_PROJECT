from libs.yuntongxun.sms import CCP
from celery_tasks.main import app

@app.task
def celery_send_sms_code(mobile,code):
  """
      Uses celery to handle sending SMS message.
      Args:
          mobile:
            User provided mobile.
          code:
            System generated code.
      Returns:
          Returns 0 on success, -1 otherwise.
  """
  CCP().send_template_sms(mobile,[code,5],1)