from django.shortcuts import render

# Create your views here.

from django.views import View
from apps.areas.models import Area
from django.http import JsonResponse
from django.core.cache import cache

class AreaView(View):
  def get(self,request):
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
    return JsonResponse({'code':0,'errmsg':'OK', 'province_list':province_list})

class SubAreaView(View):
  def get(self,request,id):
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

    return JsonResponse({'code':0,'errmsg':'OK', 'sub_data':{'subs':province_list}})

