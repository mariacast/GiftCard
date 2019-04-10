from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest
from django.views import generic
from django.db.models import Count, Q
from django.utils import timezone
from django.shortcuts import get_object_or_404, render
from django.core.urlresolvers import reverse
from django.template import RequestContext, loader
from django import forms
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics import renderPDF
from .models import CodigoQr, MultimediaQr, Categoria, Plantilla, QrPlantilla, QrMensaje, Usuario, CodigoUsuario, Frase, Vendedor, CodigoVendedor,UsuarioVendedor, Tema, CodigoTema, CodigoCategoria, ImagenInicial, CodigoImagen,CodigoImgLibre, Marco, CodigoMarco
from io import BytesIO, StringIO
from zipfile import ZipFile, ZIP_DEFLATED
from django.db import connection
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib.auth import logout
from django.contrib.auth.views import logout
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail, BadHeaderError
from django.core.mail import EmailMessage

from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate

from datetime import timedelta, datetime
import django_excel as excel
import time
import random
import qrcode
import reportlab
import hashlib as hl
import base64 as b64
import pytz
import itertools
import json
import os
import requests
import subprocess as spp
import re


#ip del server
BASE1 = "https://192.168.1.34";
#ip del server con el puerto para el https
BASE2 = "https://192.168.1.34:9025";
#ip del server con el puerto para el http
BASE3 = "http://192.168.1.34";
#direccion en el server en donde se encuentra ubicado el archivo liser.py
BASE4 = "/home/maria/giftcard/gift/main/";
#path carpeta con videos
BASE5 = "/var/www/html/pool/";

#ip del server
#BASE1 = "https://192.168.0.20";
#ip del server con el puerto para el https
#BASE2 = "https://192.168.0.20:8000";
#ip del server con el puerto para el http
#BASE3 = "http://192.168.0.20";
#direccion en el server en donde se encuentra ubicado el archivo liser.py
#BASE4 = "/home/desarrollo/Documentos/giftCard/gift/main/";
#path carpeta con videos
#BASE5 = "/var/www/html/pool/";



def limpiarCodigo(request):
	#almacena la frase guardada
	if(request.method == "POST"):
		code= request.POST["code"]

		codigos = CodigoQr.objects.filter()
		#valida si exite codigosqr
		if(len(codigos)>0):
			codigo = CodigoQr.objects.get(id=code)
			if(codigo):
				qrplantilla = QrPlantilla.objects.filter(codigoqr_id=code)
				if(len(qrplantilla)>0):
					plantilla = QrPlantilla.objects.get(codigoqr_id=code)
					plantilla.delete()
				#elimina el contenido en mensaje y cancion
				qrmensaje = QrMensaje.objects.filter(codigoqr_id=code)
				if(len(qrmensaje)>0):
					mensajeqr = QrMensaje.objects.get(codigoqr_id=code)
					mensajeqr.delete()
				#elimina el contenido multimedia - video
				multimediaqr = MultimediaQr.objects.filter(codigoqr_id=code)
				if(len(multimediaqr)>0):
					multimedia = MultimediaQr.objects.get(codigoqr_id=code)
					multimedia.delete()
				codigousuario = CodigoUsuario.objects.filter(codigoqr_id=code)
				if(len(codigousuario)>0):
					codeusu = CodigoUsuario.objects.get(codigoqr_id=code)
					codeusu.delete()
				codigo = CodigoQr.objects.get(id=code)
				codigo.estado = "0";
				codigo.fecha_modificacion = None
				codigo.fecha_expiracion = None
				codigo.save()
				response=1
			else:
				response=2
		else:
			response=3
		return HttpResponse(
				json.dumps(response),
				content_type="application/json"
			)
	else:
		return HttpResponse("Intenta de nuevo")


def landingPage(request):

	template = loader.get_template('main/landingPage.html')

	context = RequestContext(request, {
	'tema': "admin",


    })
	return HttpResponse(template.render(context))




@csrf_exempt
def eliminarExpirados(request):
	#funcion para eliminar codigos expirados
	clave = request.POST.get('clave')

	mensaje=""
	if(clave=="VuOvfxdGRuEvqOAcB9q7G65eTFmmO1fGqndwmLx5o5B5wKFJoU8aPS778aNx"):
		#calcula la fecha actual
		timezone.activate(pytz.timezone("America/Bogota"))
		hoy = str(timezone.localtime(timezone.now()))
		hoy = hoy[:19]
		hoy = datetime.strptime(hoy, "%Y-%m-%d %H:%M:%S")
		#busca todos los codigosqr
		codigos = CodigoQr.objects.filter()
		#valida si exite codigosqr
		if(len(codigos)>0):
			eliminados=[]
			#recorre los qr encontrados
			for i in codigos:
				#valida si la fecha de expiracion es diferente a Null y si el qr esta creado, grabado o visto
				if(i.fecha_expiracion != None and int(i.estado) <=2):

					expir = str(i.fecha_expiracion)
					expir = expir[:19]
					expiracion = datetime.strptime(expir, "%Y-%m-%d %H:%M:%S")

					#verifica que la fecha de expiracion es menor o igual a la de hoy
					if(expiracion <= hoy):

						#elimina el contenido en plantilla
						qrplantilla = QrPlantilla.objects.filter(codigoqr_id=i.id)
						if(len(qrplantilla)>0):
							plantilla = QrPlantilla.objects.get(codigoqr_id=i.id)
							plantilla.delete()
						#elimina el contenido en mensaje y cancion
						qrmensaje = QrMensaje.objects.filter(codigoqr_id=i.id)
						if(len(qrmensaje)>0):
							mensajeqr = QrMensaje.objects.get(codigoqr_id=i.id)
							mensajeqr.delete()
						#elimina el contenido multimedia - video
						multimediaqr = MultimediaQr.objects.filter(codigoqr_id=i.id)
						if(len(multimediaqr)>0):
							multimedia = MultimediaQr.objects.get(codigoqr_id=i.id)
							eliminados.append([multimedia.codigoqr_id, multimedia.video ])
							multimedia.delete()
						else:
							eliminados.append([i.id])



						#actualiza a estado 3 - expirado
						codigo = CodigoQr.objects.get(id=i.id)
						codigo.estado="3"
						codigo.save()

			#array de codigos eliminados
			mensaje= eliminados
		else:
			mensaje="no hay codigos qr expiraados"
	else:
		mensaje="Clave incorrecta"
	#retorna lo eliminado
	return HttpResponse(
            json.dumps(mensaje),
            content_type="application/json"
        )





def indexView(request):

	if "username" in request.session:
		return redirect('/main/indexVendedor/')
	else:

		lista_codigos = CodigoQr.objects.values('fecha_creacion','lote').annotate(dcount=Count('lote')).order_by('-fecha_creacion')
		template = loader.get_template('main/index.html')
		context = RequestContext(request, {
			'lista_codigos': lista_codigos,
			'tema': "admin",
		})
		return HttpResponse(template.render(context))


def indexVendedorView(request):
	#muestra lista de lotes
	if "username" in request.session:
		vendedor = Vendedor.objects.get(user=request.session.get('username'))
		#lista = CodigoQr.objects.values('fecha_creacion','lote').annotate(dcount=Count('lote')).order_by('-fecha_creacion')
		lista = CodigoVendedor.objects.values('codigo__fecha_creacion','codigo__lote').filter(vendedor=vendedor.id).annotate(dcount=Count('codigo__lote')).order_by('-codigo__fecha_creacion')
		#lista_codigos=[]

		lista_codigos=[]
		for i in range(len(lista)):
			print(lista[i])
			lista_codigos.append({'fecha_creacion': lista[i]['codigo__fecha_creacion'],'lote' : lista[i]['codigo__lote']})
			#lote = CodigoVendedor.objects.filter(usuario=usuario.id).filter(lote=lista[i]['lote'])
		#	if(len(lote)>0):

		#

	template = loader.get_template('main/indexVendedor.html')
	context = RequestContext(request, {
		'lista_codigos': lista_codigos,
		'tema': "admin",
	})
	return HttpResponse(template.render(context))


def login_view(request):
	#hacer login a la aplicacion
    # Si el usuario esta ya logueado, lo redireccionamos a index_view
    if request.user.is_authenticated():
        return redirect('/main/index/')
    if "username" in request.session:
        return redirect('/main/indexVendedor/')


    mensaje = ''
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)

                return redirect('/main/index/')


            else:
                # Redireccionar informando que la cuenta esta inactiva
                # Lo dejo como ejercicio al lector :)
                pass
        vendedor = Vendedor.objects.filter(user=username)
        if(len(vendedor) > 0):
            vende = Vendedor.objects.get(user=username)
            contrasena = hl.sha512(password.encode('utf-8')).hexdigest()
            if(vende.contrasena == contrasena):
               request.session["username"] = username
               return redirect('/main/indexVendedor/')



        mensaje = 'Nombre de usuario o contraseña no valido'
    return render(request, 'main/login.html', {'mensaje': mensaje,'tema': "admin"})

def logout_view(request):
	#sale de la aplicacion
	try:
		del request.session['username']
	except KeyError:
		pass
	logout(request)
	return redirect('/main/login/')

def generarView(CodigoQr):
	#envia al template en donde se generan los lotes de codigosqr
    model = CodigoQr
    temas = Tema.objects.filter().order_by('-defecto','nombre')
    marcos = Marco.objects.filter().order_by('-defecto','nombre')
    categorias = Categoria.objects.filter().order_by('nombre')
    imagenesIni = ImagenInicial.objects.filter().order_by('nombre')
    template = loader.get_template('main/generar.html')
    context = RequestContext(model, {
        'css': "generar",
        'temas': temas,
        'marcos': marcos,
        'categorias': categorias,
        'imagenes': imagenesIni,
        'tema': "admin",

    })
    #return HttpResponse(template.render(RequestContext(model)))
    return HttpResponse(template.render(context))


def ingresarPlantillaView(request):
	#envia a template end donde se ingresan las plantillas nuevas
    model = Plantilla
    #busca las categorias existente
    categorias = Categoria.objects.filter()
    listCategorias=[]
    if(len(categorias)>0):
	    for r in categorias:
		    listCategorias.append([r.id,r.nombre])

    plantilla = Plantilla.objects.filter().order_by('categoria')
    listPlantilla=[]
    if(len(plantilla)>0):
	    for r in plantilla:
		    cate = Categoria.objects.get(id=r.categoria_id)
		    listPlantilla.append([r.id,cate.nombre,r.nombre,r.url])

    template = loader.get_template('main/ingresarPlantilla.html')
    context = RequestContext(request, {
        'categorias': listCategorias,
        'plantillas': listPlantilla,
        'css': "plantilla",
        'tema': "admin",
    })
    #envia datos
    return HttpResponse(template.render(context))

def almacenarPlantilla(request):
	#almacena la plantilla guardada
	if(request.method == "POST"):
		categoria= request.POST["categoria"]
		nombre= request.POST["nombre"]
		url= request.POST["url"]
		plantilla_id= request.POST["id"]
		#verifica que los campos no esten vacios aunque ya la validacion fue hecha en javascript
		if(categoria==""):
			return HttpResponse("El campo Categoria no puede ser vacio")
		elif(nombre==""):
			return HttpResponse("El campo Nombre no puede ser vacio")
		elif(url==""):
			return HttpResponse("El campo Url no puede ser vacio")
		else:
			if(plantilla_id=="0"):
				#si los campos son diferentes de vacios se guarda la plantilla
				plantilla= Plantilla()
				plantilla.categoria_id = categoria
				plantilla.nombre = nombre
				plantilla.url = url
				plantilla.save()
			else:
				plantilla = Plantilla.objects.get(id=plantilla_id)
				plantilla.categoria_id = categoria
				plantilla.nombre = nombre
				plantilla.url = url
				plantilla.save()
			#vuelve a retorna a la vista para ingresar una nueva plantilla
			return redirect('/main/ingresarPlantilla/')

	else:
		return redirect('/main/ingresarPlantilla/')

def editarPlantilla(request):
	plantilla_id = request.POST.get('plantilla_id')

	plantilla = Plantilla.objects.filter(id=plantilla_id)
	plantillaArray = []
	if(len(plantilla)>0):
		plantilla = Plantilla.objects.get(id=plantilla_id)
		plantillaArray.append([plantilla.id,plantilla.nombre,plantilla.categoria_id,plantilla.url])

		return HttpResponse(
				json.dumps(plantillaArray),
				content_type="application/json"
			)

def eliminarPlantilla(request):
	plantilla_id = request.POST.get('plantilla_id')

	plantilla = Plantilla.objects.filter(id=plantilla_id)

	if(len(plantilla)>0):
		plantilla = Plantilla.objects.get(id=plantilla_id)
		plantilla.delete()
		mensaje=1
		return HttpResponse(
				json.dumps(mensaje),
				content_type="application/json"
			)


def ingresarCategoriaView(request):
	#envia a template end donde se ingresan las categorias nuevas
    model = Categoria
    #busca las categorias existente
    categorias = Categoria.objects.filter()
    listCategorias=[]
    if(len(categorias)>0):
	    for r in categorias:
		    listCategorias.append([r.id,r.nombre])


    template = loader.get_template('main/ingresarCategoria.html')
    context = RequestContext(request, {
        'categorias': listCategorias,
        'css': "categoria",
        'tema': "admin",

    })
    #envia datos
    return HttpResponse(template.render(context))




def almacenarCategoria(request):
	#almacena la categoria guardada
	if(request.method == "POST"):

		nombre= request.POST["nombre"]

		categoria_id= request.POST["id"]
		#verifica que los campos no esten vacios aunque ya la validacion fue hecha en javascript

		if(nombre==""):
			return HttpResponse("El campo Nombre no puede ser vacio")

		else:
			if(categoria_id=="0"):
				#si los campos son diferentes de vacios se guarda la categoria
				categoria= Categoria()
				categoria.nombre = nombre

				categoria.save()
			else:
				categoria = Categoria.objects.get(id=categoria_id)
				categoria.nombre = nombre
				categoria.save()
			#vuelve a retorna a la vista para ingresar una nueva categoria
			return redirect('/main/ingresarCategoria/')

	else:
		return redirect('/main/ingresarCategoria/')

def editarCategoria(request):
	categoria_id = request.POST.get('categoria_id')

	categoria = Categoria.objects.filter(id=categoria_id)
	categoriaArray = []
	if(len(categoria)>0):
		categoria = Categoria.objects.get(id=categoria_id)
		categoriaArray.append([categoria.id,categoria.nombre])

		return HttpResponse(
				json.dumps(categoriaArray),
				content_type="application/json"
			)

def eliminarCategoria(request):
	categoria_id = request.POST.get('categoria_id')

	categoria = Categoria.objects.filter(id=categoria_id)

	if(len(categoria)>0):
		categoria = Categoria.objects.get(id=categoria_id)
		categoria.delete()
		mensaje=1
		return HttpResponse(
				json.dumps(mensaje),
				content_type="application/json"
			)


def vendedorView(request):
	#envia a template end donde se ingresan las categorias nuevas
    model = Vendedor
    #busca las categorias existente
    vendedores = Vendedor.objects.filter()
    listVendedores=[]
    if(len(vendedores)>0):
	    for r in vendedores:
		    listVendedores.append([r.id,r.user,r.nombre,r.correo])


    template = loader.get_template('main/vendedor.html')
    context = RequestContext(request, {
        'vendedores': listVendedores,
        'css': "vendedor",
        'tema': "admin",

    })
    #envia datos
    return HttpResponse(template.render(context))



