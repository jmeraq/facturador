from django.urls import path
from . import views

urlpatterns = [
    # Autenticación
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Productos
    path('productos/', views.producto_lista, name='producto_lista'),
    path('productos/nuevo/', views.producto_crear, name='producto_crear'),
    path('productos/<int:pk>/editar/', views.producto_editar, name='producto_editar'),
    path('productos/<int:pk>/eliminar/', views.producto_eliminar, name='producto_eliminar'),

    # Inventario
    path('inventario/', views.inventario_dashboard, name='inventario_dashboard'),

    # Clientes
    path('clientes/', views.cliente_lista, name='cliente_lista'),
    path('clientes/nuevo/', views.cliente_crear, name='cliente_crear'),
    path('clientes/<int:pk>/editar/', views.cliente_editar, name='cliente_editar'),

    # Facturación
    path('facturas/', views.factura_lista, name='factura_lista'),
    path('facturas/nueva/', views.factura_crear, name='factura_crear'),
    path('facturas/<int:pk>/', views.factura_detalle, name='factura_detalle'),
    path('facturas/<int:pk>/anular/', views.factura_anular, name='factura_anular'),

    # Configuración de Emisor
    path('configuracion/', views.emisor_configuracion, name='emisor_configuracion'),

    # API interna
    path('api/productos/', views.api_productos, name='api_productos'),
]
