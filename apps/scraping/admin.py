from django.contrib import admin
from .models import Noticia
# Register your models here.
class NoticiaAdmin(admin.ModelAdmin):
    model = Noticia
    list_display = ['titulo', 'resumen', 'autor', 'contenido', 'fecha_publicacion'	 ]

admin.site.register(Noticia, NoticiaAdmin)