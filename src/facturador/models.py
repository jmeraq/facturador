from decimal import Decimal
from django.db import models, transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .validators import validar_identificacion_ecuador


class Emisor(models.Model):
    """
    Datos del emisor de facturas en Ecuador (SRI).
    Normalmente una sola empresa activa en el sistema.
    """
    ruc = models.CharField(max_length=13, default="1790012345001", verbose_name="RUC")
    razon_social = models.CharField(max_length=200, default="EMPRESA DE PRUEBA S.A.S.", verbose_name="Razón Social")
    nombre_comercial = models.CharField(max_length=200, default="MI TIENDA ECUADOR", verbose_name="Nombre Comercial")
    direccion_matriz = models.TextField(default="Av. Amazonas y Naciones Unidas, Quito - Ecuador", verbose_name="Dirección Matriz")
    establecimiento = models.CharField(max_length=3, default="001", verbose_name="Código Establecimiento")
    punto_emision = models.CharField(max_length=3, default="001", verbose_name="Punto de Emisión")
    secuencial_actual = models.PositiveIntegerField(default=1, verbose_name="Secuencial Actual")
    tarifa_iva_defecto = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('15.00'), verbose_name="Tarifa IVA (%)")
    obligado_contabilidad = models.BooleanField(default=False, verbose_name="Obligado a llevar contabilidad")
    es_contribuyente_rimpe = models.BooleanField(default=True, verbose_name="Contribuyente Régimen RIMPE")

    class Meta:
        verbose_name = "Emisor / Datos de Facturación"
        verbose_name_plural = "Emisores"

    def __str__(self):
        return f"{self.razon_social} ({self.ruc})"

    @classmethod
    def get_emisor(cls):
        """Retorna el emisor configurado o crea uno por defecto."""
        emisor, _ = cls.objects.get_or_create(id=1)
        return emisor

    def obtener_siguiente_numero(self):
        """Genera el siguiente número secuencial en formato SRI: 001-001-000000001"""
        num_str = str(self.secuencial_actual).zfill(9)
        return f"{self.establecimiento}-{self.punto_emision}-{num_str}"


class Cliente(models.Model):
    """
    Cliente para la emisión de facturas según normativa SRI.
    """
    TIPO_IDENTIFICACION_CHOICES = [
        ('04', 'RUC (13 dígitos)'),
        ('05', 'Cédula (10 dígitos)'),
        ('06', 'Pasaporte'),
        ('07', 'Consumidor Final (9999999999999)'),
    ]

    tipo_identificacion = models.CharField(
        max_length=2,
        choices=TIPO_IDENTIFICACION_CHOICES,
        default='05',
        verbose_name="Tipo de Identificación"
    )
    identificacion = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Número de Identificación"
    )
    nombres = models.CharField(max_length=200, verbose_name="Nombres y Apellidos / Razón Social")
    email = models.EmailField(blank=True, default="", verbose_name="Correo Electrónico")
    telefono = models.CharField(max_length=30, blank=True, default="", verbose_name="Teléfono / Celular")
    direccion = models.TextField(blank=True, default="Ecuador", verbose_name="Dirección")
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['nombres']

    def clean(self):
        super().clean()
        validar_identificacion_ecuador(self.tipo_identificacion, self.identificacion)

    def __str__(self):
        return f"{self.identificacion} - {self.nombres}"