def almacenarVendedor(request):
	#almacena la categoria guardada
	if(request.method == "POST"):

		user= request.POST["usuario"]
		nombre= request.POST["nombre"]
		correo= request.POST["correo"]
		contrasena= request.POST["contrasena"]
		#estado= request.POST["estado"]

		vendedor_id= request.POST["id"]
		bandera= request.POST["bandera"]

		contrasena = hl.sha512(contrasena.encode('utf-8')).hexdigest()
		#verifica que los campos no esten vacios aunque ya la validacion fue hecha en javascript
		mensaje=""

		if(bandera=="c"):
			vende = Vendedor.objects.get(id=vendedor_id)
			vende.contrasena = contrasena
			vende.save()
			mensaje=1
		else:

			if(vendedor_id=="0"):
				#si los campos son diferentes de vacios se guarda la categoria
				vende = Vendedor.objects.filter(user=user)
				if(len(vende)>0):
					mensaje=2
				else:
					vende= Vendedor()
					vende.nombre = nombre
					vende.user = user
					vende.correo = correo
					vende.contrasena = contrasena
					vende.estado = "A"

					vende.save()
					mensaje=1
			else:
				vende = Vendedor.objects.get(id=vendedor_id)
				vende.nombre = nombre
				vende.user = user
				vende.correo = correo
				vende.contrasena = contrasena
				vende.estado = "A"
				vende.save()
		#vuelve a retorna a la vista para ingresar una nueva categoria
				mensaje=1
		return HttpResponse(
				json.dumps(mensaje),
				content_type="application/json"
			)


	else:
		return redirect('/main/vendedor/')

def editarVendedor(request):
	vendedor_id = request.POST.get('vendedor_id')

	vende = Vendedor.objects.filter(id=vendedor_id)
	vendedorArray = []
	if(len(vende)>0):
		vendedor = Vendedor.objects.get(id=vendedor_id)
		vendedorArray.append([vendedor.id,vendedor.user,vendedor.nombre,vendedor.correo])

		return HttpResponse(
				json.dumps(vendedorArray),
				content_type="application/json"
			)

def eliminarVendedor(request):
	vendedor_id = request.POST.get('vendedor_id')

	vende = Vendedor.objects.filter(id=vendedor_id)

	if(len(vende)>0):
		vendedor = Vendedor.objects.get(id=vendedor_id)
		vendedor.delete()
		mensaje=1
		return HttpResponse(
				json.dumps(mensaje),
				content_type="application/json"
			)


def usuarioView(request):
	#envia a template end donde se ingresan las categorias nuevas
    model = Usuario
    #busca las categorias existente

    usuarios = Usuario.objects.filter().order_by('nombre')


    template = loader.get_template('main/usuario.html')
    context = RequestContext(request, {

        'usuarios': usuarios,
        'css': "usuario",
        'tema':"admin",

    })
    #envia datos
    return HttpResponse(template.render(context))

def usuariosVendedorView(request):
	#envia a template end donde se ingresan las categorias nuevas
    model = Usuario
    #busca las categorias existente
    vendedor = Vendedor.objects.get(user=request.session.get('username'))

    usuarios = UsuarioVendedor.objects.values('usuario__id','usuario__nombre','usuario__correo','cantidad').filter(vendedor=vendedor.id).order_by('usuario__nombre')


    template = loader.get_template('main/usuariosVendedor.html')
    context = RequestContext(request, {

        'usuarios': usuarios,
        'css': "usuario",
        'tema':"admin",

    })
    #envia datos
    return HttpResponse(template.render(context))


def enviarCorreoUsuario(request):
	if(request.method == "POST"):
		respon = json.loads(request.body.decode("utf8"))

		asunto = respon["asunto"]
		mensaje = respon["mensaje"]
		correos = respon["correos"]
		archivo = respon["archivo"]
		exten = respon["extension"]
		if(exten=="0" and archivo=="0"):
			try:
				email = EmailMessage(asunto, mensaje, to=correos)

				email.send()

				mensaje= 1

			except BadHeaderError:
				mensaje= 2



		else:


			a = int(random.randint(3,5*23))
			b = int(random.randint(5,3*25))
			c = int(random.randint(2,4*10))
			e = int(random.randint(6,4*17))
			d= int((((a*c)*(b*e))/a*e))

			#actualizacion de contraseña en la base de datos
			ran = b64.b64encode(str(d).encode('utf8')).decode('utf8')
			ale = hl.sha512(ran.encode('utf-8')).hexdigest()
			ale= ale[:10]+"."+exten



			count = archivo.count(",")

			if(count>0):

				posicion = archivo.find(",")
				archivo = archivo[posicion+1:]


			f = open("/tmp/"+ale, "a")
			f.write(archivo)
			f.close()

			spp.getstatusoutput("base64 -d /tmp/"+ale+" > "+BASE5+str(ale))


			fp = open(BASE5+ale, 'rb')
			attach = MIMEApplication(fp.read(), exten)
			attach.add_header('Content-Disposition', 'attachment', filename= "Archivo_"+ale+"."+exten)

			try:
				email = EmailMessage(asunto, mensaje, to=correos)
				email.attach(attach)
				email.send()

				mensaje= 1

			except BadHeaderError:
				mensaje= 2

			spp.getstatusoutput("rm -frv /tmp/"+ale)
			spp.getstatusoutput("rm -frv "+BASE5+ale)

		return HttpResponse(
				json.dumps(mensaje),
				content_type="application/json"
			)


	else:
		return redirect('/main/usuario/')


def asignarVendedorView(request):

    vendedores2 = Vendedor.objects.filter().order_by('nombre')

    lotes = CodigoQr.objects.values('fecha_creacion','lote').annotate(dcount=Count('lote')).order_by('-fecha_creacion')
    lotcod =[]
    conta=0
    for i in lotes:

        vendedores = CodigoVendedor.objects.values('vendedor__id','vendedor__nombre').filter(codigo__lote = i['lote']).annotate(dcount=Count('vendedor__id')).order_by('vendedor__nombre')
        listcod=[]
        totalAsignado=0
        cantidadLote = CodigoQr.objects.filter(lote = i['lote']).count()
        for r in vendedores:
            cantidad = CodigoVendedor.objects.filter(vendedor = r['vendedor__id']).filter(codigo__lote = i['lote']).count()
            totalAsignado= totalAsignado+ cantidad
            listcod.append([r['vendedor__nombre'],cantidad])
        cantidadDefault = cantidadLote - totalAsignado
        venDef = Vendedor.objects.filter(id=1).count()
        if(venDef > 0):
            venDef = Vendedor.objects.get(id=1)
            venDef = venDef.nombre
            listcod.append([venDef,cantidadDefault])


        lotcod.append([i['lote'],listcod,cantidadLote])


    template = loader.get_template('main/asignarVendedor.html')
    context = RequestContext(request, {

        'vendedores2': vendedores2,
        'lotes': lotes,
        'lotcod': lotcod,
        'css': "asignarVendedor",
        'tema': "admin",

    })
    #envia datos
    return HttpResponse(template.render(context))



def almacenarCodigoVendedor(request):
	#almacena la categoria guardada
	if(request.method == "POST"):

		vendedor= request.POST["vendedor"]
		lote= request.POST["lote"]
		cantidad= request.POST["cantidad"]
		mensaje=""

		codigosTotales = CodigoQr.objects.filter(lote=lote).filter(estado="0").count()
		codigosAsign = CodigoVendedor.objects.filter(codigo__lote=lote).count()

		print(codigosTotales)
		print(codigosAsign)
		codigosDis= codigosTotales - codigosAsign
		if(int(cantidad) > codigosDis):
			mensaje=0
		else:
			codigos= CodigoQr.objects.filter(lote=lote).filter(estado="0")
			contador = int(cantidad)
			for i in codigos:
				if(contador > 0):
					existe = CodigoVendedor.objects.filter(codigo=i.id).count()
					if(existe == 0):
						codigo= CodigoVendedor()
						codigo.vendedor_id = vendedor
						codigo.codigo_id = i.id
						codigo.save()
						contador = contador - 1
			mensaje=1


		return HttpResponse(
				json.dumps(mensaje),
				content_type="application/json"
			)


	else:
		return redirect('/main/vendedor/')

def editarCodigoVendedor(request):
	vendedor_id = request.POST.get('vendedor_id')

	vende = Vendedor.objects.filter(id=vendedor_id)
	vendedorArray = []
	if(len(vende)>0):
		vendedor = Vendedor.objects.get(id=vendedor_id)
		vendedorArray.append([vendedor.id,vendedor.user,vendedor.nombre,vendedor.correo])

		return HttpResponse(
				json.dumps(vendedorArray),
				content_type="application/json"
			)

def eliminarCodigoVendedor(request):
	regis_id = request.POST.get('regis_id')

	codigos = CodigoVendedor.objects.filter(codigo=regis_id).filter(codigo__estado="0")

	if(len(codigos)>0):
		codigoven = CodigoVendedor.objects.get(codigo=regis_id)
		codigoven.delete()
		mensaje=1
	else:
		mensaje=2
	return HttpResponse(
			json.dumps(mensaje),
			content_type="application/json"
		)

def devolucion(request):
	respon = json.loads(request.body.decode("utf8"))

	codes = respon["codigos"]
	for i in codes:

		codigo = CodigoVendedor.objects.filter(codigo__estado="0").filter(codigo= i)

		if(len(codigo)>0):

			codigoven = CodigoVendedor.objects.get(codigo=i)
			codigoven.delete()
			mensaje=1
	return HttpResponse(
			json.dumps(mensaje),
			content_type="application/json"
		)



def traerLotes(request):
	vendedor_id = request.POST.get('id')


	sele="<option value='@'>Seleccione...</option>";

	if(vendedor_id != ""):
		lista = CodigoVendedor.objects.values('codigo__lote').filter(vendedor=vendedor_id).annotate(dcount=Count('codigo__lote')).order_by('codigo__lote')
		if(lista):

			for i in lista:
				print(i)
				sele+= "<option value='"+str(i['codigo__lote'])+"'>"+str(i['codigo__lote'])+"</option>";


	return HttpResponse(
			json.dumps(sele),
			content_type="application/json"
		)


def traerCodigos(request):
	vendedor_id = request.POST.get('vendedor')
	lote_id = request.POST.get('lote')


	sele="<option value='@'>Seleccione...</option>";

	if(vendedor_id != "" and lote_id != ""):
		lista = CodigoVendedor.objects.values('codigo__id').filter(vendedor=vendedor_id).filter(codigo__lote=lote_id).order_by('codigo__id')
		if(lista):

			for i in lista:

				sele+= "<option value='"+str(i['codigo__id'])+"'>"+str(i['codigo__id'])+"</option>";


	return HttpResponse(
			json.dumps(sele),
			content_type="application/json"
		)


def ingresarFraseView(request):
	#envia a template end donde se ingresan las frases nuevas
    model = Frase
    #busca las categorias existente
    categorias = Categoria.objects.filter()
    listCategorias=[]
    if(len(categorias)>0):
	    for r in categorias:
		    listCategorias.append([r.id,r.nombre])

    frase = Frase.objects.filter().order_by('categoria')
    listfrase=[]
    if(len(frase)>0):
	    for r in frase:
		    cate = Categoria.objects.get(id=r.categoria_id)
		    listfrase.append([r.id,cate.nombre,r.contenido])

    template = loader.get_template('main/ingresarFrase.html')
    context = RequestContext(request, {
        'categorias': listCategorias,
        'frases': listfrase,
        'css': "frase",
        'tema': "admin",
    })
    #envia datos
    return HttpResponse(template.render(context))

def almacenarFrase(request):
	#almacena la frase guardada
	if(request.method == "POST"):
		categoria= request.POST["categoria"]
		contenido= request.POST["contenido"]
		frase_id= request.POST["id"]
		#verifica que los campos no esten vacios aunque ya la validacion fue hecha en javascript
		if(categoria==""):
			return HttpResponse("El campo Categoria no puede ser vacio")
		elif(contenido==""):
			return HttpResponse("El campo contenido no puede ser vacio")

		else:
			if(frase_id=="0"):
				#si los campos son diferentes de vacios se guarda la frase
				frase= Frase()
				frase.categoria_id = categoria
				frase.contenido = contenido
				frase.save()
			else:
				frase = Frase.objects.get(id=frase_id)
				frase.categoria_id = categoria
				frase.contenido = contenido
				frase.save()
			#vuelve a retorna a la vista para ingresar una nueva frase
			return redirect('/main/ingresarFrase/')

	else:
		return redirect('/main/ingresarFrase/')

def editarFrase(request):
	frase_id = request.POST.get('frase_id')

	frase = Frase.objects.filter(id=frase_id)
	fraseArray = []
	if(len(frase)>0):
		frase = Frase.objects.get(id=frase_id)
		fraseArray.append([frase.id,frase.contenido,frase.categoria_id])

		return HttpResponse(
				json.dumps(fraseArray),
				content_type="application/json"
			)
def urlIframe(request):
	plantilla_id = request.POST.get('id')
	url=""
	plantilla = Plantilla.objects.filter(id=plantilla_id)
	if(len(plantilla)>0):
		planti = Plantilla.objects.get(id=plantilla_id)
		url = planti.url
	else:
		url=""
	return HttpResponse(
			json.dumps(url),
			content_type="application/json"
		)

def eliminarFrase(request):
	frase_id = request.POST.get('frase_id')

	frase = Frase.objects.filter(id=frase_id)

	if(len(frase)>0):
		frase = Frase.objects.get(id=frase_id)
		frase.delete()
		mensaje=1
		return HttpResponse(
				json.dumps(mensaje),
				content_type="application/json"
			)


def consultarFrases(request):
	#almacena la frase guardada
	if(request.method == "POST"):
		texto= request.POST["texto"]
		categoria= request.POST["categoria"]





		if(categoria != ""):

			frase = Frase.objects.filter(contenido__contains= texto).filter(categoria = categoria).order_by('categoria')
			frases=[]
			if(len(frase)>0):
				for r in frase:

					frases.append([r.id,r.contenido])
		else:

			frase = Frase.objects.filter(contenido__contains= texto).order_by('categoria')
			frases=[]
			if(len(frase)>0):
				for r in frase:

					frases.append([r.id,r.contenido])

		return HttpResponse(
				json.dumps(frases),
				content_type="application/json"
			)
	else:
		return HttpResponse("Intenta de nuevo")


def pegarFras(request):
	#almacena la frase guardada
	if(request.method == "POST"):
		fras_id= request.POST["id"]


		frase = Frase.objects.filter(id=fras_id)
		if(len(frase)>0):
			frase=Frase.objects.get(id=fras_id)
			contenido = frase.contenido
		else:
			contenido=""
		return HttpResponse(
				json.dumps(contenido),
				content_type="application/json"
			)
	else:
		return HttpResponse("Intenta de nuevo")



