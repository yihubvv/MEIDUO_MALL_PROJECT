#!/usr/bin/env python3

import os
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DJANGO_ROOT = PROJECT_ROOT / 'meiduo_mall'

sys.path.insert(0, str(DJANGO_ROOT))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meiduo_mall.settings')

import django

django.setup()

from apps.contents.detail import generic_detail_html
from apps.goods.models import SKU


def generate_all_static_sku_detail_htmls():
    count = 0
    for sku in SKU.objects.all().iterator():
        generic_detail_html(sku)
        count += 1
        print(sku.id)
    print('Generated %s static detail pages.' % count)
    return count


if __name__ == '__main__':
    generate_all_static_sku_detail_htmls()
