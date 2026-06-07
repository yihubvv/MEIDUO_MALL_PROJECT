from django.template import loader
from meiduo_mall import settings
import os
from utils.goods import get_categories
from apps.contents.models import ContentCategory
import time

def generic_meiduo_index():
    print('----------%s----------------------' % time.ctime())
    categories = get_categories()
    contents = {}
    content_categories = ContentCategory.objects.all()
    for cat in content_categories:
        contents[cat.key] = cat.content_set.filter(status=True).order_by('sequence')

    context = {
        'categories': categories,
        'contents': contents,
    }
    index_template = loader.get_template('index.html')
    index_html_data = index_template.render(context)

    file_path = os.path.join(os.path.dirname(settings.BASE_DIR), 'front_end_pc', 'index.html')
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(index_html_data)

    return index_html_data


def generic_detail_htmls():
    from apps.goods.models import SKU
    from apps.contents.detail import generic_detail_html

    skus = SKU.objects.all()
    for sku in skus:
        generic_detail_html(sku)
    print('----------%s generated %s detail pages----------' % (time.ctime(), skus.count()))