def reportesView(request):
	#genera el reporte
	template = loader.get_template('main/reportes.html')
	#busca los codigos
	codigoqr = CodigoQr.objects.filter()
	#verifica si hay codigos creados
	if(len(codigoqr)==0):
		return HttpResponse("No se puede generar el reporte, porque no hay Codigos Qr creados")
	else:

	#si exite codigos los consulta de nuevoo agrupandolos por lote y ordenandolos por fecha de creacion
		lotes = CodigoQr.objects.values('fecha_creacion','lote').annotate(dcount=Count('lote')).order_by('-fecha_creacion')

		codeArray =[]
		totalesArray =[]
		totalE0=0
		totalE1=0
		totalE2=0
		totalE3=0
		totalE4=0
		totalE5=0
		totalTotal=0
		for codigo in lotes:
			#cuenta la cantidad de codigos por cada lote y estado
			estado0 = CodigoQr.objects.filter(lote=codigo['lote']).filter(estado="0").count()
			estado1 = CodigoQr.objects.filter(lote=codigo['lote']).filter(estado="1").count()
			estado2 = CodigoQr.objects.filter(lote=codigo['lote']).filter(estado="2").count()
			estado3 = CodigoQr.objects.filter(lote=codigo['lote']).filter(estado="3").count()
			estado4 = CodigoQr.objects.filter(lote=codigo['lote']).filter(estado="4").count()
			estado5 = CodigoQr.objects.filter(lote=codigo['lote']).filter(estado="5").count()
			#cuenta el total de codigos por lote
			total = CodigoQr.objects.filter(lote=codigo['lote']).count()
			#acumula los codigos por estado
			totalE0+=estado0
			totalE1+=estado1
			totalE2+=estado2
			totalE3+=estado3
			totalE4+=estado4
			totalE5+=estado5
			totalTotal+=total
			codeArray.append([codigo['fecha_creacion'],codigo['lote'],estado0,estado1,estado2,estado3,estado4,estado5,total])
		totalesArray.append([totalE0,totalE1,totalE2,totalE3,totalE4,totalE5,totalTotal])
	#envia la informacion al template
	context = RequestContext(request, {
		'codeArray': codeArray,
		'totalesArray': totalesArray,
		'css': "reporte",
		'tema': "admin",
	})
	return HttpResponse(template.render(context))


def reportesVendedorView(request):
	#genera el reporte
	template = loader.get_template('main/reportesVendedor.html')
	#busca los codigos
	codigoqr = CodigoQr.objects.filter()
	#verifica si hay codigos creados
	if(len(codigoqr)==0):
		return HttpResponse("No se puede generar el reporte, porque no hay Codigos Qr creados")
	else:

		if "username" in request.session:
			vendedor = Vendedor.objects.get(user=request.session.get('username'))
			#lotes = CodigoQr.objects.values('fecha_creacion','lote').annotate(dcount=Count('lote')).order_by('-fecha_creacion')
			lotes = CodigoVendedor.objects.values('codigo__fecha_creacion','codigo__lote').filter(vendedor=vendedor.id).annotate(dcount=Count('codigo__lote')).order_by('-codigo__fecha_creacion')
			codeArray =[]
			totalesArray =[]
			totalE0=0
			totalE1=0
			totalE2=0
			totalE3=0
			totalE4=0
			totalE5=0
			totalTotal=0
			for codigo in lotes:
				#cuenta la cantidad de codigos por cada lote y estado
				#estado0 = CodigoQr.objects.filter(lote=codigo['lote']).filter(estado="0").count()
				estado0 = CodigoVendedor.objects.filter(vendedor=vendedor.id).filter(codigo__lote=codigo['codigo__lote']).filter(codigo__estado="0").count()
				estado1 = CodigoVendedor.objects.filter(vendedor=vendedor.id).filter(codigo__lote=codigo['codigo__lote']).filter(codigo__estado="1").count()
				estado2 = CodigoVendedor.objects.filter(vendedor=vendedor.id).filter(codigo__lote=codigo['codigo__lote']).filter(codigo__estado="2").count()
				estado3 = CodigoVendedor.objects.filter(vendedor=vendedor.id).filter(codigo__lote=codigo['codigo__lote']).filter(codigo__estado="3").count()
				estado4 = CodigoVendedor.objects.filter(vendedor=vendedor.id).filter(codigo__lote=codigo['codigo__lote']).filter(codigo__estado="4").count()
				estado5 = CodigoVendedor.objects.filter(vendedor=vendedor.id).filter(codigo__lote=codigo['codigo__lote']).filter(codigo__estado="5").count()
				#estado1 = CodigoQr.objects.filter(lote=codigo['lote']).filter(estado="1").count()
				#estado2 = CodigoQr.objects.filter(lote=codigo['lote']).filter(estado="2").count()
				#estado3 = CodigoQr.objects.filter(lote=codigo['lote']).filter(estado="3").count()
				#estado4 = CodigoQr.objects.filter(lote=codigo['lote']).filter(estado="4").count()
				#estado5 = CodigoQr.objects.filter(lote=codigo['lote']).filter(estado="5").count()
				#cuenta el total de codigos por lote
				#total = CodigoQr.objects.filter(lote=codigo['lote']).count()
				total = CodigoVendedor.objects.filter(vendedor=vendedor.id).filter(codigo__lote=codigo['codigo__lote']).count()
				#acumula los codigos por estado
				totalE0+=estado0
				totalE1+=estado1
				totalE2+=estado2
				totalE3+=estado3
				totalE4+=estado4
				totalE5+=estado5
				totalTotal+=total
				codeArray.append([codigo['codigo__fecha_creacion'],codigo['codigo__lote'],estado0,estado1,estado2,estado3,estado4,estado5,total])
			totalesArray.append([totalE0,totalE1,totalE2,totalE3,totalE4,totalE5,totalTotal])

		else:
		#si exite codigos los consulta de nuevoo agrupandolos por lote y ordenandolos por fecha de creacion
			lotes = CodigoQr.objects.values('fecha_creacion','lote').annotate(dcount=Count('lote')).order_by('-fecha_creacion')

			codeArray =[]
			totalesArray =[]
			totalE0=0
			totalE1=0
			totalE2=0
			totalE3=0
			totalE4=0
			totalE5=0
			totalTotal=0
			for codigo in lotes:
				#cuenta la cantidad de codigos por cada lote y estado
				estado0 = CodigoQr.objects.filter(lote=codigo['lote']).filter(estado="0").count()
				estado1 = CodigoQr.objects.filter(lote=codigo['lote']).filter(estado="1").count()
				estado2 = CodigoQr.objects.filter(lote=codigo['lote']).filter(estado="2").count()
				estado3 = CodigoQr.objects.filter(lote=codigo['lote']).filter(estado="3").count()
				estado4 = CodigoQr.objects.filter(lote=codigo['lote']).filter(estado="4").count()
				estado5 = CodigoQr.objects.filter(lote=codigo['lote']).filter(estado="5").count()
				#cuenta el total de codigos por lote
				total = CodigoQr.objects.filter(lote=codigo['lote']).count()
				#acumula los codigos por estado
				totalE0+=estado0
				totalE1+=estado1
				totalE2+=estado2
				totalE3+=estado3
				totalE4+=estado4
				totalE5+=estado5
				totalTotal+=total
				codeArray.append([codigo['fecha_creacion'],codigo['lote'],estado0,estado1,estado2,estado3,estado4,estado5,total])
			totalesArray.append([totalE0,totalE1,totalE2,totalE3,totalE4,totalE5,totalTotal])
		#envia la informacion al template
		context = RequestContext(request, {
			'codeArray': codeArray,
			'totalesArray': totalesArray,
			'css': "reporte",
			'tema': "admin",
		})
		return HttpResponse(template.render(context))



def guardarRegistro(request):
	#guarda el registro de usuario
	if(request.method == "POST"):

		nombre = request.POST.get('nombre')
		correo = request.POST.get('correoRegistro')
		contrasena = request.POST.get('contrasenaRegistro')
		#encripta la contraseña
		contrasena = hl.sha512(contrasena.encode('utf-8')).hexdigest()
		usuarioCount = Usuario.objects.filter(correo=correo)
		if(len(usuarioCount)>0):
			#si hay un usuario existente con ese correo envia un 2 que significa que el usuario ya existe y no se puede registrar
			mensaje= 2
		else:
			#guarda el usuario
			usuario= Usuario()
			usuario.nombre = nombre
			usuario.correo= correo
			usuario.contrasena= contrasena
			usuario.estado= "A"
			usuario.save()
			mensaje= 1
		return HttpResponse(
				json.dumps(mensaje),
				content_type="application/json"
			)
	else:
		return HttpResponse("No se puede realizar el registro")


def cambiarContrasena(request):
	#cambiar contraseña de la multimedia
	contrasena = request.POST.get('contrasenaCambio')
	correo = request.POST.get('correoCambio')

	#encripta contraseña
	contrasena = hl.sha512(contrasena.encode('utf-8')).hexdigest()

	usuarioCount = Usuario.objects.filter(correo=correo)
	if(len(usuarioCount)==0):
		mensaje= 2
	else:
		#actualiza contraseña del usuario que corresponde al correo
		request.session['correo'] = correo
		usuario = Usuario.objects.get(correo=correo)
		usuario.contrasena= contrasena
		usuario.estado= "A"
		usuario.save()
		mensaje= 1
	return HttpResponse(
            json.dumps(mensaje),
            content_type="application/json"
        )

def eliminarGrabacion(request):
	#elimina grabacion
	code_id = request.POST.get('code_id')

	codigoqr = CodigoQr.objects.filter(id=code_id)
	#se valida que el codigo exista
	if(len(codigoqr)==0):
		mensaje="Codigo Qr no existe"
	else:
		#se actualiza el codigo a estado 5 de eliminado por el usuario
		codigo = CodigoQr.objects.get(id=code_id)
		codigo.estado="5"
		codigo.save()
		#se borra toda la multimedia perteneciente al codigo
		multimediaqr = MultimediaQr.objects.filter(codigoqr_id=code_id)
		if(len(multimediaqr)>0):
			multimedia = MultimediaQr.objects.get(codigoqr_id=code_id)
			multimedia.delete()
		qrplantilla = QrPlantilla.objects.filter(codigoqr_id=code_id)
		if(len(qrplantilla)>0):
			plantilla = QrPlantilla.objects.get(codigoqr_id=code_id)
			plantilla.delete()
		qrmensaje = QrMensaje.objects.filter(codigoqr_id=code_id)
		if(len(qrmensaje)>0):
			mensajeqr = QrMensaje.objects.get(codigoqr_id=code_id)
			mensajeqr.delete()

		mensaje="Eliminado con exito"

	return HttpResponse(
            json.dumps(mensaje),
            content_type="application/json"
        )
def verGrabacion(request):
	code_id = request.POST.get('code_id')

	codigo = CodigoQr.objects.filter(id=code_id)
	if(len(codigo)==0):
		mensaje="Codigo Qr no esxite"
	else:
		codigoqr= CodigoQr.objects.get(id=code_id)
		na = codigoqr.hashPrivado
		nc = codigoqr.hashVerificacion
		nb = nc / (na*727)

		pub = hl.sha512()
		pub.update(str(nb).encode('utf8'))
		dpub = pub.hexdigest()
		dpub = b64.b64encode(dpub.encode('utf8')).decode('utf8')

		enlace= "/main/confirmar/?id="+code_id+"&hash="+dpub

		return HttpResponse(
            json.dumps(enlace),
            content_type="application/json"
        )


def extenderGrabacion(request):
	#extender grabacion o codigo qr
	code_id = request.POST.get('code_id')
	code_actual= request.session.get('code_id')
	correo = request.session.get('correo')
	codigoqr = CodigoQr.objects.filter(id=code_id)
	#se valida que exista el codigo
	if(len(codigoqr)==0):
		mensaje="Codigo Qr no esxite"
	else:

		codigoActual = CodigoQr.objects.get(id=code_actual)
		estadoActual = codigoActual.estado
		#se valida que el codigo actual que se esta utilizando no se halla usado
		if(int(estadoActual)==0):
			#se calcula la fecha de hoy
			timezone.activate(pytz.timezone("America/Bogota"))
			fecha = str(timezone.localtime(timezone.now()))
			fechaActualizacion = fecha[0:18]
			# se actualiza el codigo actual y se pone estado 4 de utilizado para extender y la fecha de hoy como fecha de modificacion y expiracion
			codigoActual = CodigoQr.objects.get(id=code_actual)
			codigoActual.estado="4"
			codigoActual.fecha_modificacion= fechaActualizacion
			codigoActual.fecha_expiracion= fechaActualizacion
			codigoActual.save()
			#se relacion del codigo utilizado con el usuario que lo esta utilizando
			usuario = Usuario.objects.get(correo=correo)
			codigoUsuario= CodigoUsuario()
			codigoUsuario.codigoqr_id = code_actual
			codigoUsuario.usuario_id = usuario.id
			codigoUsuario.save()

			#se extiende la fecha al nuevo codigo
			codigoExtendido = CodigoQr.objects.get(id=code_id)

			expir = str(codigoExtendido.fecha_expiracion)
			expir = expir[:19]
			expiracion = datetime.strptime(expir, "%Y-%m-%d %H:%M:%S")
			dias= codigoActual.dias
			d = timedelta(days=int(dias))
			expiracionNueva = expiracion + d

			codigoExtendido.fecha_expiracion= expiracionNueva
			codigoExtendido.save()

			mensaje= "codigo extendido con exito"
		else:
			mensaje= 1
	return HttpResponse(
            json.dumps(mensaje),
            content_type="application/json"
        )


def codigosAntiguos(request):

	correo= request.session.get('correo')
	code_id= request.session.get('code_id')

	codigo = CodigoQr.objects.get(id=code_id)


	na = codigo.hashPrivado
	nc = codigo.hashVerificacion
	nb = nc / (na*727)

	pub = hl.sha512()
	pub.update(str(nb).encode('utf8'))
	dpub = pub.hexdigest()
	dpub = b64.b64encode(dpub.encode('utf8')).decode('utf8')



	usuarioCount = Usuario.objects.filter(correo=correo)
	listaCodigo = []
	if(len(usuarioCount)>0):
		usuario = Usuario.objects.get(correo=correo)
		codigos = CodigoUsuario.objects.filter(usuario_id=usuario.id)

		for r in codigos:
			codigo= CodigoQr.objects.get(id=r.codigoqr_id)
			if(codigo):
				fecha = str(codigo.fecha_modificacion)
				fecha2 = str(codigo.fecha_expiracion)
				listaCodigo.append([str(codigo.id),fecha[0:10],fecha2[0:10]])

	respuesta= [code_id,dpub]

	return HttpResponse(
            json.dumps(respuesta),
            content_type="application/json"
        )


def administracion(request):
	#muestra  el template de administracion y envia los codigos pertenecientes al usuario
	correo= request.session.get('correo')
	usuarioCount = Usuario.objects.filter(correo=correo)
	listaCodigo = []
	if "code_id" in request.session:
		if "code_admin" in request.session:
			if(request.session.get('code_id')==request.session.get('code_admin')):
				code_id = request.session.get('code_id')
				code_hash = request.session.get('code_hash')
				request.session['code_admin'] = code_id
				request.session['hash_admin'] = code_hash
				request.session['correo_admin'] = request.session.get('correo')

			elif(request.session.get('code_admin')==""):
				code_id = request.session.get('code_id')
				code_hash = request.session.get('code_hash')
			elif(request.session.get('code_id')==""):
				code_id = request.session.get('code_admin')
				code_hash = request.session.get('hash_admin')
				request.session['correo'] = request.session.get('correo_admin')
				request.session['code_id'] = request.session.get('code_admin')
				request.session['code_hash'] = request.session.get('hash_admin')
			else:
				code_id = request.session.get('code_id')
				code_hash = request.session.get('code_hash')
				request.session['code_admin'] = code_id
				request.session['hash_admin'] = code_hash
				request.session['correo_admin'] = request.session.get('correo')
				
		else:
			code_id = request.session.get('code_id')
			code_hash = request.session.get('code_hash')
			request.session['code_admin'] = code_id
			request.session['hash_admin'] = code_hash
			request.session['correo_admin'] = request.session.get('correo')
	else:
		code_id="";
		code_hash="";





	opciones ="";
	if(len(usuarioCount)>0):
		#busca el usuario perteneciente al correo
		usuario = Usuario.objects.get(correo=correo)
		##codigos = CodigoUsuario.objects.filter(usuario_id=usuario.id)

		#busca los codigos pertenecientes al usuario


		usu = Usuario.objects.filter(correo= correo)
		if(len(usu)>0):
			usuario = Usuario.objects.get(correo= correo)
			codigosUsu = CodigoUsuario.objects.filter(usuario_id= usuario.id).order_by('codigoqr__estado','codigoqr__fecha_modificacion')


			if(len(codigosUsu)>0):

				listaCodigo=[]
				for i in codigosUsu:

					codigo= CodigoQr.objects.get(id=i.codigoqr_id)

					if(codigo):
						fecha = str(codigo.fecha_modificacion)
						fecha2 = str(codigo.fecha_expiracion)
						na= codigo.hashPrivado
						hash_privado = b64.b64encode(str(na).encode('utf8')).decode('utf8')
						ultimos = hash_privado[-10:]
						pin = ultimos[:6]
						pin = pin.upper()
						listaCodigo.append([str(codigo.id),fecha[0:10],fecha2[0:10], str(codigo.estado), str(pin)])






	#busca las opciones del codigo actual

	if(code_id==""):
		code_id=0
	codigos= CodigoQr.objects.filter(id=str(code_id))
	if(len(codigos)>0):
		codigoActual= CodigoQr.objects.get(id=str(code_id))
		opciones = codigoActual.opciones
		estado= codigoActual.estado
		estadoCodigo=""
		if(int(estado)>0):
			estadoCodigo="grabado"
	else:
		estadoCodigo="grabado"
	template = loader.get_template('main/administrar.html')
	context = RequestContext(request, {
	'listaCodigo':listaCodigo,
	'code_id': code_id,
	'code_hash': code_hash,
	'opciones': opciones,
	'estado': estadoCodigo,
	'tema': "admin",


    })
	return HttpResponse(template.render(context))



