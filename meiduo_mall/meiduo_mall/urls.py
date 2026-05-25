"""meiduo_mall URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, register_converter
from django.urls.converters import get_converters

# from django.http import HttpResponse

# def log(request):

#     # 1. Import logging
#     import logging

#     # 2. Create a logger
#     logger = logging.getLogger('django')

#     # 3. Call logger methods to save logs
#     logger.info('User logged in')
#     logger.warning('Redis cache is insufficient')
#     logger.error('This record does not exist')
#     logger.debug('~~~~~~~~~~~~~~~')

#     return HttpResponse('log')

# Register converter
from utils.converters import UsernameConverter, MobileConverter

if 'username' not in get_converters():
    register_converter(UsernameConverter, 'username')

register_converter(MobileConverter, 'mobile')

urlpatterns = [
    path('admin/', admin.site.urls),
    # Import the routes from the users application
    path('',include('apps.users.urls')),
]
