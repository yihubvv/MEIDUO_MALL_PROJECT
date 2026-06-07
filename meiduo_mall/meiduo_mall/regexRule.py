import re
PHONE_RE = re.compile(r'^(?:\d{10}|1\d{10})$')
EMAIL_RE = re.compile(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$')
RAW_USERNAME_RE = r'[a-zA-Z_-]{5,20}'
RAW_PHONE_RE = r'^\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}$'
RAW_EMAIL_RE= r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'