def adminPage(request):
	#muestra  el template de administracion y envia los codigos pertenecientes al usuario
	correo= request.session.get('correo')
	usuarioCount = Usuario.objects.filter(correo=correo)
	listaCodigo = []
	code_id = request.session.get('code_id')
	code_hash = request.session.get('code_hash')

	opciones ="";
	if(len(usuarioCount)>0):
		#busca el usuario perteneciente al correo
		usuario = Usuario.objects.get(correo=correo)
		##codigos = CodigoUsuario.objects.filter(usuario_id=usuario.id)

		#busca los codigos pertenecientes al usuario
		usu = Usuario.objects.filter(correo= correo)
		if(len(usu)>0):
			usuario = Usuario.objects.get(correo= correo)
			codigosUsu = CodigoUsuario.objects.filter(usuario_id= usuario.id).order_by('codigoqr__estado','codigoqr__fecha_modificacion')


			if(len(codigosUsu)>0):

				listaCodigo=[]
				for i in codigosUsu:

					codigo= CodigoQr.objects.get(id=i.codigoqr_id)

					if(codigo):
						fecha = str(codigo.fecha_modificacion)
						fecha2 = str(codigo.fecha_expiracion)
						na= codigo.hashPrivado
						hash_privado = b64.b64encode(str(na).encode('utf8')).decode('utf8')
						ultimos = hash_privado[-10:]
						pin = ultimos[:6]
						pin = pin.upper()
						listaCodigo.append([str(codigo.id),fecha[0:10],fecha2[0:10], str(codigo.estado), str(pin)])


	estadoCodigo=""

	template = loader.get_template('main/adminPage.html')
	context = RequestContext(request, {
	'listaCodigo':listaCodigo,
	'code_id': code_id,
	'code_hash': code_hash,
	'opciones': opciones,
	'estado': estadoCodigo,
	'tema': "admin",


    })
	return HttpResponse(template.render(context))



def loginMultimedia(request):
	#hace el login del usuario en la multimedia

	correo = request.POST.get('correoLogin')
	contrasena = request.POST.get('contrasenaLogin')
	qr_id = request.POST.get('qr_id')
	usuarioCount = Usuario.objects.filter(correo=correo)
	cor=""
	if(len(usuarioCount)==0):
		mensaje= 1 #usuario no registrado
	else:
		usuario = Usuario.objects.get(correo=correo)
		contrasena = hl.sha512(contrasena.encode('utf-8')).hexdigest()
		#verificacion deocntraseña
		if(usuario.contrasena==contrasena):


			if(usuario.estado=="A"):
				request.session['correo'] = correo

				mensaje= 3 #usuario activo
			else:
				mensaje = 4 #usuario para cambio de contraseña
				cor= correo
		else:
			mensaje=2 #contraseña incorrecta
	respuesta= [mensaje,cor]

	return HttpResponse(
            json.dumps(respuesta),
            content_type="application/json"
        )

def loginPage(request):
	#hace el login del usuario en la multimedia
	correo = request.POST.get('correoLogin')
	contrasena = request.POST.get('contrasenaLogin')
	qr_id = request.POST.get('qr_id')
	usuarioCount = Usuario.objects.filter(correo=correo)
	cor=""
	if(len(usuarioCount)==0):
		mensaje= 1 #usuario no registrado
	else:
		usuario = Usuario.objects.get(correo=correo)
		contrasena = hl.sha512(contrasena.encode('utf-8')).hexdigest()
		#verificacion deocntraseña
		if(usuario.contrasena==contrasena):


			if(usuario.estado=="A"):
				request.session['correo'] = correo

				mensaje= 3 #usuario activo
			else:
				mensaje = 4 #usuario para cambio de contraseña
				cor= correo
		else:
			mensaje=2 #contraseña incorrecta
	respuesta= [mensaje,cor]

	return HttpResponse(
            json.dumps(respuesta),
            content_type="application/json"
        )


def cerrarMultimedia(request):
	#cerrar sesion de multimedia
	request.session['correo'] = ""
	request.session['code_id'] = ""
	request.session['code_hash'] = ""

	mensaje= 1


	return HttpResponse(
            json.dumps(mensaje),
            content_type="application/json"
        )
def recuperarCorreo(request):
	#mensaje de recuperacion de correo
	from_email = request.POST.get('correoRecuperacion')
	subject = ("Mensaje de Recuperacion de contraseña de  Gift Card")

	usuarios = Usuario.objects.filter(correo=from_email)
	if(len(usuarios)>0):
		#se crea una nueva contraseña
		usuario = Usuario.objects.get(correo=from_email)
		a = int(random.randint(3,5*23))
		b = int(random.randint(5,3*25))
		c = int(random.randint(2,4*10))
		e = int(random.randint(6,4*17))
		d= int((((a*c)*(b*e))/a*e))

		#actualizacion de contraseña en la base de datos
		contrasena = b64.b64encode(str(d).encode('utf8')).decode('utf8')
		contra = hl.sha512(contrasena.encode('utf-8')).hexdigest()
		usuario.contrasena= contra
		usuario.estado="R"
		usuario.save()
		message = ("Ingresa de nuevo con tu Contrasena recuperada:  " +str(contrasena))

		if subject and message and from_email:
			try:
				#envio de mensaje con la nueva contraseña al correo
				email = EmailMessage(subject, message, to=[from_email])
				email.send()

			except BadHeaderError:
				mensaje= 1
			mensaje= 2
		else:

			mensaje=3
	else:
		mensaje= 4
	return HttpResponse(
            json.dumps(mensaje),
            content_type="application/json"
        )


def multimediaRTC(request):
	#carga los templates que permite grabar la multimedia y ver lo grabado
	code_id = request.GET.get('id')
	code_hash = request.GET.get('hash')



	if "code_id" in request.session:
		if(code_id!= request.session['code_id']):
			request.session['correo'] = ""


	else:
		request.session['correo'] = ""

	request.session['code_id'] = code_id
	request.session['code_hash'] = code_hash
	#verifica si el codigoqr existe
	codigoqr = CodigoQr.objects.filter(id=code_id)
	tema=""
	codigoTemaCount = CodigoTema.objects.filter(codigo_id=code_id).count()
	if(codigoTemaCount > 0):
		codigoTema = CodigoTema.objects.get(codigo_id=code_id)
		tema= Tema.objects.get(id=codigoTema.tema_id).codigo

	marco=""
	marcoSRC=""

	codigoMarcoCount = CodigoMarco.objects.filter(codigo_id=code_id).count()
	if(codigoMarcoCount > 0):
		codigoMarco = CodigoMarco.objects.get(codigo_id=code_id)
		marco= codigoMarco.marco_id
		marcoSRC= Marco.objects.get(id=marco).enlace



	if(len(codigoqr)==0):
		mensaje= "Codigo Qr no valido"

		template = loader.get_template('main/mensajeCodigo.html')
		context = RequestContext(request, {
				'base2': BASE2,
				'mensaje': mensaje,
				'tema': "admin",
			})
			#envia al template
		return HttpResponse(template.render(context))



	#busca el hash del codigo qr
	codigo = CodigoQr.objects.get(id=code_id)


	na = codigo.hashPrivado
	nc = codigo.hashVerificacion
	nb = nc / (na*727)

	pub = hl.sha512()
	pub.update(str(nb).encode('utf8'))
	dpub = pub.hexdigest()
	dpub = b64.b64encode(dpub.encode('utf8')).decode('utf8')

	#verifica si los hash son correctos
	if(code_hash != dpub or codigo.estado =="3" or codigo.estado =="4" or codigo.estado =="5"):
		if(code_hash != dpub):

			mensaje = "Codigo Qr no valido"

		#verifica los estado del codigo
		if(codigo.estado =="3" ):

			mensaje= "Codigo Expirado."

		if(codigo.estado =="4" ):

			mensaje= "Codigo Usado para extender Tiempo."

		if(codigo.estado =="5" ):

			mensaje= "Mensaje Eliminado."

		template = loader.get_template('main/mensajeCodigo.html')
		context = RequestContext(request, {
				'base2': BASE2,
				'mensaje': mensaje,
				'tema': "admin",
			})
			#envia al template
		return HttpResponse(template.render(context))


	if(codigo.estado=="0"):
		#si tien estado creado procede a enviarlo al template de grabarMultimedia


		model = MultimediaQr
		template = loader.get_template('main/grabarMultimediaRTC.html')
		#busca las categorias de plantillas
		plantillas = Plantilla.objects.values('categoria_id').annotate(dcount=Count('categoria_id'))


		categoria = Categoria.objects.filter(codigocategoria__codigo_id=code_id)
		categorias=[]
		if(len(categoria)>0):
			for r in categoria:
				planti = Plantilla.objects.filter(categoria_id= r.id)
				if(len(planti)>0):
					categorias.append([r.id,r.nombre])



		if (len(categorias)==0):
			categorias.append([0,"No hay plantillas disponibles"])

		#verifica si hay una sesion iniciada
		correo= request.session.get('correo')

		if(correo!="" ):
			session=1
		else:
			session=0

		pla=""
		can=""
		men=""
		vid=""
		img=""
		lib=""

		#verifica las opciones que tiene habilitadas para grabar
		if(len(codigo.opciones)>0):

			for i in range(0,len(codigo.opciones)):
				if(codigo.opciones[i]=="P"):
					pla="P"
				elif(codigo.opciones[i]=="C"):
					can="C"
				elif(codigo.opciones[i]=="M"):
					men="M"
				elif(codigo.opciones[i]=="V"):
					vid="V"
				elif(codigo.opciones[i]=="I"):
					img="I"
				elif(codigo.opciones[i]=="L"):
					lib="L"
				else:
					pla=""
					can=""
					men=""
					vid=""
					img=""
					lib=""
		else:
			pla=""
			can=""
			men=""
			vid=""
			img=""
			lib=""
		imagenInicial=""
		if(img != ""):
			codigoImagen = CodigoImagen.objects.get(codigo_id=code_id)
			imagenInicial = (ImagenInicial.objects.get(id=codigoImagen.imagen_id)).url

		marcos = Marco.objects.filter().order_by('-defecto','nombre')
		diriOS= "/main/multimediaiOS/?id="+code_id+"&hash="+code_hash
		temas = Tema.objects.filter().order_by('-defecto','nombre')
		context = RequestContext(request, {
			'categorias': categorias,
			'qr_id': code_id,
			'qr_hash': code_hash,
			'session': session,
			'opciones': codigo.opciones,
			'pla':pla,
			'can':can,
			'men':men,
			'vid':vid,
			'img':img,
			'lib':lib,
			'BASE2':BASE2,
			'diriOS':diriOS,
			'temas':temas,
			'tema': tema,
			'marcos': marcos,
			'marco': marco,

			'imagenInicial': imagenInicial,
		})
		#envia al template
		return HttpResponse(template.render(context))

	elif(codigo.estado=="1" or codigo.estado=="2"):
		#si el estado es mayor a 0 es porque ya se grabo un mensaje por ello se envia al template de verPlantilla

		expir = str(codigo.fecha_expiracion)
		expir = expir[:19]
		expiracion = datetime.strptime(expir, "%Y-%m-%d %H:%M:%S")

		#verifia si ya esta expirado
		timezone.activate(pytz.timezone("America/Bogota"))
		fecha = str(timezone.localtime(timezone.now()))
		fechaAc = fecha[0:18]

		modi = str(codigo.fecha_modificacion)
		modi = modi[:19]
		modifi = datetime.strptime(modi, "%Y-%m-%d %H:%M:%S")
		hoy = datetime.strptime(fechaAc, "%Y-%m-%d %H:%M:%S")

		if(hoy> expiracion ):
			#codigo.estado="3"
			#codigo.save()
			return HttpResponse("Codigo Expirado")

		#busca la multimedia almacenada previamente
		srcVideo=""
		srcPlantilla=""
		mensaje=""
		urlMusica=""
		imagenInicial=""
		imgLibre=""
		posicionImagen=0
		multimediaqr = MultimediaQr.objects.filter(codigoqr_id=code_id)
		mensajeqr = QrMensaje.objects.filter(codigoqr_id=code_id)
		qrplantilla = QrPlantilla.objects.filter(codigoqr_id=code_id)
		codigoimagen = CodigoImagen.objects.filter(codigo_id=code_id)
		codigoimglibre = CodigoImgLibre.objects.filter(codigoqr_id=code_id)
		if(len(multimediaqr) > 0):
			multimediaqr = MultimediaQr.objects.get(codigoqr_id=code_id)
			srcVideo= multimediaqr.video
			srcVideo= BASE3+"/pool/"+str(srcVideo)
		if(len(mensajeqr) > 0):
			mensajeqr = QrMensaje.objects.get(codigoqr_id=code_id)
			mensaje= mensajeqr.mensaje
			urlMusica= mensajeqr.urlMusica

		if(len(qrplantilla) > 0):
			qrplantilla = QrPlantilla.objects.get(codigoqr_id=code_id)
			plantilla = Plantilla.objects.filter(id=qrplantilla.plantilla_id)
			if(len(plantilla) > 0):
				plantilla = Plantilla.objects.get(id=qrplantilla.plantilla_id)
				srcPlantilla= plantilla.url
		if(len(codigoimagen) > 0):
			codeimagen = CodigoImagen.objects.get(codigo_id=code_id)
			imagen = ImagenInicial.objects.get(id=codeimagen.imagen_id)
			imagenInicial= imagen.url


		if(len(codigoimglibre) > 0):
			codeimglibre = CodigoImgLibre.objects.get(codigoqr_id=code_id)
			imgLibre = BASE3+"/pool/"+str(codeimglibre.imagen)
			posicionImagen= codeimglibre.posicion

		if(codigo.estado=="1"):
			#actualiza el estado a codigoqr visto
			timezone.activate(pytz.timezone("America/Bogota"))
			fecha = str(timezone.localtime(timezone.now()))
			fechaActualizacion = fecha[0:18]
			codigoqr = CodigoQr.objects.get(id=code_id)
			codigoqr.estado = "2"
			codigoqr.save()

		template = loader.get_template('main/verPlantilla.html')

		#modifica la url para ser compartida
		url= BASE2+"/main/compartir/"
		datos= "id="+code_id+"&hash="+code_hash
		enlace= str(url)+"/"+code_id+"/"+code_hash

		i= ((len(code_hash))/2)-5
		j= ((len(code_hash))/2)+5

		inicio= code_hash[0:10]
		mitad= code_hash[int(i):int(j)]
		fin = code_hash[-10:]
		code_hash= str(inicio)+str(mitad)+str(fin)
		compartirEnlace= str(url)+code_id+"/"+code_hash

		vm=""
		vv=""
		vp=""
		um=""
		vi=""
		vl=""
		#verifica cuales opciones han sido almacenadas
		if(mensaje!="" or urlMusica!=""):
			vm=1
		if(srcVideo!=""):
			vv=1
		if(srcPlantilla!=""):
			vp=1
		if(urlMusica!=""):
			um=1
		if(imagenInicial!=""):
			vi=1
		if(imgLibre!=""):
			vl=1

		arcVideo= "";

		multimedia = MultimediaQr.objects.filter(codigoqr_id=code_id)

		if(len(multimedia)>0):
			tempo1 = os.path.isfile("/tmp/v_"+code_id+".mp4")
			tempo2 = os.path.isfile("/tmp/"+code_id+".mp4")

			if(tempo1 == False and tempo2 == False):
				pool = os.path.isfile(BASE5+code_id+".mp4")

				if(pool== True):
					arcVideo=1
				else:
					arcVideo=""

			else:
				arcVideo=""


		hash_privado = b64.b64encode(str(na).encode('utf8')).decode('utf8')
		ultimos = hash_privado[-10:]
		pin = ultimos[:6]
		pin = pin.upper()

		timezone.activate(pytz.timezone("America/Bogota"))
		fecha = str(timezone.localtime(timezone.now()))
		fechaAc = fecha[0:18]

		modi = str(codigo.fecha_modificacion)
		modi = modi[:19]
		modifi = datetime.strptime(modi, "%Y-%m-%d %H:%M:%S")
		fechaAc = datetime.strptime(fechaAc, "%Y-%m-%d %H:%M:%S")

		maximo =  timedelta(minutes=30)
		modifi = modifi + maximo

		tiempo=""
		if(fechaAc > modifi):

			tiempo=1
		expira = str(codigo.fecha_expiracion)[:16]
		ano = str(codigo.fecha_expiracion)[:4]
		mes = str(codigo.fecha_expiracion)[5:7]
		dia = str(codigo.fecha_expiracion)[8:10]

		ano2 = str(fechaAc)[:4]
		mes2 = str(fechaAc)[5:7]
		dia2 = str(fechaAc)[8:10]

		fecha1 = datetime(int(ano2),int(mes2),int(dia2))   # Asigna datetime de la fecha actual
		fecha2 = datetime(int(ano),int(mes),int(dia))  # Asigna datetime específica
		diasRes = fecha2 - fecha1
		dias=""
		diasRes = str(diasRes)
		if "days" in diasRes:
			position = diasRes.find(",");
			dias = diasRes[:position]
			dias = dias.replace("days","")
		else:
			dias = "0"

		print(imgLibre)
		print(vl)
		print(posicionImagen)
		context = RequestContext(request, {
			'srcVideo': srcVideo,
			'srcPlantilla': srcPlantilla,
			'url': url,
			'code': code_id,
			'hash': code_hash,
			'datos': datos,
			'enlace':enlace,
			'mensaje': mensaje,
			'urlMusica': urlMusica,
			'vm':vm,
			'vv':vv,
			'vp':vp,
			'um':um,
			'vi':vi,
			'vl':vl,
			'imgLibre': imgLibre,
			'posicionImagen': posicionImagen,
			'compartirEnlace':compartirEnlace,
			'arcVideo': arcVideo,
			'pin': pin,
			'tiempo': tiempo,
			'tema': tema,
			'marcoSRC': marcoSRC,
			'imagenInicial': imagenInicial,
			'expiracion': expira,
			'diasRestantes': dias,

		})


		#envia informacion
		return HttpResponse(template.render(context))