class Producto(models.Model):
    """
    Tabla de productos para facturación e inventario.
    """
    TARIFA_IVA_CHOICES = [
        (Decimal('15.00'), 'IVA 15% (Tarifa vigente Ecuador)'),
        (Decimal('0.00'), 'IVA 0% (Tarifa cero)'),
    ]

    codigo = models.CharField(max_length=50, unique=True, verbose_name="Código / SKU")
    nombre = models.CharField(max_length=200, verbose_name="Nombre del Producto")
    descripcion = models.TextField(blank=True, default="", verbose_name="Descripción")
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Precio Unitario (sin IVA)")
    tarifa_iva = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        choices=TARIFA_IVA_CHOICES,
        default=Decimal('15.00'),
        verbose_name="Tarifa de IVA"
    )
    stock = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), verbose_name="Stock en Inventario")
    stock_minimo = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('5.00'), verbose_name="Stock Mínimo")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['nombre']

    def __str__(self):
        return f"[{self.codigo}] {self.nombre} (Stock: {self.stock})"

    @property
    def precio_con_iva(self):
        factor = Decimal('1.00') + (self.tarifa_iva / Decimal('100.00'))
        return round(self.precio_unitario * factor, 2)

    @property
    def stock_bajo(self):
        return self.stock <= self.stock_minimo

    def tiene_stock_suficiente(self, cantidad):
        return self.stock >= Decimal(str(cantidad))


class Factura(models.Model):
    """
    Cabecera de Factura para Ecuador.
    """
    FORMA_PAGO_CHOICES = [
        ('01', '01 - Efectivo (Sin utilización del sistema financiero)'),
        ('16', '16 - Tarjeta de Débito'),
        ('19', '19 - Tarjeta de Crédito'),
        ('20', '20 - Otros con utilización del sistema financiero (Transferencia/Depósito)'),
    ]

    ESTADO_CHOICES = [
        ('EMITIDA', 'Emitida'),
        ('ANULADA', 'Anulada'),
    ]

    numero_factura = models.CharField(max_length=25, unique=True, verbose_name="Número de Factura")
    secuencial = models.PositiveIntegerField(verbose_name="Secuencial")
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='facturas', verbose_name="Cliente")
    fecha_emision = models.DateTimeField(default=timezone.now, verbose_name="Fecha de Emisión")
    forma_pago = models.CharField(max_length=2, choices=FORMA_PAGO_CHOICES, default='01', verbose_name="Forma de Pago")
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='EMITIDA', verbose_name="Estado")

    # Valores tributarios Ecuador
    subtotal_15 = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), verbose_name="Subtotal IVA 15%")
    subtotal_0 = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), verbose_name="Subtotal IVA 0%")
    subtotal_sin_impuestos = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), verbose_name="Subtotal sin Impuestos")
    descuento_total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), verbose_name="Descuento")
    iva_15 = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), verbose_name="IVA 15%")
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), verbose_name="Importe Total")

    observaciones = models.TextField(blank=True, default="", verbose_name="Observaciones")
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Factura"
        verbose_name_plural = "Facturas"
        ordering = ['-fecha_emision', '-id']

    def __str__(self):
        return f"Factura #{self.numero_factura} - {self.cliente.nombres} (${self.total})"

    def anular(self, motivo="Anulación de factura por usuario"):
        """
        Anula la factura y repone el inventario de todos los productos incluidos.
        """
        if self.estado == 'ANULADA':
            raise ValidationError("Esta factura ya se encuentra anulada.")

        with transaction.atomic():
            self.estado = 'ANULADA'
            self.observaciones = f"{self.observaciones}\n[ANULADA el {timezone.now().strftime('%Y-%m-%d %H:%M')}: {motivo}]".strip()
            self.save(update_fields=['estado', 'observaciones'])

            # Reponer inventario
            for detalle in self.detalles.select_related('producto').all():
                prod = detalle.producto
                stock_previo = prod.stock
                prod.stock += detalle.cantidad
                prod.save(update_fields=['stock'])

                MovimientoInventario.objects.create(
                    producto=prod,
                    tipo='DEVOLUCION_ANULACION',
                    cantidad=detalle.cantidad,
                    stock_anterior=stock_previo,
                    stock_nuevo=prod.stock,
                    factura=self,
                    motivo=f"Reposición de stock por anulación de factura {self.numero_factura}"
                )


