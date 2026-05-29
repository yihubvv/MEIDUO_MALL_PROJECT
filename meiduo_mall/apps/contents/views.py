from django.shortcuts import render
from django.conf import settings

# Create your views here.
from fdfs_client.client import Fdfs_client


def get_fdfs_client():
    return Fdfs_client(settings.FDFS_CLIENT_CONF)
