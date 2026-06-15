from django.conf import settings
from django.http import JsonResponse
from django.views import View

# Create your views here.
from fdfs_client.client import Fdfs_client

from apps.contents.models import ContentCategory
from meiduo_mall import errors as error


def get_fdfs_client():
    return Fdfs_client(settings.FDFS_CLIENT_CONF)


class ContentListView(View):
    def get(self, request, key):
        try:
            category = ContentCategory.objects.get(key=key)
        except ContentCategory.DoesNotExist:
            return JsonResponse({'code': 400, 'errmsg': error.DOES_NOT_EXIST})

        contents = category.content_set.filter(status=True).order_by('sequence')
        content_list = []
        for content in contents:
            if not content.image:
                continue
            content_list.append({
                'id': content.id,
                'title': content.title,
                'url': content.url,
                'image_url': content.image.url,
                'text': content.text or '',
                'sequence': content.sequence,
            })

        return JsonResponse({
            'code': 0,
            'errmsg': error.NO_ERROR,
            'contents': content_list,
        })
