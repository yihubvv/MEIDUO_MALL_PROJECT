from django.shortcuts import render
from django.http import HttpRequest
# Create your views here.
from django.views import View
from utils.goods import get_breadcrumb,get_goods_specs, get_categories
from apps.contents.models import ContentCategory
class IndexView(View):
  def get(self, request:HttpRequest):

    categories = get_categories()
    contents= {}
    content_categories = ContentCategory.objects.all()
    for cat in content_categories:
      contents[cat.key] = cat.content_set.filter(status=True).order_by('sequence')
    
    context = {
      'categories': categories,
      'contents': contents,
    }
    return render(request, 'index.html', context)