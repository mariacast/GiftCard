from django.db import models

# Create your models here.
class CodigoQr(models.Model):

	lote= models.CharField(max_length=50)
	fecha_creacion = models.DateTimeField()
	fecha_modificacion = models.DateTimeField(null = True)
	fecha_expiracion = models.DateTimeField(null = True)
	estado = models.CharField(max_length=1)
	hashPrivado = models.DecimalField( max_digits=60, decimal_places=0)
	hashVerificacion = models.DecimalField( max_digits=60, decimal_places=0)
	opciones = models.CharField(max_length=10)
	dias = models.CharField(max_length=3)

class Categoria(models.Model):	
	
	nombre = models.CharField(max_length=40)
	
class Plantilla(models.Model):
	
	categoria = models.ForeignKey(Categoria)
	nombre = models.CharField(max_length=40)
	url = models.TextField()

class Frase(models.Model):
	
	categoria = models.ForeignKey(Categoria)
	contenido = models.TextField()


class MultimediaQr(models.Model):

	video= models.TextField()
	codigoqr= models.ForeignKey(CodigoQr)
	
class QrMensaje(models.Model):

	mensaje= models.TextField()
	urlMusica= models.TextField()
	codigoqr= models.ForeignKey(CodigoQr)

class QrPlantilla(models.Model):
	
	plantilla = models.ForeignKey(Plantilla)
	codigoqr = models.ForeignKey(CodigoQr)
	
class Usuario(models.Model):

	nombre= models.CharField(max_length=100)
	correo= models.CharField(max_length=60)
	contrasena= models.TextField()
	estado = models.CharField(max_length=1)

class CodigoUsuario(models.Model):
	codigoqr = models.ForeignKey(CodigoQr)
	usuario = models.ForeignKey(Usuario)

	
class Vendedor(models.Model):
	user= models.CharField(max_length=50)
	nombre= models.CharField(max_length=100)
	correo= models.CharField(max_length=60)
	contrasena= models.TextField()
	estado = models.CharField(max_length=1)

class CodigoVendedor(models.Model):
	codigo = models.ForeignKey(CodigoQr)
	vendedor = models.ForeignKey(Vendedor)
	
class UsuarioVendedor(models.Model):
	vendedor = models.ForeignKey(Vendedor)
	usuario = models.ForeignKey(Usuario)
	cantidad =  models.IntegerField()

class Tema(models.Model):
	nombre= models.CharField(max_length=60)
	descripcion= models.TextField()
	enlaces= models.TextField()
	codigo= models.CharField(max_length=60)
	defecto= models.CharField(max_length=1)

class CodigoTema(models.Model):
	codigo = models.ForeignKey(CodigoQr)
	tema = models.ForeignKey(Tema)

class CodigoCategoria(models.Model):
	codigo = models.ForeignKey(CodigoQr)
	categoria = models.ForeignKey(Categoria)

class ImagenInicial(models.Model):
	
	nombre = models.CharField(max_length=40)
	url = models.TextField()

class CodigoImagen(models.Model):
	codigo = models.ForeignKey(CodigoQr)
	imagen = models.ForeignKey(ImagenInicial)

class CodigoImgLibre(models.Model):

	imagen = models.TextField()
	posicion = models.CharField(max_length=5)
	codigoqr = models.ForeignKey(CodigoQr)

class Marco(models.Model):
	nombre= models.CharField(max_length=60)
	enlace= models.TextField()
	defecto= models.CharField(max_length=1)

class CodigoMarco(models.Model):
	codigo = models.ForeignKey(CodigoQr)
	marco = models.ForeignKey(Marco)
