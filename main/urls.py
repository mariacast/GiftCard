from django.conf.urls import patterns, include, url

from . import views

app_name = 'main'
urlpatterns = [
	
	
	url(r'^traerTema/$', views.traerTema, name='traerTema'),
	url(r'^validarLote/$', views.validarLote, name='validarLote'),
	url(r'^traerImagen/$', views.traerImagen, name='traerImagen'),
	url(r'^traerMarco/$', views.traerMarco, name='traerMarco'),
	url(r'^index/$', views.indexView, name='index'),
	url(r'^indexVendedor/$', views.indexVendedorView, name='indexVendedor'),
	
    url(r'^generar/$', views.generarView, name='generar'),
    
    url(r'^ingresarPlantilla/$', views.ingresarPlantillaView, name='ingresarPlantilla'),
    url(r'^almacenarPlantilla/$', views.almacenarPlantilla, name='almacenarPlantilla'),
    url(r'^editarPlantilla/$', views.editarPlantilla, name='editarPlantilla'),
    url(r'^eliminarPlantilla/$', views.eliminarPlantilla, name='eliminarPlantilla'),
    
    url(r'^ingresarImagen/$', views.ingresarImagenView, name='ingresarImagen'),
    url(r'^almacenarImagen/$', views.almacenarImagen, name='almacenarImagen'),
    url(r'^editarImagen/$', views.editarImagen, name='editarImagen'),
    url(r'^eliminarImagen/$', views.eliminarImagen, name='eliminarImagen'),
 
    url(r'^ingresarMarco/$', views.ingresarMarcoView, name='ingresarMarco'),
    url(r'^almacenarMarco/$', views.almacenarMarco, name='almacenarMarco'),
    url(r'^editarMarco/$', views.editarMarco, name='editarMarco'),
    url(r'^eliminarMarco/$', views.eliminarMarco, name='eliminarMarco'),
 
    
    url(r'^vendedor/$', views.vendedorView, name='vendedor'),
    url(r'^editarVendedor/$', views.editarVendedor, name='editarVendedor'),
    url(r'^eliminarVendedor/$', views.eliminarVendedor, name='eliminarVendedor'),
    url(r'^almacenarVendedor/$', views.almacenarVendedor, name='almacenarVendedor'),
    
    url(r'^asignarVendedor/$', views.asignarVendedorView, name='asignarVendedor'),
    url(r'^editarCodigoVendedor/$', views.editarCodigoVendedor, name='editarCodigoVendedor'),
    url(r'^eliminarCodigoVendedor/$', views.eliminarCodigoVendedor, name='eliminarVendedor'),
    url(r'^almacenarCodigoVendedor/$', views.almacenarCodigoVendedor, name='almacenarCodigoVendedor'),
    url(r'^traerLotes/$', views.traerLotes, name='traerLotes'),
    url(r'^traerCodigos/$', views.traerCodigos, name='traerCodigos'),
    url(r'^devolucion/$', views.devolucion, name='devolucion'),
    url(r'^usuario/$', views.usuarioView, name='usuario'),
    url(r'^usuariosVendedor/$', views.usuariosVendedorView, name='usuariosVendedor'),
    url(r'^enviarCorreoUsuario/$', views.enviarCorreoUsuario, name='enviarCorreoUsuario'),
    
    
    url(r'^ingresarCategoria/$', views.ingresarCategoriaView, name='ingresarCategoria'),
    url(r'^editarCategoria/$', views.editarCategoria, name='editarCategoria'),
    url(r'^eliminarCategoria/$', views.eliminarCategoria, name='eliminarCategoria'),
    url(r'^almacenarCategoria/$', views.almacenarCategoria, name='almacenarCategoria'),
    
    url(r'^ingresarFrase/$', views.ingresarFraseView, name='ingresarFrase'),
    url(r'^editarFrase/$', views.editarFrase, name='editarFrase'),
    url(r'^eliminarFrase/$', views.eliminarFrase, name='eliminarFrase'),
    url(r'^almacenarFrase/$', views.almacenarFrase, name='almacenarFrase'),
	url(r'^loginPage/$', views.loginPage, name='loginPage'),
	url(r'^adminPage/$', views.adminPage, name='adminPage'),
    url(r'^consultarFrases/$', views.consultarFrases, name='consultarFrases'),
    url(r'^pegarFras/$', views.pegarFras, name='pegarFras'),
    url(r'reportes/$', views.reportesView, name='reportes'),
    url(r'reportesVendedor/$', views.reportesVendedorView, name='reportesVendedor'),
    url(r'^qcode/$', views.qcode, name='qcode?'),
    url(r'multimedia/$', views.multimediaView, name='multimedia'),
    url(r'multimediaiOS/$', views.multimediaiOS, name='multimediaiOS'),
    url(r'multimediaRTC/$', views.multimediaRTC, name='multimediaRTC'),
    url(r'confirmar/$', views.confirmarView, name='confirmar'),
    url(r'^guardarMultimedia/$', views.guardarMultimedia, name='guardarMultimedia'),
    url(r'guardarPlantilla/$', views.guardarPlantilla, name='guardarPlantilla'),
    url(r'^(?P<codigo_lote>[^/]+)/codigos/$', views.codigosView, name='codigos'),
    url(r'^(?P<codigo_lote>[^/]+)/codigosVendedor/$', views.codigosVendedorView, name='codigosVendedor'),
    url(r'^(?P<codigo_lote>[^/]+)/descargar/$', views.descargar, name='descargar'),
    url(r'^(?P<codigo_lote>[^/]+)/descargarVendedor/$', views.descargarVendedor, name='descargarVendedor'),
    url(r'^qcode/$', views.qcode, name='qcode?'),
    url(r'^(?P<codigo_lote>[^/]+)/listCodigos/$', views.listCodigos, name='listCodigos'),
    url(r'^(?P<codigo_lote>[^/]+)/listCodigosVendedor/$', views.listCodigosVendedor, name='listCodigosVendedor'),
    url(r'^guardar/$', views.guardar, name='guardar'),
    url(r'^eliminarExpirados/$', views.eliminarExpirados, name='eliminarExpirados'),
    url(r'^guardarRegistro/$', views.guardarRegistro, name='guardarRegistro'),
    url(r'^loginMultimedia/$', views.loginMultimedia, name='loginMultimedia'),
    url(r'^cerrarMultimedia/$', views.cerrarMultimedia, name='cerrarMultimedia'),
    url(r'^recuperarCorreo/$', views.recuperarCorreo, name='recuperarCorreo'),
    url(r'^cambiarContrasena/$', views.cambiarContrasena, name='cambiarContrasena'),
    url(r'^codigosAntiguos/$', views.codigosAntiguos, name='codigosAntiguos'),
    url(r'^administracion/$', views.administracion, name='administracion'),
    url(r'^eliminarGrabacion/$', views.eliminarGrabacion, name='eliminarGrabacion'),
    url(r'^verGrabacion/$', views.verGrabacion, name='verGrabacion'),
    url(r'^extenderGrabacion/$', views.extenderGrabacion, name='extenderGrabacion'),
    url(r'^traerLista/$', views.traerLista, name='traerLista'),
    url(r'^$', views.login_view, name='login'),
    url(r'^login/$', views.login_view, name='login2'),
    url(r'^salir/$', views.logout_view, name='salir'),
    url(r'^compartir/(?P<code_id>[^/]+)/(?P<code_hash>[^/]+)$', views.compartir, name='compartir'),
    url(r'send_mail/$', views.send_mail, name='send_mail'),
	
	url(r'subirVideo/$', views.subirVideo, name='subirVideo'),
	url(r'subirImagen/$', views.subirImagen, name='subirImagen'),
	url(r'limpiarCodigo/$', views.limpiarCodigo, name='limpiarCodigo'),
	url(r'urlIframe/$', views.urlIframe, name='urlIframe'),
    
    
]