class DetalleFactura(models.Model):
    """
    Renglón o ítem individual de una factura.
    """
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE, related_name='detalles', verbose_name="Factura")
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name='detalles_factura', verbose_name="Producto")
    codigo_producto = models.CharField(max_length=50, verbose_name="Código")
    nombre_producto = models.CharField(max_length=200, verbose_name="Descripción del Producto")
    cantidad = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Cantidad")
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Precio Unitario")
    tarifa_iva = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('15.00'), verbose_name="Tarifa IVA (%)")
    descuento = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Descuento")
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Subtotal")
    valor_iva = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Valor IVA")
    total = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Total Línea")

    class Meta:
        verbose_name = "Detalle de Factura"
        verbose_name_plural = "Detalles de Factura"

    def __str__(self):
        return f"{self.cantidad} x {self.nombre_producto} (Factura {self.factura.numero_factura})"


class MovimientoInventario(models.Model):
    """
    Registro histórico (Kardex) de entradas y salidas de inventario.
    Se crea automáticamente cuando un producto es facturado para reducir el stock.
    """
    TIPO_CHOICES = [
        ('INGRESO', 'Ingreso / Reabastecimiento'),
        ('EGRESO_VENTA', 'Egreso por Facturación'),
        ('AJUSTE', 'Ajuste manual de inventario'),
        ('DEVOLUCION_ANULACION', 'Reposición por Anulación de Factura'),
    ]

    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='movimientos', verbose_name="Producto")
    tipo = models.CharField(max_length=25, choices=TIPO_CHOICES, verbose_name="Tipo de Movimiento")
    cantidad = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Cantidad")
    stock_anterior = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Stock Anterior")
    stock_nuevo = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Stock Resultante")
    factura = models.ForeignKey(Factura, null=True, blank=True, on_delete=models.SET_NULL, related_name='movimientos', verbose_name="Factura Asociada")
    motivo = models.CharField(max_length=255, verbose_name="Motivo o Justificación")
    fecha = models.DateTimeField(auto_now_add=True, verbose_name="Fecha y Hora")

    class Meta:
        verbose_name = "Movimiento de Inventario"
        verbose_name_plural = "Movimientos de Inventario"
        ordering = ['-fecha', '-id']

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.producto.nombre}: {self.cantidad} ({self.fecha.strftime('%d/%m/%Y %H:%M')})"


class PerfilUsuario(models.Model):
    """
    Perfil de usuario con roles de acceso:
    - ADMINISTRADOR: Acceso total al sistema
    - ASESOR: Emisión de facturas, clientes, y consulta
    - BODEGUERO: Gestión de productos e inventario
    """
    ROL_ADMIN = 'ADMINISTRADOR'
    ROL_ASESOR = 'ASESOR'
    ROL_BODEGUERO = 'BODEGUERO'

    ROL_CHOICES = [
        (ROL_ADMIN, 'Administrador (Acceso Total)'),
        (ROL_ASESOR, 'Asesor Comercial (Facturación)'),
        (ROL_BODEGUERO, 'Bodeguero (Gestión de Inventario)'),
    ]

    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default=ROL_ASESOR, verbose_name="Rol en el Sistema")

    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuarios"

    def __str__(self):
        return f"{self.usuario.username} - {self.get_rol_display()}"

    @property
    def es_admin(self):
        return self.rol == self.ROL_ADMIN or self.usuario.is_superuser

    @property
    def es_asesor(self):
        return self.rol in [self.ROL_ADMIN, self.ROL_ASESOR] or self.usuario.is_superuser

    @property
    def es_bodeguero(self):
        return self.rol in [self.ROL_ADMIN, self.ROL_BODEGUERO] or self.usuario.is_superuser


@receiver(post_save, sender=User)
def asegurar_perfil_usuario(sender, instance, created, **kwargs):
    """Crea automáticamente el perfil del usuario si no existe."""
    if created:
        rol_inicial = PerfilUsuario.ROL_ADMIN if instance.is_superuser else PerfilUsuario.ROL_ASESOR
        PerfilUsuario.objects.get_or_create(usuario=instance, defaults={'rol': rol_inicial})
