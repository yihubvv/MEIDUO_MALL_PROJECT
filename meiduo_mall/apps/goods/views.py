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
        'default_image_url':sku.default_image.url
      })

    total_num = paginator.num_pages

    return JsonResponse({'code':0,'errmsg':'OK', 'breadcrumb':breadcrumb,'list':sku_dict,'count':total_num})