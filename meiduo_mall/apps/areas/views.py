from django.shortcuts import render

# Create your views here.

from django.views import View
from apps.areas.models import Area
from django.http import JsonResponse
from django.core.cache import cache
import meiduo_mall.errors as error
class AreaView(View):
  def get(self,request):
    """
    This function checks if area data has been stored correctly and cache the data if not already do so.
    Args:
        request:
            request from frontend.
    Returns:
        response:
          response with a message of success or error and a list of province.
    """
    province_list = cache.get('province')
    if province_list is None:
      province_list = []
      provinces = Area.objects.filter(parent=None)
      for province in provinces:
         province_list.append({
           'id':province.id,
           'name':province.name
         })
      cache.set('province',province_list,24*3600)
    return JsonResponse({'code':0,'errmsg':error.NO_ERROR, 'province_list':province_list})

class SubAreaView(View):

  def get(self,request,id):
    """
    This function checks if sub-area data has been stored correctly and cache the data if not already do so.
    Args:
        request:
            request from frontend.
        id:
          the id of their parent city.
    Returns:
        response:
          response with a message of success or error and a list of sub-areas.
    """
    province_list = cache.get('city:%s'%id)
    if province_list is None:
      provinces = Area.objects.filter(parent_id=id)
      province_list = []
      for province in provinces:
         province_list.append({
           'id':province.id,
           'name':province.name
         })
      cache.set('city:%s'%id,province_list,24*3600)

    return JsonResponse({'code':0,'errmsg':error.NO_ERROR, 'sub_data':{'subs':province_list}})

