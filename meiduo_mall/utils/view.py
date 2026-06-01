from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse

class LoginRequiredJsonMixin(LoginRequiredMixin):
  def handle_no_permission(self):
    return JsonResponse({'code':400,'errmsg':'Not Logged in!'}, status=401)