def multimediaiOS(request):
	#carga los templates que permite grabar la multimedia y ver lo grabado
	code_id = request.GET.get('id')
	code_hash = request.GET.get('hash')



	if "code_id" in request.session:
		if(code_id!= request.session['code_id']):
			request.session['correo'] = ""


	else:
		request.session['correo'] = ""

	request.session['code_id'] = code_id
	request.session['code_hash'] = code_hash
	#verifica si el codigoqr existe
	codigoqr = CodigoQr.objects.filter(id=code_id)
	tema=""
	codigoTemaCount = CodigoTema.objects.filter(codigo_id=code_id).count()
	if(codigoTemaCount > 0):
		codigoTema = CodigoTema.objects.get(codigo_id=code_id)
		tema= Tema.objects.get(id=codigoTema.tema_id).codigo

	marco=""
	marcoSRC=""

	codigoMarcoCount = CodigoMarco.objects.filter(codigo_id=code_id).count()
	if(codigoMarcoCount > 0):
		codigoMarco = CodigoMarco.objects.get(codigo_id=code_id)
		marco= codigoMarco.marco_id
		marcoSRC= Marco.objects.get(id=marco).enlace



	if(len(codigoqr)==0):

		mensaje= "Codigo Qr no valido"

		template = loader.get_template('main/mensajeCodigo.html')
		context = RequestContext(request, {
				'base2': BASE2,
				'mensaje': mensaje,
				'tema': "admin",
			})
			#envia al template
		return HttpResponse(template.render(context))



	#busca el hash del codigo qr
	codigo = CodigoQr.objects.get(id=code_id)


	na = codigo.hashPrivado
	nc = codigo.hashVerificacion
	nb = nc / (na*727)

	pub = hl.sha512()
	pub.update(str(nb).encode('utf8'))
	dpub = pub.hexdigest()
	dpub = b64.b64encode(dpub.encode('utf8')).decode('utf8')

	#verifica si los hash son correctos

	if(code_hash != dpub or codigo.estado =="3" or codigo.estado =="4" or codigo.estado =="5"):
		if(code_hash != dpub):

			mensaje = "Codigo Qr no valido"

		#verifica los estado del codigo
		if(codigo.estado =="3" ):

			mensaje= "Codigo Expirado."

		if(codigo.estado =="4" ):

			mensaje= "Codigo Usado para extender Tiempo."

		if(codigo.estado =="5" ):

			mensaje= "Mensaje Eliminado."

		template = loader.get_template('main/mensajeCodigo.html')
		context = RequestContext(request, {
				'base2': BASE2,
				'mensaje': mensaje,
				'tema': "admin",
			})
			#envia al template
		return HttpResponse(template.render(context))

	if(codigo.estado=="0"):
		#si tien estado creado procede a enviarlo al template de grabarMultimedia

		model = MultimediaQr
		template = loader.get_template('main/grabarMultimediaiOS.html')
		#busca las categorias de plantillas
		plantillas = Plantilla.objects.values('categoria_id').annotate(dcount=Count('categoria_id'))
		categoria = Categoria.objects.filter(codigocategoria__codigo_id=code_id)
		categorias=[]
		if(len(categoria)>0):
			for r in categoria:
				planti = Plantilla.objects.filter(categoria_id= r.id)
				if(len(planti)>0):
					categorias.append([r.id,r.nombre])


		if (len(categorias)==0):
			categorias.append([0,"No hay plantillas disponibles"])

		#verifica si hay una sesion iniciada
		correo= request.session.get('correo')

		if(correo!="" ):
			session=1
		else:
			session=0

		pla=""
		can=""
		men=""
		vid=""
		img=""
		lib=""

		#verifica las opciones que tiene habilitadas para grabar
		if(len(codigo.opciones)>0):

			for i in range(0,len(codigo.opciones)):
				if(codigo.opciones[i]=="P"):
					pla="P"
				elif(codigo.opciones[i]=="C"):
					can="C"
				elif(codigo.opciones[i]=="M"):
					men="M"
				elif(codigo.opciones[i]=="V"):
					vid="V"
				elif(codigo.opciones[i]=="I"):
					img="V"
				elif(codigo.opciones[i]=="L"):
					lib="L"
				else:
					pla=""
					can=""
					men=""
					vid=""
					img=""
					lib=""
		else:
			pla=""
			can=""
			men=""
			vid=""
			img=""
			lib=""

		imagenInicial=""
		if(img != ""):
			codigoImagen = CodigoImagen.objects.get(codigo_id=code_id)
			imagenInicial = (ImagenInicial.objects.get(id=codigoImagen.imagen_id)).url

		temas = Tema.objects.filter().order_by('-defecto','nombre')
		marcos = Marco.objects.filter().order_by('-defecto','nombre')
		print(codigo.opciones)
		context = RequestContext(request, {
			'categorias': categorias,
			'qr_id': code_id,
			'qr_hash': code_hash,
			'session': session,
			'opciones': codigo.opciones,
			'pla':pla,
			'can':can,
			'men':men,
			'img':img,
			'lib':lib,
			'BASE2':BASE2,
			'vid':vid,
			'temas': temas,
			'tema': tema,
			'marco': marco,
			'marcos': marcos,
			'imagenInicial': imagenInicial,
		})
		#envia al template
		return HttpResponse(template.render(context))
	elif(codigo.estado=="1" or codigo.estado=="2"):
		#si el estado es mayor a 0 es porque ya se grabo un mensaje por ello se envia al template de verPlantilla

		expir = str(codigo.fecha_expiracion)
		expir = expir[:19]
		expiracion = datetime.strptime(expir, "%Y-%m-%d %H:%M:%S")

		#verifia si ya esta expirado
		timezone.activate(pytz.timezone("America/Bogota"))
		fecha = str(timezone.localtime(timezone.now()))
		fechaAc = fecha[0:18]

		modi = str(codigo.fecha_modificacion)
		modi = modi[:19]
		modifi = datetime.strptime(modi, "%Y-%m-%d %H:%M:%S")
		hoy = datetime.strptime(fechaAc, "%Y-%m-%d %H:%M:%S")


		#verifia si ya esta expirado
		if(hoy > expiracion ):
			#codigo.estado="3"
			#codigo.save()
			return HttpResponse("Codigo Expirado")

		#busca la multimedia almacenada previamente
		srcVideo=""
		srcPlantilla=""
		mensaje=""
		urlMusica=""
		imagenInicial=""
		imgLibre=""
		posicionImagen=0
		multimediaqr = MultimediaQr.objects.filter(codigoqr_id=code_id)
		mensajeqr = QrMensaje.objects.filter(codigoqr_id=code_id)
		qrplantilla = QrPlantilla.objects.filter(codigoqr_id=code_id)
		codigoimglibre = CodigoImgLibre.objects.filter(codigoqr_id=code_id)
		if(len(multimediaqr) > 0):
			multimediaqr = MultimediaQr.objects.get(codigoqr_id=code_id)
			srcVideo= multimediaqr.video
			srcVideo= BASE3+"/pool/"+str(srcVideo)
		if(len(mensajeqr) > 0):
			mensajeqr = QrMensaje.objects.get(codigoqr_id=code_id)
			mensaje= mensajeqr.mensaje
			urlMusica= mensajeqr.urlMusica

		if(len(qrplantilla) > 0):
			qrplantilla = QrPlantilla.objects.get(codigoqr_id=code_id)
			plantilla = Plantilla.objects.filter(id=qrplantilla.plantilla_id)
			if(len(plantilla) > 0):
				plantilla = Plantilla.objects.get(id=qrplantilla.plantilla_id)
				srcPlantilla= plantilla.url
		codigoimagen = CodigoImagen.objects.filter(codigo_id=code_id)
		if(len(codigoimagen) > 0):
			codeimagen = CodigoImagen.objects.get(codigo_id=code_id)
			imagen = ImagenInicial.objects.get(id=codeimagen.imagen_id)
			imagenInicial= imagen.url


		if(len(codigoimglibre) > 0):
			codeimglibre = CodigoImgLibre.objects.get(codigoqr_id=code_id)
			imgLibre = BASE3+"/pool/"+str(codeimglibre.imagen)
			posicionImagen= codeimglibre.posicion


		if(codigo.estado=="1"):
			#actualiza el estado a codigoqr visto
			timezone.activate(pytz.timezone("America/Bogota"))
			fecha = str(timezone.localtime(timezone.now()))
			fechaActualizacion = fecha[0:18]
			codigoqr = CodigoQr.objects.get(id=code_id)
			codigoqr.estado = "2"
			codigoqr.save()

		template = loader.get_template('main/verPlantilla.html')

		#modifica la url para ser compartida
		url= BASE2+"/main/compartir/"
		datos= "id="+code_id+"&hash="+code_hash
		enlace= str(url)+"/"+code_id+"/"+code_hash

		i= ((len(code_hash))/2)-5
		j= ((len(code_hash))/2)+5

		inicio= code_hash[0:10]
		mitad= code_hash[int(i):int(j)]
		fin = code_hash[-10:]
		code_hash= str(inicio)+str(mitad)+str(fin)
		compartirEnlace= str(url)+code_id+"/"+code_hash

		vm=""
		vv=""
		vp=""
		um=""
		vi=""
		vl=""
		#verifica cuales opciones han sido almacenadas
		if(mensaje!="" or urlMusica!=""):
			vm=1
		if(srcVideo!=""):
			vv=1
		if(srcPlantilla!=""):
			vp=1
		if(urlMusica!=""):
			um=1
		if(imagenInicial!=""):
			vi=1
		if(imgLibre!=""):
			vl=1


		arcVideo= "";

		multimedia = MultimediaQr.objects.filter(codigoqr_id=code_id)

		if(len(multimedia)>0):
			tempo1 = os.path.isfile("/tmp/v_"+code_id+".mp4")
			tempo2 = os.path.isfile("/tmp/"+code_id+".mp4")

			if(tempo1 == False and tempo2 == False):
				pool = os.path.isfile(BASE5+code_id+".mp4")

				if(pool== True):
					arcVideo=1
				else:
					arcVideo=""

			else:
				arcVideo=""


		hash_privado = b64.b64encode(str(na).encode('utf8')).decode('utf8')
		ultimos = hash_privado[-10:]
		pin = ultimos[:6]
		pin = pin.upper()

		timezone.activate(pytz.timezone("America/Bogota"))
		fecha = str(timezone.localtime(timezone.now()))
		fechaAc = fecha[0:18]

		modi = str(codigo.fecha_modificacion)
		modi = modi[:19]
		modifi = datetime.strptime(modi, "%Y-%m-%d %H:%M:%S")
		fechaAc = datetime.strptime(fechaAc, "%Y-%m-%d %H:%M:%S")

		maximo =  timedelta(minutes=30)
		modifi = modifi + maximo

		tiempo=""
		if(fechaAc > modifi):

			tiempo=1

		expira = str(codigo.fecha_expiracion)[:16]
		ano = str(codigo.fecha_expiracion)[:4]
		mes = str(codigo.fecha_expiracion)[5:7]
		dia = str(codigo.fecha_expiracion)[8:10]

		ano2 = str(fechaAc)[:4]
		mes2 = str(fechaAc)[5:7]
		dia2 = str(fechaAc)[8:10]

		fecha1 = datetime(int(ano2),int(mes2),int(dia2))   # Asigna datetime de la fecha actual
		fecha2 = datetime(int(ano),int(mes),int(dia))  # Asigna datetime específica
		diasRes = fecha2 - fecha1
		dias=""
		diasRes = str(diasRes)
		if "days" in diasRes:
			position = diasRes.find(",");
			dias = diasRes[:position]
			dias = dias.replace("days","")
		else:
			dias = "0"



		context = RequestContext(request, {
			'srcVideo': srcVideo,
			'srcPlantilla': srcPlantilla,
			'url': url,
			'code': code_id,
			'hash': code_hash,
			'datos': datos,
			'enlace':enlace,
			'mensaje': mensaje,
			'urlMusica': urlMusica,
			'imagenInicial': imagenInicial,
			'imgLibre': imgLibre,
			'posicionImagen': posicionImagen,
			'vm':vm,
			'vv':vv,
			'vp':vp,
			'um':um,
			'vi':vi,
			'vl':vl,
			'compartirEnlace':compartirEnlace,
			'arcVideo': arcVideo,
			'pin': pin,
			'tiempo': tiempo,
			'tema': tema,
			'marcoSRC': marcoSRC,
			'expiracion': expira,
			'diasRestantes': dias,

		})


		#envia informacion
		return HttpResponse(template.render(context))


