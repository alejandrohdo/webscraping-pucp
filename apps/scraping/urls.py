from django.contrib import admin
from django.urls import path
from .views import procesar_url
urlpatterns = [
    path(r'procesar', procesar_url, name='p_procesar')

]
