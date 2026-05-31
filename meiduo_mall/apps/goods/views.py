from django.shortcuts import render
from django.http import HttpRequest
# Create your views here.
from django.views import View
from utils import models
from utils.models import BaseModel
from utils.goods import get_breadcrumb, get_goods_specs, get_categories
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
  
from apps.goods.models import GoodsCategory
from django.http import JsonResponse
from utils.goods import get_breadcrumb
from apps.goods.models import SKU
from django.core.paginator import Paginator
class ListView(View):
  def get(self, request, category_id):
    ordering = request.GET.get('ordering')
    page_size = request.GET.get('page_size')
    page = request.GET.get('page')
    try:
      category = GoodsCategory.objects.get(id=category_id)
    except GoodsCategory.DoesNotExist:
      return JsonResponse({'code':400, 'errmsg':'incomplete data'})
    breadcrumb = get_breadcrumb(category)
    skus = SKU.objects.filter(category=category,is_launched=True).order_by(ordering)
    
    paginator = Paginator(skus,page_size)
    page_skus = paginator.page(page)

    sku_dict = []
    for sku in page_skus.object_list:
      sku_dict.append({
        'id':sku.id,
        'name':sku.name,
        'price':sku.price,
        'comments': sku.comments,
        'default_image_url':sku.default_image.url
      })

    total_num = paginator.num_pages

    return JsonResponse({'code':0,'errmsg':'OK', 'breadcrumb':breadcrumb,'list':sku_dict,'count':total_num})

from haystack.views import SearchView
from django.http import JsonResponse
class SKUSearchView(SearchView):

  def __call__(self, request):
    try:
      self.results_per_page = int(request.GET.get('page_size', self.results_per_page))
    except (TypeError, ValueError):
      pass

    return super().__call__(request)

  def create_response(self):
    context = self.get_context()
    sku_list = []
    page = context['page']
    paginator = context['paginator']
    for item in page.object_list:
      sku = item.object
      if sku is None:
        continue
      sku_list.append({
        'id': sku.id,
        'name': sku.name,
        'price': sku.price,
        'comments': sku.comments,
        'default_image_url': sku.default_image.url if sku.default_image else '',
      })
    return JsonResponse({
      'count': paginator.count,
      'list': sku_list,
      'page': page.number,
      'page_size': self.results_per_page,
      'total_page': paginator.num_pages,
      'searchkey': context.get('query'),
    })
from datetime import date
from utils.goods import get_goods_specs, get_categories,get_breadcrumb
class DetailView(View):
  def get(self,request, sku_id):
    try:
      sku=SKU.objects.get(id=sku_id)
    except SKU.DoesNotExist:
      pass
    categories = get_categories()
    breadcrumb = get_breadcrumb(sku.category)
    goods_specs = get_goods_specs(sku)
    context = {
      'categories': categories,
      'breadcrumb': breadcrumb,
      'sku': sku,
      'specs': goods_specs,
    }
    return render(request,'detail.html',context)
  
from apps.goods.models import GoodsVisitCount
class CategoryVisitCountView(View):
  def get(self, request, category_id):
    return self.post(request, category_id)

  def post(self, request, category_id):
    try:
      category = GoodsCategory.objects.get(id=category_id)
    except GoodsCategory.DoesNotExist:
      return JsonResponse({'code':400,'errmsg':'No such category.'})
    today = date.today()
    try:
      gvc = GoodsVisitCount.objects.get(category=category,date=today)
    except GoodsVisitCount.DoesNotExist:
      GoodsVisitCount.objects.create(category = category, date=today,count = 1)
    else: 
      gvc.count += 1
      gvc.save()

    return JsonResponse({'code':0, 'errmsg': 'OK'})
