from django.contrib import admin
from django.urls import path, include
from apps.scraping.views import Index
urlpatterns = [
    path('admin/', admin.site.urls),
    path(r'', Index.as_view(
            template_name='scraping/index.html'), name='index_principal'),
    path(r'noticias', include(('apps.scraping.urls', 'app_noticias'), 
        namespace='app_noticias')),
]
