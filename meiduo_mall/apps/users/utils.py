from itsdangerous import URLSafeTimedSerializer as Serializer
from django.conf import settings


def generic_email_verify_token(user_id):
    """
    This function encodes our data with itsdangerous lib so we can pass this data to frontend securely.
    Args:
        request:
            user_id.
    Returns:
        data:
        signed/encrypted data.
    """
    s = Serializer(secret_key=settings.SECRET_KEY)
    data = s.dumps({'user_id': user_id})
    return data

def check_token(token):
    """
    This function decodes our data with itsdangerous lib so we can erify if this data has been tampered with.
    Args:
        token:
            token form frontend.
    Returns:
        data:
        decoded data.
    """
    s = Serializer(secret_key=settings.SECRET_KEY)
    try:
      data = s.loads(token, max_age=3600*24)
    except Exception as e:
      return None
    return data.get('user_id')


