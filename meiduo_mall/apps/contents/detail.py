import os
from meiduo_mall import settings
from django.template import loader
from utils.goods import get_categories, get_breadcrumb, get_goods_specs
def generic_detail_html(sku):
    categories = get_categories()
    breadcrumb = get_breadcrumb(sku.category)
    goods_specs = get_goods_specs(sku)
    context = {
        'categories': categories,
        'breadcrumb': breadcrumb,
        'sku': sku,
        'specs': goods_specs,
    }

    detail_template = loader.get_template('detail.html')
    detail_html_data = detail_template.render(context)
    file_path = os.path.join(os.path.dirname(settings.BASE_DIR), 'front_end_pc', 'goods', f'{sku.id}.html')
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(detail_html_data)

    return detail_html_data