def multimediaView(request):
	#carga los templates que permite grabar la multimedia y ver lo grabado
	code_id = request.GET.get('id')
	code_hash = request.GET.get('hash')

	template = loader.get_template('main/validarMultimedia.html')


	context = RequestContext(request, {

		'qr_id': code_id,
		'qr_hash': code_hash,

	})
	#envia al template
	return HttpResponse(template.render(context))


@csrf_exempt
def confirmarView(request):
	#es la misma vista de multimedia, se realizo para que el usuario que almacena el video lo vea sin alterar su estado
	code_id = request.GET.get('id')
	code_hash = request.GET.get('hash')

	codigoqr = CodigoQr.objects.filter(id=code_id)

	tema=""
	codigoTemaCount = CodigoTema.objects.filter(codigo_id=code_id).count()
	if(codigoTemaCount > 0):
		codigoTema = CodigoTema.objects.get(codigo_id=code_id)
		tema= Tema.objects.get(id=codigoTema.tema_id).codigo

	marcoSRC=""

	codigoMarcoCount = CodigoMarco.objects.filter(codigo_id=code_id).count()
	if(codigoMarcoCount > 0):
		codigoMarco = CodigoMarco.objects.get(codigo_id=code_id)
		marco= codigoMarco.marco_id
		marcoSRC= Marco.objects.get(id=marco).enlace


	if(len(codigoqr)==0):
		enlace= "/main/multimedia/?id="+code_id+"&hash="+code_hash
		return redirect(enlace)



	codigo = CodigoQr.objects.get(id=code_id)

	na = codigo.hashPrivado
	nc = codigo.hashVerificacion
	nb = nc / (na*727)

	pub = hl.sha512()
	pub.update(str(nb).encode('utf8'))
	dpub = pub.hexdigest()
	dpub = b64.b64encode(dpub.encode('utf8')).decode('utf8')

	if(code_hash != dpub or codigo.estado =="3" or codigo.estado =="4" or codigo.estado =="5" or codigo.estado =="0"):
		enlace= "/main/multimedia/?id="+code_id+"&hash="+code_hash
		return redirect(enlace)

	elif(codigo.estado=="1" or codigo.estado=="2"):
		srcVideo=""
		srcPlantilla=""
		mensaje=""
		urlMusica=""
		imagenInicial=""
		imgLibre=""
		posicionImagen=0
		multimediaqr = MultimediaQr.objects.filter(codigoqr_id=code_id)
		mensajeqr = QrMensaje.objects.filter(codigoqr_id=code_id)
		qrplantilla = QrPlantilla.objects.filter(codigoqr_id=code_id)
		codigoimglibre = CodigoImgLibre.objects.filter(codigoqr_id=code_id)
		if(len(multimediaqr) > 0):
			multimediaqr = MultimediaQr.objects.get(codigoqr_id=code_id)
			srcVideo= multimediaqr.video
			srcVideo= BASE3+"/pool/"+str(srcVideo)
		if(len(mensajeqr) > 0):
			mensajeqr = QrMensaje.objects.get(codigoqr_id=code_id)
			mensaje= mensajeqr.mensaje
			urlMusica= mensajeqr.urlMusica

		codigoimagen = CodigoImagen.objects.filter(codigo_id=code_id)
		if(len(codigoimagen) > 0):
			codeimagen = CodigoImagen.objects.get(codigo_id=code_id)
			imagen = ImagenInicial.objects.get(id=codeimagen.imagen_id)
			imagenInicial= imagen.url


		if(len(qrplantilla) > 0):
			qrplantilla = QrPlantilla.objects.get(codigoqr_id=code_id)
			plantilla = Plantilla.objects.filter(id=qrplantilla.plantilla_id)
			if(len(plantilla) > 0):
				plantilla = Plantilla.objects.get(id=qrplantilla.plantilla_id)
				srcPlantilla= plantilla.url

		if(len(codigoimglibre) > 0):
			codeimglibre = CodigoImgLibre.objects.get(codigoqr_id=code_id)
			imgLibre = BASE3+"/pool/"+str(codeimglibre.imagen)
			posicionImagen= codeimglibre.posicion


		template = loader.get_template('main/verPlantilla.html')


		url= BASE2+"/main/compartir/"
		datos= "id="+code_id+"&hash="+code_hash
		enlace= str(url)+"/"+code_id+"/"+code_hash

		i= ((len(code_hash))/2)-5
		j= ((len(code_hash))/2)+5

		inicio= code_hash[0:10]
		mitad= code_hash[int(i):int(j)]
		fin = code_hash[-10:]
		code_hash= str(inicio)+str(mitad)+str(fin)
		compartirEnlace= str(url)+code_id+"/"+code_hash
		vm=""
		vv=""
		vp=""
		um=""
		vi=""
		vl=""
		if(mensaje!="" or urlMusica!=""):
			vm=1
		if(srcVideo!=""):
			vv=1
		if(srcPlantilla!=""):
			vp=1
		if(urlMusica!=""):
			um=1
		if(imagenInicial!=""):
			vi=1
		if(imgLibre!=""):
			vl=1

		correo= request.session.get('correo')
		if(correo!=""):
			from_var="confUsuario"
		else:
			from_var="confAnonimo"

		arcVideo= "";

		arcVideo= "";

		multimedia = MultimediaQr.objects.filter(codigoqr_id=code_id)

		if(len(multimedia)>0):
			tempo1 = os.path.isfile("/tmp/v_"+code_id+".mp4")
			tempo2 = os.path.isfile("/tmp/"+code_id+".mp4")

			if(tempo1 == False and tempo2 == False):
				pool = os.path.isfile(BASE5+code_id+".mp4")

				if(pool== True):
					arcVideo=1
				else:
					arcVideo=""

			else:
				arcVideo=""

		hash_privado = b64.b64encode(str(na).encode('utf8')).decode('utf8')
		ultimos = hash_privado[-10:]
		pin = ultimos[:6]
		pin = pin.upper()

		timezone.activate(pytz.timezone("America/Bogota"))
		fecha = str(timezone.localtime(timezone.now()))
		fechaAc = fecha[0:18]

		modi = str(codigo.fecha_modificacion)
		modi = modi[:19]
		modifi = datetime.strptime(modi, "%Y-%m-%d %H:%M:%S")
		fechaAc = datetime.strptime(fechaAc, "%Y-%m-%d %H:%M:%S")

		maximo =  timedelta(minutes=30)
		modifi = modifi + maximo

		tiempo=""
		if(fechaAc > modifi):

			tiempo=1

		expira = str(codigo.fecha_expiracion)[:16]
		ano = str(codigo.fecha_expiracion)[:4]
		mes = str(codigo.fecha_expiracion)[5:7]
		dia = str(codigo.fecha_expiracion)[8:10]

		ano2 = str(fechaAc)[:4]
		mes2 = str(fechaAc)[5:7]
		dia2 = str(fechaAc)[8:10]

		fecha1 = datetime(int(ano2),int(mes2),int(dia2))   # Asigna datetime de la fecha actual
		fecha2 = datetime(int(ano),int(mes),int(dia))  # Asigna datetime específica
		diasRes = fecha2 - fecha1
		dias=""
		diasRes = str(diasRes)
		if "days" in diasRes:
			position = diasRes.find(",");
			dias = diasRes[:position]
			dias = dias.replace("days","")
		else:
			dias = "0"



		context = RequestContext(request, {
			'srcVideo': srcVideo,
			'srcPlantilla': srcPlantilla,
			'url': url,
			'code': code_id,
			'hash': code_hash,
			'datos': datos,
			'enlace':enlace,
			'mensaje': mensaje,
			'urlMusica': urlMusica,
			'imagenInicial': imagenInicial,
			'posicionImagen': posicionImagen,
			'imgLibre': imgLibre,
			'vm':vm,
			'vv':vv,
			'vi':vi,
			'vl':vl,
			'vp':vp,
			'um':um,
			'from': from_var,
			'compartirEnlace': compartirEnlace,
			'arcVideo': arcVideo,
			'pin': pin,
			'tiempo': tiempo,
			'tema': tema,
			'marcoSRC': marcoSRC,
			'expiracion': expira,
			'diasRestantes': dias,

		})

		return HttpResponse(template.render(context))
def compartir(request,code_id,code_hash):
	#opcion de compartir
	#verifica  la url acortada y lo redirecciona a la multimedia
	codigos = CodigoQr.objects.filter(id=code_id)
	if(len(codigos)>0):
		codigo = CodigoQr.objects.get(id=code_id)
		na = codigo.hashPrivado
		nc = codigo.hashVerificacion
		nb = nc / (na*727)

		pub = hl.sha512()
		pub.update(str(nb).encode('utf8'))
		dpub = pub.hexdigest()
		dpub = b64.b64encode(dpub.encode('utf8')).decode('utf8')

		i= ((len(dpub))/2)-5
		j= ((len(dpub))/2)+5

		inicio= dpub[0:10]
		mitad= dpub[int(i):int(j)]
		fin = dpub[-10:]
		code_db= str(inicio)+str(mitad)+str(fin)

		if(code_hash==code_db):

			enlace= "/main/multimedia/?id="+code_id+"&hash="+dpub
			return redirect(enlace)
		else:
			return HttpResponse("CODIGO INCORRECTO")
	else:
		return HttpResponse("CODIGO INCORRECTO")




def send_mail(request):
	#envia email con la url de la multimedia almacenada
	datos = request.POST.get('datos')
	enlace = request.POST.get('enlace')
	code = request.POST.get('code')
	mensaje=""
	codigos = QrMensaje.objects.filter(codigoqr_id=code)
	if(len(codigos)>0):
		mensa = QrMensaje.objects.get(codigoqr_id=code)
		mensajes = mensa.mensaje
		mensajes = mensajes.replace("</p>", "\n")
		mensajes  = re.sub('<[^<]+?>', '', mensajes)
		mensaje  = re.sub('&nbsp;', ' ', mensajes)


	else:
		mensaje="Mensaje enviado por una persona especial   "
	mensaje = mensaje+"\n"

	subject = ("Detalle Gift Card")
	message = (str(mensaje)+str(enlace))
	from_email = request.POST.get('correoDestino')
	mensaje=""


	if subject and message and from_email:
		try:
			email = EmailMessage(subject, message, to=[from_email])
			email.send()

		except BadHeaderError:
			mensaje= "vuelve a intentarlo"

		mensaje="Correo enviado Satisfactoriamente"
	else:

		mensaje="Debes ingresar un correo, vuelve a intentarlo"
	return HttpResponse(
            json.dumps(mensaje),
            content_type="application/json"
        )





def traerLista(request):

	#busca las plantillas y las envia al ajax en un directorio
	categoria=request.POST["categoria"]
	plantilla = Plantilla.objects.filter(categoria_id=categoria)

	listPlant={}
	planti= []

	for p in plantilla:
		planti.append({ "id": str(p.id), "nombre": str(p.nombre),  "url" : str(p.url), "cate" : str(p.categoria_id) })
	lisPlant= planti


	listPlant["plantilla"]= planti

	return HttpResponse(
            json.dumps(listPlant),
            content_type="application/json"
        )


def traerTema(request):

	#busca las plantillas y las envia al ajax en un directorio
	respon = json.loads(request.body.decode("utf8"))
	tema_id = respon["id"]

	temaCount = Tema.objects.filter(id=tema_id).count()
	respuesta={}
	if(temaCount > 0):
		tema = Tema.objects.get(id=tema_id)
		respuesta['id'] = tema.id
		respuesta['nombre'] = tema.nombre
		respuesta['descripcion'] = tema.descripcion
		respuesta['enlaces'] = tema.enlaces

	return HttpResponse(
            json.dumps(respuesta),
            content_type="application/json"
        )


def traerMarco(request):

	#busca las plantillas y las envia al ajax en un directorio
	respon = json.loads(request.body.decode("utf8"))
	marco_id = respon["id"]

	marcoCount = Marco.objects.filter(id=marco_id).count()
	respuesta={}
	if(marcoCount > 0):
		marco = Marco.objects.get(id=marco_id)
		respuesta['id'] = marco.id
		respuesta['nombre'] = marco.nombre
		respuesta['enlace'] = marco.enlace

	return HttpResponse(
            json.dumps(respuesta),
            content_type="application/json"
        )




def traerImagen(request):

	#busca las plantillas y las envia al ajax en un directorio
	respon = json.loads(request.body.decode("utf8"))
	imagen_id = respon["id"]

	imagenCount = ImagenInicial.objects.filter(id=imagen_id).count()
	respuesta={}
	if(imagenCount > 0):
		imagen = ImagenInicial.objects.get(id=imagen_id)
		respuesta['id'] = imagen.id
		respuesta['nombre'] = imagen.nombre
		respuesta['url'] = imagen.url


	return HttpResponse(
            json.dumps(respuesta),
            content_type="application/json"
        )



@csrf_exempt
def subirVideo(request):

	if(request.method == "POST"):

		action=request.POST["action"]

		if(action=="save"):

			upName=request.POST["upName"]
			upData=request.POST["upData"]
			count = upData.count(",")

			if(count>0):

				posicion = upData.find(",")
				upData = upData[posicion+1:]




			f = open("/tmp/"+upName, "a")
			f.write(upData)
			f.close()

			return HttpResponse(upName, content_type="application/text")
		else:
			upName=request.POST["upName"]
			spp.Popen(["python3", BASE4+"/liser.py", upName])

			return HttpResponse(upName, content_type="application/text")
	return HttpResponse("Lee el codigo Qr de nuevo")


@csrf_exempt
def subirImagen(request):

	if(request.method == "POST"):

		action=request.POST["action"]

		if(action=="save"):

			upName=request.POST["upName"]
			upData=request.POST["upData"]
			count = upData.count(",")

			if(count>0):

				posicion = upData.find(",")
				upData = upData[posicion+1:]

			print(upData)


			f = open("/tmp/"+upName, "a")
			f.write(upData)
			f.close()

			return HttpResponse(upName, content_type="application/text")
		else:
			upName=request.POST["upName"]
			print(upName)
			spp.Popen(["python3", BASE4+"/liserImg.py", upName])

			return HttpResponse(upName, content_type="application/text")
	return HttpResponse("Lee el codigo Qr de nuevo")


