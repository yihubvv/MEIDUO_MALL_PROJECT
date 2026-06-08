import os
import re
from meiduo_mall import settings
from django.template import loader
from utils.goods import get_categories, get_breadcrumb, get_goods_specs


FDFS_IMAGE_URL_RE = re.compile(
    r'https?://(?:image\.meiduo\.site|[\d.]+):8888/(?P<path>group\d+/[^"\'>\s]+)'
)


def normalize_fdfs_urls(html):
    base_url = settings.FDFS_BASE_URL.rstrip('/') + '/'
    return FDFS_IMAGE_URL_RE.sub(lambda match: base_url + match.group('path'), html or '')


def generic_detail_html(sku):
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

    template_path = os.path.abspath(os.path.join(settings.BASE_DIR, 'templates', 'detail.html'))
    detail_template = loader.get_template('detail.html')
    template_origin = getattr(getattr(detail_template, 'origin', None), 'name', '')
    if template_origin and os.path.abspath(template_origin) != template_path:
        raise RuntimeError('Unexpected detail template: %s' % template_origin)
    print('Using detail template: %s' % template_path)
    detail_html_data = detail_template.render(context)
    file_path = os.path.join(os.path.dirname(settings.BASE_DIR), 'front_end_pc', 'goods', f'{sku.id}.html')
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(detail_html_data)

    return detail_html_data
