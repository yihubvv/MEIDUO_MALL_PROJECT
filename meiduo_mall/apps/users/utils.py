from itsdangerous import URLSafeTimedSerializer as Serializer
from django.conf import settings


def generic_email_verify_token(user_id):
    s = Serializer(secret_key=settings.SECRET_KEY)
    data = s.dumps({'user_id': user_id})
    return data

def check_token(token):
    s = Serializer(secret_key=settings.SECRET_KEY)
    try:
      data = s.loads(token, max_age=3600*24)
    except Exception as e:
      return None
    return data.get('user_id')


