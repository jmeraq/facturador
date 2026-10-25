from django.contrib import admin
from .models import Emisor, Cliente, Producto, Factura, DetalleFactura, MovimientoInventario, PerfilUsuario


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'rol')
    list_filter = ('rol',)
    search_fields = ('usuario__username', 'usuario__first_name', 'usuario__last_name', 'usuario__email')


@admin.register(Emisor)
class EmisorAdmin(admin.ModelAdmin):
    list_display = ('razon_social', 'ruc', 'establecimiento', 'punto_emision', 'secuencial_actual', 'tarifa_iva_defecto')


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('identificacion', 'tipo_identificacion', 'nombres', 'email', 'telefono')
    search_fields = ('identificacion', 'nombres', 'email')
    list_filter = ('tipo_identificacion',)


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'precio_unitario', 'tarifa_iva', 'stock', 'stock_minimo', 'activo')
    search_fields = ('codigo', 'nombre')
    list_filter = ('activo', 'tarifa_iva')


class DetalleFacturaInline(admin.TabularInline):
    model = DetalleFactura
    extra = 0
    readonly_fields = ('codigo_producto', 'nombre_producto', 'cantidad', 'precio_unitario', 'tarifa_iva', 'subtotal', 'valor_iva', 'total')


@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    list_display = ('numero_factura', 'cliente', 'fecha_emision', 'forma_pago', 'total', 'estado')
    search_fields = ('numero_factura', 'cliente__nombres', 'cliente__identificacion')
    list_filter = ('estado', 'forma_pago', 'fecha_emision')
    inlines = [DetalleFacturaInline]


@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'producto', 'tipo', 'cantidad', 'stock_anterior', 'stock_nuevo', 'factura', 'motivo')
    search_fields = ('producto__nombre', 'producto__codigo', 'motivo')
    list_filter = ('tipo', 'fecha')