def guardarMultimedia(request):

	#guarda multimedia grabada y seleccionada
	if(request.method == "POST"):

		videoBlob= request.POST["videoBlob"]
		imagenBlob= request.POST["imagenBlob"]
		posicion= request.POST["posicion"]

		mensaje= request.POST["detalleForm"]
		plantilla= request.POST["idPlantilla"]
		qr_id= request.POST["qr_id"]
		urlMusica= request.POST["urlMusica"]
		tema= request.POST["tema"]
		marco= request.POST["marco"]


		if(mensaje=='<p><br data-mce-bogus="1"></p>' or mensaje == "<p>&nbsp;<br></p>"):
			mensaje=""

		multimedia = MultimediaQr.objects.filter(codigoqr_id=qr_id)
		planti = QrPlantilla.objects.filter(codigoqr_id=qr_id)
		mensa = QrMensaje.objects.filter(codigoqr_id=qr_id)
		imgLibre = CodigoImgLibre.objects.filter(codigoqr_id=qr_id)
		#valida que no se halla guardado nada previamente
		if(len(multimedia)>0):
			return HttpResponse("Ya se ha guardado un video")
		elif(len(planti)>0):
			return HttpResponse("Ya se ha guardado una plantilla")
		elif(len(mensa)>0):
			return HttpResponse("Ya se ha guardado un mensaje")
		elif(len(imgLibre)>0):
			return HttpResponse("Ya se ha guardado una Imagen")
		elif(imagenBlob=="" and videoBlob=="" and mensaje=="" and plantilla=="" and urlMusica==""):
			return HttpResponse("Debe escoger una plantilla, una cancion, escribir un mensaje o grabar un video")
		else:
			#si no se ha guardado nada y se graba o selecciono algo en la vista se procede almacenar la informacion
			if(videoBlob!=""):
				video= MultimediaQr()
				video.video = videoBlob
				video.codigoqr_id= qr_id
				video.save()
			if(imagenBlob!=""):
				imagen= CodigoImgLibre()
				imagen.imagen = imagenBlob
				imagen.posicion = posicion
				imagen.codigoqr_id= qr_id
				imagen.save()

			if(mensaje!="" or urlMusica !=""):
				mensajeqr= QrMensaje()
				mensajeqr.mensaje = mensaje
				mensajeqr.urlMusica= urlMusica
				mensajeqr.codigoqr_id= qr_id
				mensajeqr.save()

			if(plantilla!=""):
				plantillaqr= QrPlantilla()
				plantillaqr.plantilla_id = plantilla
				plantillaqr.codigoqr_id= qr_id
				plantillaqr.save()
			if(tema != ""):
				codigoTemaCount = CodigoTema.objects.filter(codigo_id=qr_id).count()
				if(codigoTemaCount >0):
					codigoTema = CodigoTema.objects.get(codigo_id=qr_id)
					codigoTema.tema_id=tema
					codigoTema.save()
				else:
					codigoTema = CodigoTema()
					codigoTema.codigo_id=qr_id
					codigoTema.tema_id=tema
					codigoTema.save()

			if(marco != ""):
				codigoMarcoCount = CodigoMarco.objects.filter(codigo_id=qr_id).count()
				if(codigoMarcoCount >0):
					codigoMarco = CodigoMarco.objects.get(codigo_id=qr_id)
					codigoMarco.marco_id=marco
					codigoMarco.save()
				else:
					codigoMarco = CodigoMarco()
					codigoMarco.codigo_id=qr_id
					codigoMarco.marco_id=marco
					codigoMarco.save()


			correo= request.session.get('correo')
			#se relaciona el codigoqr al usuario que lo esta almacenando
			if(correo!=""):
				usuario = Usuario.objects.get(correo=correo)
				codigoCount = CodigoUsuario.objects.filter(codigoqr_id=qr_id)
				if(len(codigoCount)==0):
					codigoUsuario= CodigoUsuario()
					codigoUsuario.codigoqr_id = qr_id
					codigoUsuario.usuario_id = usuario.id
					codigoUsuario.save()

				codvenCount = CodigoVendedor.objects.filter(codigo=qr_id)
				if(len(codvenCount)>0):
					vendor =  CodigoVendedor.objects.get(codigo=qr_id)
					vendedor = vendor.vendedor_id
				else:
					vendedor = 1


				vendedores = Vendedor.objects.filter(id=vendedor)
				if(len(vendedores)>0 ):
					usuvenCount = UsuarioVendedor.objects.filter(usuario=usuario.id).filter(vendedor=vendedor)
					if(len(usuvenCount)>0):
						usuarioVendedor = UsuarioVendedor.objects.get(Q(usuario=usuario.id),Q(vendedor=vendedor))
						usuarioVendedor.cantidad = usuarioVendedor.cantidad + 1
						usuarioVendedor.save()

					else:
						usuarioVendedor= UsuarioVendedor()
						usuarioVendedor.usuario_id = usuario.id
						usuarioVendedor.vendedor_id = vendedor
						usuarioVendedor.cantidad = 1
						usuarioVendedor.save()




			#se busca los dias de vigencia que tiene el codigoqr
			codigoqr = CodigoQr.objects.get(id=qr_id)
			dias = codigoqr.dias
			#se calcula el dia de hoy
			timezone.activate(pytz.timezone("America/Bogota"))
			fecha = str(timezone.localtime(timezone.now()))
			d = timedelta(days=int(dias))
			#se suman los dias para crear una fecha de expiracion
			expiracion = datetime.now() + d

			expiracion = str(expiracion)
			expiracion = expiracion[0:10]+" "+fecha[11:19]


			fechaActualizacion = fecha[0:19]
			#se actualiza el estado del codigo qr a grabado y la fecha de modificacion y expiracion
			codigoqr.estado = "1"
			codigoqr.fecha_modificacion= fechaActualizacion
			codigoqr.fecha_expiracion= expiracion
			codigoqr.save()

			np= codigoqr.hashVerificacion / (codigoqr.hashPrivado * 727)
			na = codigoqr.hashPrivado


			pub = hl.sha512()
			pub.update(str(np).encode('utf8'))
			dpub = pub.hexdigest()
			dpub = b64.b64encode(dpub.encode('utf8')).decode('utf8')

			tema=""
			codigoTemaCount = CodigoTema.objects.filter(codigo_id=qr_id).count()
			if(codigoTemaCount > 0):
				codigoTema = CodigoTema.objects.get(codigo_id=qr_id)
				tema= Tema.objects.get(id=codigoTema.tema_id).codigo


			#se crea un template pequeño que busca dar la opcion de confirmar lo que se guardo
			html = "<html>"
			html+="<head>"
			html+="<link rel =stylesheet href=/static/main/"+str(tema)+"/css/style.css>"
			html+="<div id='verguardar'>"
			html+="<h3>Guardado con exito</h3>"
			html+="<h3>Su contenido estara vigente hasta: </h3>"+str(expiracion)

			multimedia = MultimediaQr.objects.filter(codigoqr_id=qr_id)

			if(len(multimedia)>0):
				tempo1 = os.path.isfile("/tmp/v_"+qr_id+".mp4")
				tempo2 = os.path.isfile("/tmp/"+qr_id+".mp4")

				if(tempo1 == False and tempo2 == False):
					pool = os.path.isfile(BASE5+qr_id+".mp4")

					if(pool== True):
						html+="<h3>Su Video ya fue procesado por el sistema y esta listo para ser visto.</h3>"
					else:
						hash_privado = b64.b64encode(str(na).encode('utf8')).decode('utf8')
						ultimos = hash_privado[-10:]
						pin = ultimos[:6]
						pin = pin.upper()

						html+="<h3>Su Video esta siendo procesado, estara listo en unos minutos.</h3>"
						html+="<h3>Conserva este PIN por si su video no carga correctamente:  <h3>"+"<h2 id='pin'>"+str(pin)+"</h2>"

				else:
					hash_privado = b64.b64encode(str(na).encode('utf8')).decode('utf8')
					ultimos = hash_privado[-10:]
					pin = ultimos[:6]
					pin = pin.upper()

					html+="<h3>Su Video esta siendo procesado, estara listo en unos minutos.</h3>"
					html+="<h3>Conserva este PIN por si su video no carga correctamente:  <h3>"+"<h2 id='pin'>"+str(pin)+"</h2>"


			html+="<h3>¿Desea observar su grabacion?</h3>"
			html+="</head>"
			html+="<body>"
			html+="<form action='/main/confirmar/?id="+str(codigoqr.id)+"&hash="+str(dpub)+"'  method='post'>"
			html+="<button type='submit' id='ir_ver' ></button>"
			html+="</div>"
			html+="</body>"
			html+="</html>"
			return HttpResponse(html)
	else:
		return HttpResponse("Vuelve a leer el codigo qr")

#no se utiliza pero se deja hay para evitar posibles conflictos
def guardarPlantilla(request):
	if(request.method == "POST"):
		plantilla = request.POST['idPlantilla']
		detalle=request.POST["detalle"]
		qr_id= request.POST["qr_id"]
		multimedia = MultimediaQr.objects.filter(codigoqr_id=qr_id)
		planti = QrPlantilla.objects.filter(codigoqr_id=qr_id)
		if(len(multimedia)>0):
			return HttpResponse("Ya se ha guardado un video")
		elif(len(planti)>0):
			return HttpResponse("Ya se ha guardado una plantilla")
		elif(plantilla==""):
			return HttpResponse("Debe seleccionar una plantilla")
		else:

			qrplantilla= QrPlantilla()
			qrplantilla.codigoqr_id = qr_id
			qrplantilla.plantilla_id = plantilla
			qrplantilla.detalle = detalle

			qrplantilla.save()

			timezone.activate(pytz.timezone("America/Bogota"))
			fecha = str(timezone.localtime(timezone.now()))
			fechaActualizacion = fecha[0:18]
			codigoqr = CodigoQr.objects.get(id=qr_id)
			codigoqr.estado = "1"
			codigoqr.fecha_modificacion= fechaActualizacion
			codigoqr.save()

			np= codigoqr.hashVerificacion / (codigoqr.hashPrivado * 727)
			# Crear las response para descargar el archivo zip

			pub = hl.sha512()
			pub.update(str(np).encode('utf8'))
			dpub = pub.hexdigest()
			dpub = b64.b64encode(dpub.encode('utf8')).decode('utf8')

			# Cargar la informacion del codigo qr

			html = "<html>"
			html+="<head>"
			html+="<h4>Guardado con exito</h4>"
			html+="<h3>¿Deseas observar tu mensaje?</h3>"
			html+="</head>"
			html+="<body>"
			html+="<form action='/main/confirmar/?id="+str(codigoqr.id)+"&hash="+str(dpub)+"'  method='post'>"
			html+="<input type='submit' value='Ir'>"
			html+="</body>"
			html+="</html>"
			return HttpResponse(html)
	else:
		return HttpResponse("Vuelve a leer el codigo Qr")


def codigosView(request,codigo_lote):
	#funcion que permite ver los codigosqr pertenecientes al lote seleccionado

	codigos = CodigoQr.objects.filter(lote=codigo_lote).order_by('estado','fecha_modificacion','id')

	template = loader.get_template('main/codigos.html')
	context = RequestContext(request, {
        'codigos': codigos,
        'lote': codigo_lote,
        'css': "codigos",
		'tema': "admin",
    })
	return HttpResponse(template.render(context))

def codigosVendedorView(request,codigo_lote):
	#funcion que permite ver los codigosqr pertenecientes al lote seleccionado
	if "username" in request.session:
		vendedor = Vendedor.objects.get(user=request.session.get('username'))
		#codigos = CodigoQr.objects.filter(lote=codigo_lote).order_by('estado','fecha_modificacion')
		lista = CodigoVendedor.objects.values('codigo__id','codigo__fecha_creacion','codigo__estado').filter(codigo__lote=codigo_lote).filter(vendedor=vendedor.id).order_by('codigo__estado','-codigo__fecha_creacion',"codigo__id")
		#lista_codigos=[]


		codigos=[]
		for i in range(len(lista)):
			print(lista[i])
			codigos.append({'id': lista[i]['codigo__id'],'fecha_creacion': lista[i]['codigo__fecha_creacion'],'estado' : lista[i]['codigo__estado']})

	template = loader.get_template('main/codigosVendedor.html')
	context = RequestContext(request, {
        'codigos': codigos,
        'lote': codigo_lote,
        'css': "codigosVendedor",
		'vendedor': vendedor,
		'lote': codigo_lote,
		'tema': "admin",
    })
	return HttpResponse(template.render(context))



def qcode(request):
	#descarga el pdf con el codigoqr especifico
	code_id = request.GET.get('id')
	code_hash = request.GET.get('hash')

	response = HttpResponse(content_type='application/pdf')
	response['Content-Disposition'] = "attachment; filename='codigoqr-"+str(code_id)+".pdf'"

	codigo = CodigoQr.objects.get(id=code_id)

	na = codigo.hashPrivado
	nc = codigo.hashVerificacion
	nb = nc / (na*727)

	pub = hl.sha512()
	pub.update(str(nb).encode('utf8'))
	dpub = pub.hexdigest()
	dpub = b64.b64encode(dpub.encode('utf8')).decode('utf8')
	#validacion del hash del codigo
	if(code_hash == dpub):
		nb= codigo.hashVerificacion / (codigo.hashPrivado * 727)
		# Crear las response para descargar el archivo zip

		pub = hl.sha512()
		pub.update(str(nb).encode('utf8'))
		dpub = pub.hexdigest()
		dpub = b64.b64encode(dpub.encode('utf8')).decode('utf8')


		# Crear el fichero pdf
		fpdf = BytesIO()

		# Crear el area de dibujo y vincularla al fichero pdf
		p = canvas.Canvas(fpdf)

		# Cargar la informacion del codigo qr
		qrw = QrCodeWidget(BASE2+"/main/multimedia?id="+str(codigo.id)+"&hash="+str(dpub))


		# Calcular el ancho y alto del codigo qr
		b = qrw.getBounds()
		w = b[2] - b[0]
		h = b[3] - b[1]

		# Ajustar el tamaño del canvas al tamaño del codigo
		p.setPageSize((w + 2, h + 2))

		# Dibujar el codigo qr
		d = Drawing()
		d.add(qrw)
		renderPDF.draw(d, p, 1, 1)

		# Crear la pagina y guardar el contenido del pdf
		p.showPage()
		p.save()

		# Agregar el fichero pdf al contenedor zip



		rpdf = fpdf.getvalue()
		fpdf.close()

		response.write(rpdf)
		return response

	else:
		html = "<html><body>Not Found 404</body></html>"
		return HttpResponse(html)


def validarLote(request):
	if(request.method == "POST"):
		respon = json.loads(request.body.decode("utf8"))

		lote = respon["lote"]
		codigos = CodigoQr.objects.filter(lote=lote)
		if(len(codigos) >0):
			respuesta=1
		else:
			respuesta=2
		return HttpResponse(
				json.dumps(respuesta),
				content_type="application/json"
			)




