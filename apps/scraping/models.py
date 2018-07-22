from django.db import models

# Create your models here.
class Noticia(models.Model):
	titulo = models.TextField(max_length=1200)
	resumen = models.TextField(max_length=5000)
	autor = models.CharField(max_length=500, null=True, blank=True)
	fecha_publicacion = models.DateTimeField(null=True)
	contenido = models.TextField(blank=True)
	palabras_clave = models.TextField(blank=True)
	imagen_destacada = models.TextField()
	video = models.TextField()
	
	def __str__(self):
		return self.titulo

