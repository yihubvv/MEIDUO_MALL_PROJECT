from itsdangerous import URLSafeTimedSerializer as Serializer
from meiduo_mall import settings
from itsdangerous import BadData, BadTimeSignature, SignatureExpired
def generic_open_id(openid):
  s = Serializer(settings.SECRET_KEY)
  openid=s.dumps({'openid':openid})
  return openid

def decode_open_id(openid):
  s = Serializer(settings.SECRET_KEY)
  try:
    result = s.loads(openid, max_age=3600)
  except Exception:
    return None
  else:
    return result.get('openid')