def guardar(request):
	if(request.method == "POST"):
		#guarda el lote que se ha generado
		lote= request.POST["lote"]
		cantidad=request.POST["cantidad"]
		dias=request.POST["dias"]
		listopciones=request.POST.getlist('opciones')
		listcategorias=request.POST["categorias"]
		listcategorias = listcategorias.split(';')
		tema=request.POST["tema"]
		imagenInicial=request.POST["imagenInicial"]
		marco=request.POST["marco"]
		#valida si los campos estan completos. esta validacion se hace tambien en el javascript
		if(lote == ""):
			return HttpResponse("El campo lote no puede ser vacio")

		if(dias == ""):
			return HttpResponse("El campo dias no puede ser vacio")

		if(cantidad == ""):
			return HttpResponse("El campo cantidad no puede ser vacio")

		opciones=""
		lib=""
		for i in listopciones:
			if(i=="L"):
				lib="L"
			opciones=opciones+str(i)

		codigos = CodigoQr.objects.filter(lote=lote)
		if(len(codigos) >0):
			return HttpResponse("El lote ya existe, no se puede generar de nuevo")

		timezone.activate(pytz.timezone("America/Bogota"))

		fecha = str(timezone.localtime(timezone.now()))

		fechaCreacion = fecha[0:18]
		lista=[]

		if(tema==""):
			temas = Tema.objects.filter(defecto=1)
			if(len(temas)>0):
				for i in temas:
					tema= i.id
			else:
				temas = Tema.objects.filter().order_by("id")[:1]
				for i in temas:
					tema= i.id

		if(marco=="" and lib == "L"):
			marcos = Marco.objects.filter(defecto=1)
			if(len(marcos)>0):
				for i in marcos:
					marco= i.id
			else:
				marcos = Marcos.objects.filter().order_by("id")[:1]
				for i in marcos:
					marco= i.id




		for i in range(int(cantidad)):
			#creacion de los hash de cada codigoqr
			na = int(random.randint(10**13, 10**23)*random.random()*random.random()*random.random())
			nb = int(random.randint(10**13, 10**23)*random.random()*random.random()*random.random())
			nc = na*nb*727
			nb = nc / (na*727)
			#guarda los codigosqr
			codigo= CodigoQr()
			codigo.lote = lote
			codigo.fecha_creacion = fechaCreacion
			codigo.fecha_publicacion = None
			codigo.estado = '0'
			codigo.hashPrivado =  str(na)
			codigo.hashVerificacion = str(nc)
			codigo.opciones = opciones
			codigo.dias = dias
			codigo.save()

			codigoTema= CodigoTema()
			codigoTema.codigo_id =codigo.id
			codigoTema.tema_id = tema
			codigoTema.save()

			print(listcategorias)
			for c in listcategorias:
				print(c)
				if(c!=''):
					codigoCategoria= CodigoCategoria()
					codigoCategoria.codigo_id =codigo.id
					codigoCategoria.categoria_id = c
					codigoCategoria.save()

			if(imagenInicial != ""):
				codigoImagen= CodigoImagen()
				codigoImagen.codigo_id =codigo.id
				codigoImagen.imagen_id = imagenInicial
				codigoImagen.save()
			if(marco != ""):
				codigoMarco= CodigoMarco()
				codigoMarco.codigo_id =codigo.id
				codigoMarco.marco_id = marco
				codigoMarco.save()




		#genera archivo csv en el servidor
		codigos = CodigoQr.objects.filter(lote=lote).filter(estado='0').order_by('estado')
		i=0

		for code in codigos:
			np= code.hashVerificacion / (code.hashPrivado * 727)


			pub = hl.sha512()
			pub.update(str(np).encode('utf8'))
			dpub = pub.hexdigest()
			dpub = b64.b64encode(dpub.encode('utf8')).decode('utf8')

			# Cargar la informacion del codigo qr
			lista.append(BASE2+"/main/multimedia?id="+str(code.id)+"&hash="+str(dpub))


		#f= open("main/archivos/"+str(lote)+".csv","w")
		#lista = "\n".join(lista)
		#f.write(lista)
		#f.closed
		#redirecciona al index
		return redirect('/main/index/')
	else:
		return redirect('/main/index/')


def descargar(request,codigo_lote):

	response = HttpResponse(content_type='application/zip')
	response['Content-Disposition'] = "attachment; filename='"+str(codigo_lote)+".zip'"

	# Crear el fichero CSV para almacenar la lista de todos los ficheros pdf
	fcsv = StringIO()
	lista = []

	# Crear el fichero zip contenedor
	fzip = BytesIO()
	archive = ZipFile(fzip, 'w', ZIP_DEFLATED)

	codigos = CodigoQr.objects.filter(lote=codigo_lote).filter(estado='0').order_by('estado')
	i=0
	for codigo in codigos:
		nb= codigo.hashVerificacion / (codigo.hashPrivado * 727)
		# Crear las response para descargar el archivo zip



		pub = hl.sha512()
		pub.update(str(nb).encode('utf8'))
		dpub = pub.hexdigest()
		dpub = b64.b64encode(dpub.encode('utf8')).decode('utf8')


		# Crear el fichero pdf
		fpdf = BytesIO()

		# Crear el area de dibujo y vincularla al fichero pdf
		p = canvas.Canvas(fpdf)

		# Cargar la informacion del codigo qr
		qrw = QrCodeWidget(BASE2+"/main/multimedia?id="+str(codigo.id)+"&hash="+str(dpub))

		# Calcular el ancho y alto del codigo qr
		b = qrw.getBounds()
		w = b[2] - b[0]
		h = b[3] - b[1]

		# Ajustar el tamaño del canvas al tamaño del codigo
		p.setPageSize((w + 2, h + 2))

		# Dibujar el codigo qr
		d = Drawing()
		d.add(qrw)
		renderPDF.draw(d, p, 1, 1)

		# Crear la pagina y guardar el contenido del pdf
		p.showPage()
		p.save()

		# Agregar el fichero pdf al contenedor zip
		archive.writestr(str(codigo_lote)+str(i+1)+'.pdf', fpdf.getvalue())
		fpdf.close()

		# Agregar el nombre del fichero pdf a la lista
		lista.append(BASE2+"/main/qcode?id="+str(codigo.id)+"&hash="+dpub)
		i+=1


    # Convertir la lista de ficheros en formato texto y escribirla en el fichero CSV
	lista = "\n".join(lista)
	fcsv.write(lista)

	# Agregar la lista (CSV) al contenedor zip
	archive.writestr(str(codigo_lote)+'.csv', fcsv.getvalue())
	fcsv.close()

	# Cerrar el fichero zip
	archive.close()

	# Obtener el contenido del fichero zip
	fzip.flush()
	rzip = fzip.getvalue()
	fzip.close()

	# Cargar el contenido del fichero zip en la response
	response.write(rzip)

	# Enviar la response con el fichero zip para ser descargada.

	return response



def descargarVendedor(request,codigo_lote):

	response = HttpResponse(content_type='application/zip')
	response['Content-Disposition'] = "attachment; filename='"+str(codigo_lote)+".zip'"

	# Crear el fichero CSV para almacenar la lista de todos los ficheros pdf
	fcsv = StringIO()
	lista = []

	# Crear el fichero zip contenedor
	fzip = BytesIO()
	archive = ZipFile(fzip, 'w', ZIP_DEFLATED)


	vendedor = Vendedor.objects.get(user=request.session.get('username'))

	codigos = CodigoQr.objects.filter(lote=codigo_lote).filter(estado='0').filter(codigovendedor__vendedor=vendedor.id).order_by('estado')
	i=0
	for codigo in codigos:
		nb= codigo.hashVerificacion / (codigo.hashPrivado * 727)
		# Crear las response para descargar el archivo zip



		pub = hl.sha512()
		pub.update(str(nb).encode('utf8'))
		dpub = pub.hexdigest()
		dpub = b64.b64encode(dpub.encode('utf8')).decode('utf8')


		# Crear el fichero pdf
		fpdf = BytesIO()

		# Crear el area de dibujo y vincularla al fichero pdf
		p = canvas.Canvas(fpdf)

		# Cargar la informacion del codigo qr
		qrw = QrCodeWidget(BASE2+"/main/multimedia?id="+str(codigo.id)+"&hash="+str(dpub))

		# Calcular el ancho y alto del codigo qr
		b = qrw.getBounds()
		w = b[2] - b[0]
		h = b[3] - b[1]

		# Ajustar el tamaño del canvas al tamaño del codigo
		p.setPageSize((w + 2, h + 2))

		# Dibujar el codigo qr
		d = Drawing()
		d.add(qrw)
		renderPDF.draw(d, p, 1, 1)

		# Crear la pagina y guardar el contenido del pdf
		p.showPage()
		p.save()

		# Agregar el fichero pdf al contenedor zip
		archive.writestr(str(codigo_lote)+str(i+1)+'.pdf', fpdf.getvalue())
		fpdf.close()

		# Agregar el nombre del fichero pdf a la lista
		lista.append(BASE2+"/main/qcode?id="+str(codigo.id)+"&hash="+dpub)
		i+=1


    # Convertir la lista de ficheros en formato texto y escribirla en el fichero CSV
	lista = "\n".join(lista)
	fcsv.write(lista)

	# Agregar la lista (CSV) al contenedor zip
	archive.writestr(str(codigo_lote)+'.csv', fcsv.getvalue())
	fcsv.close()

	# Cerrar el fichero zip
	archive.close()

	# Obtener el contenido del fichero zip
	fzip.flush()
	rzip = fzip.getvalue()
	fzip.close()

	# Cargar el contenido del fichero zip en la response
	response.write(rzip)

	# Enviar la response con el fichero zip para ser descargada.

	return response



def listCodigos(request,codigo_lote):
	response = HttpResponse(content_type='application/csv')
	response['Content-Disposition'] = "attachment; filename='"+str(codigo_lote)+".csv'"

	fexcel = BytesIO()
	fcsv = StringIO()
	lista = []
	codigos = CodigoQr.objects.filter(lote=codigo_lote).filter(estado='0').order_by('estado')
	i=0
	for codigo in codigos:
		nb= codigo.hashVerificacion / (codigo.hashPrivado * 727)
		# Crear las response para descargar el archivo excel



		pub = hl.sha512()
		pub.update(str(nb).encode('utf8'))
		dpub = pub.hexdigest()
		dpub = b64.b64encode(dpub.encode('utf8')).decode('utf8')

		lista.append(BASE2+"/main/qcode?id="+str(codigo.id)+"&hash="+dpub)

	lista = "\n".join(lista)

	fcsv.write(lista)




	fcsv.flush()
	rexcel = fcsv.getvalue()
	fcsv.close()

	response.write(rexcel)

	# Enviar la response con el fichero excel para ser descargada.

	return response

def listCodigosVendedor(request,codigo_lote):
	response = HttpResponse(content_type='application/csv')
	response['Content-Disposition'] = "attachment; filename='"+str(codigo_lote)+".csv'"

	fexcel = BytesIO()
	fcsv = StringIO()
	lista = []
	vendedor = Vendedor.objects.get(user=request.session.get('username'))
	codigos = CodigoQr.objects.filter(lote=codigo_lote).filter(codigovendedor__vendedor=vendedor.id).filter(estado='0').order_by('estado')
	i=0
	for codigo in codigos:
		nb= codigo.hashVerificacion / (codigo.hashPrivado * 727)
		# Crear las response para descargar el archivo excel



		pub = hl.sha512()
		pub.update(str(nb).encode('utf8'))
		dpub = pub.hexdigest()
		dpub = b64.b64encode(dpub.encode('utf8')).decode('utf8')

		lista.append(BASE2+"/main/qcode?id="+str(codigo.id)+"&hash="+dpub)

	lista = "\n".join(lista)

	fcsv.write(lista)




	fcsv.flush()
	rexcel = fcsv.getvalue()
	fcsv.close()

	response.write(rexcel)

	# Enviar la response con el fichero excel para ser descargada.

	return response

def ingresarImagenView(request):
	#envia a template end donde se ingresan las plantillas nuevas
	model = ImagenInicial
	#busca las categorias existente

	imagen = ImagenInicial.objects.filter().order_by('nombre')
	listImagen=[]
	if(len(imagen)>0):
		for r in imagen:

			listImagen.append([r.id,r.nombre,r.url])

	template = loader.get_template('main/ingresarImagen.html')
	context = RequestContext(request, {

	'imagenes': listImagen,
	'css': "imagen",
	'tema': "admin",
	})
	#envia datos
	return HttpResponse(template.render(context))

def almacenarImagen(request):
	#almacena la imagen guardada
	if(request.method == "POST"):

		nombre= request.POST["nombre"]
		url= request.POST["url"]
		imagen_id= request.POST["id"]

		#verifica que los campos no esten vacios aunque ya la validacion fue hecha en javascript

		if(nombre==""):
			return HttpResponse("El campo Nombre no puede ser vacio")
		elif(url==""):
			return HttpResponse("El campo Url no puede ser vacio")
		else:
			if(imagen_id=="0"):
				#si los campos son diferentes de vacios se guarda la plantilla
				imagen= ImagenInicial()
				imagen.nombre = nombre
				imagen.url = url
				imagen.save()
			else:
				imagen = ImagenInicial.objects.get(id=imagen_id)
				imagen.nombre = nombre
				imagen.url = url
				imagen.save()
				#vuelve a retorna a la vista para ingresar una nueva plantilla
			return redirect('/main/ingresarImagen/')

	else:
		return redirect('/main/ingresarImagen/')
def editarImagen(request):
	imagen_id = request.POST.get('imagen_id')

	imagen = ImagenInicial.objects.filter(id=imagen_id)
	imagenArray = []
	if(len(imagen)>0):
		imagen = ImagenInicial.objects.get(id=imagen_id)
		imagenArray.append([imagen.id,imagen.nombre,imagen.url])

		return HttpResponse(
			json.dumps(imagenArray),
			content_type="application/json"
			)

def eliminarImagen(request):
	imagen_id = request.POST.get('imagen_id')

	imagen = ImagenInicial.objects.filter(id=imagen_id)

	if(len(imagen)>0):
		imagen = ImagenInicial.objects.get(id=imagen_id)
		imagen.delete()
		mensaje=1
		return HttpResponse(
			json.dumps(mensaje),
			content_type="application/json"
			)



def ingresarMarcoView(request):
	#envia a template end donde se ingresan las plantillas nuevas
	model = Marco
	#busca las categorias existente

	marco= Marco.objects.filter().order_by('nombre')
	listMarco=[]
	if(len(marco)>0):
		for r in marco:
			d=""
			if(r.defecto == "1"):
				d="Si"
			else:
				d="No"

			listMarco.append([r.id,r.nombre,r.enlace,d])

	template = loader.get_template('main/ingresarMarco.html')
	context = RequestContext(request, {

	'marcos': listMarco,
	'css': "marco",
	'tema': "admin",
	})
	#envia datos
	return HttpResponse(template.render(context))

def almacenarMarco(request):
	#almacena la imagen guardada
	if(request.method == "POST"):

		nombre= request.POST["nombre"]
		url= request.POST["url"]
		marco_id= request.POST["id"]
		defecto= request.POST["defecto"]

		#verifica que los campos no esten vacios aunque ya la validacion fue hecha en javascript

		if(nombre==""):
			return HttpResponse("El campo Nombre no puede ser vacio")
		elif(url==""):
			return HttpResponse("El campo Url no puede ser vacio")
		else:
			if(marco_id=="0"):
				#si los campos son diferentes de vacios se guarda la plantilla
				imagen= Marco()
				imagen.nombre = nombre
				imagen.enlace = url
				imagen.defecto = defecto
				imagen.save()
			else:
				imagen = Marco.objects.get(id=marco_id)
				imagen.nombre = nombre
				imagen.enlace = url
				imagen.defecto = defecto
				imagen.save()
				#vuelve a retorna a la vista para ingresar una nueva plantilla
			return redirect('/main/ingresarMarco/')

	else:
		return redirect('/main/ingresarMarco/')
def editarMarco(request):
	marco_id = request.POST.get('marco_id')

	marco = Marco.objects.filter(id=marco_id)
	marcoArray = []
	if(len(marco)>0):
		marco = Marco.objects.get(id=marco_id)
		marcoArray.append([marco.id,marco.nombre,marco.enlace,marco.defecto])

		return HttpResponse(
			json.dumps(marcoArray),
			content_type="application/json"
			)

def eliminarMarco(request):
	marco_id = request.POST.get('marco_id')

	marco = Marco.objects.filter(id=marco_id)

	if(len(marco)>0):
		marco = Marco.objects.get(id=marco_id)
		marco.delete()
		mensaje=1
		return HttpResponse(
			json.dumps(mensaje),
			content_type="application/json"
			)
