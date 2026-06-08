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
    """
    Gets objects and render the page.
    Args:
        request:
            request from frontend.
    Returns:
        render(request, 'index.html', context):
          render the index page with these item info.
    """
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
import meiduo_mall.errors as error
import utils.responses.general_response as response 
class ListView(View):
  """
  Gets objects and render the page.
  Args:
      request:
          request from frontend.
  Returns:
      render(request, 'index.html', context):
        render the index page with these item info.
  """
  def get(self, request, category_id):
    ordering = request.GET.get('ordering')
    page_size = request.GET.get('page_size')
    page = request.GET.get('page')
    try:
      category = GoodsCategory.objects.get(id=category_id)
    except GoodsCategory.DoesNotExist:
      return response.JsonResponseError(errmsg=error.INSUFFICIENT_DATA)
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

    return JsonResponse({'code':0,'errmsg':error.NO_ERROR, 'breadcrumb':breadcrumb,'list':sku_dict,'count':total_num})

from haystack.views import SearchView
from django.http import JsonResponse
class SKUSearchView(SearchView):
  """
  Implements elastic search with haystack
  """
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
from apps.contents.detail import normalize_fdfs_urls
class DetailView(View):
  """
  Render the product detail page when user clicked on an image.
  Args:
      request:
          request from frontend.
      sku_id:
        the id of the product.

  Returns:
      render(request,'detail.html',context)
        render the index page with item info.
  """

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
      'desc_detail': normalize_fdfs_urls(sku.spu.desc_detail),
      'desc_pack': normalize_fdfs_urls(sku.spu.desc_pack),
      'desc_service': normalize_fdfs_urls(sku.spu.desc_service),
    }
    return render(request,'detail.html',context)
  
from apps.goods.models import GoodsVisitCount
class CategoryVisitCountView(View):
  def get(self, request, category_id):
    return self.post(request, category_id)

  """
  Keeps in track of the times that an user visits a page.
  Args:
      request:
          request from frontend.
      category_id:
        the id of the category.

  Returns:
      Json response:
        JsonResponse of Ok on success Item does not exist otherwise.
  """

  def post(self, request, category_id):
    try:
      category = GoodsCategory.objects.get(id=category_id)
    except GoodsCategory.DoesNotExist:
      return response.JsonResponseError(errmsg=error.DOES_NOT_EXIST)
    today = date.today()
    try:
      gvc = GoodsVisitCount.objects.get(category=category,date=today)
    except GoodsVisitCount.DoesNotExist:
      GoodsVisitCount.objects.create(category = category, date=today,count = 1)
    else: 
      gvc.count += 1
      gvc.save()

    return response.JsonResponsePass(errmsg=error.NO_ERROR)

class HotGoodsView(View):
  """
  Searches for the top 2 best seller items in a given category.
  Args:
      request:
          request from frontend.
      category_id:
          a given category
  Returns:
      Jsonresponse:
        A jsonresponse with a desired result.
  """
  def get(self,request:HttpRequest, category_id):
    skus = SKU.objects.filter(category_id=category_id, is_launched=True).order_by('-sales')[:2]
    sku_list = []
    for sku in skus:
      sku_list.append({
               'id':sku.id,
               'default_image_url':sku.default_image.url,
               'name':sku.name,
               'price':sku.price
           })
    return JsonResponse({'code':0, 'errmsg':error.NO_ERROR, 'hot_skus':sku_list})
