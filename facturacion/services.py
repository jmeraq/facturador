from decimal import Decimal, ROUND_HALF_UP
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Emisor, Cliente, Producto, Factura, DetalleFactura, MovimientoInventario


def redondear(valor: Decimal) -> Decimal:
    """Aplica redondeo comercial a 2 decimales."""
    return valor.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


class FacturacionService:
    """
    Controlador / Servicio de Negocio para el proceso de Facturación e Inventario.
    Asegura integridad transaccional (ACID) y reducción automática de stock.
    """

    @classmethod
    @transaction.atomic
    def emitir_factura(cls, cliente: Cliente, items: list[dict], forma_pago: str = '01', observaciones: str = '') -> Factura:
        """
        Emite una factura y reduce el inventario correspondiente.
        items: lista de diccionarios con formato:
        [
            {
                'producto_id': 1,
                'cantidad': Decimal('2.00'),
                'descuento': Decimal('0.00'), # opcional
                'precio_unitario': Decimal('10.50'), # opcional, si no se pasa usa el del producto
            },
            ...
        ]
        """
        if not items:
            raise ValidationError("Debe incluir al menos un producto en la factura.")

        emisor = Emisor.get_emisor()
        numero_factura = emisor.obtener_siguiente_numero()
        secuencial = emisor.secuencial_actual

        # Crear cabecera inicial de la factura
        factura = Factura.objects.create(
            numero_factura=numero_factura,
            secuencial=secuencial,
            cliente=cliente,
            fecha_emision=timezone.now(),
            forma_pago=forma_pago,
            estado='EMITIDA',
            observaciones=observaciones.strip()
        )

        subtotal_15 = Decimal('0.00')
        subtotal_0 = Decimal('0.00')
        descuento_acumulado = Decimal('0.00')
        iva_15_acumulado = Decimal('0.00')

        # Procesar cada ítem con bloqueo de fila select_for_update() para evitar condiciones de carrera
        for idx, item in enumerate(items, start=1):
            prod_id = item.get('producto_id')
            if not prod_id:
                raise ValidationError(f"Línea #{idx}: Producto no especificado.")

            try:
                # Bloqueo a nivel de base de datos para control de concurrencia
                producto = Producto.objects.select_for_update().get(id=prod_id, activo=True)
            except Producto.DoesNotExist:
                raise ValidationError(f"Línea #{idx}: El producto seleccionado no existe o está inactivo.")

            cantidad = Decimal(str(item.get('cantidad', 1)))
            if cantidad <= Decimal('0.00'):
                raise ValidationError(f"Línea #{idx} ({producto.nombre}): La cantidad debe ser mayor a 0.")

            # VALIDACIÓN ESTRICTA DE INVENTARIO
            if not producto.tiene_stock_suficiente(cantidad):
                raise ValidationError(
                    f"Stock insuficiente para '{producto.nombre}'. "
                    f"Disponible en inventario: {producto.stock}, Solicitado: {cantidad}."
                )

            precio_unitario = Decimal(str(item.get('precio_unitario', producto.precio_unitario)))
            if precio_unitario < Decimal('0.00'):
                raise ValidationError(f"Línea #{idx} ({producto.nombre}): El precio no puede ser negativo.")

            descuento = Decimal(str(item.get('descuento', Decimal('0.00'))))
            if descuento < Decimal('0.00'):
                descuento = Decimal('0.00')

            subtotal_linea = redondear((cantidad * precio_unitario) - descuento)
            if subtotal_linea < Decimal('0.00'):
                subtotal_linea = Decimal('0.00')

            tarifa = producto.tarifa_iva
            if tarifa > Decimal('0.00'):
                iva_linea = redondear(subtotal_linea * (tarifa / Decimal('100.00')))
                subtotal_15 += subtotal_linea
                iva_15_acumulado += iva_linea
            else:
                iva_linea = Decimal('0.00')
                subtotal_0 += subtotal_linea

            total_linea = subtotal_linea + iva_linea
            descuento_acumulado += descuento

            # Guardar el detalle de la factura
            DetalleFactura.objects.create(
                factura=factura,
                producto=producto,
                codigo_producto=producto.codigo,
                nombre_producto=producto.nombre,
                cantidad=cantidad,
                precio_unitario=precio_unitario,
                tarifa_iva=tarifa,
                descuento=descuento,
                subtotal=subtotal_linea,
                valor_iva=iva_linea,
                total=total_linea
            )

            # REDUCCIÓN DE INVENTARIO AUTOMÁTICA
            stock_previo = producto.stock
            stock_nuevo = stock_previo - cantidad
            producto.stock = stock_nuevo
            producto.save(update_fields=['stock'])

            # REGISTRO EN KARDEX / AUDITORÍA DE INVENTARIO
            MovimientoInventario.objects.create(
                producto=producto,
                tipo='EGRESO_VENTA',
                cantidad=cantidad,
                stock_anterior=stock_previo,
                stock_nuevo=stock_nuevo,
                factura=factura,
                motivo=f"Factura #{factura.numero_factura} emitida a {cliente.nombres}"
            )

        # Actualizar totales en la cabecera de la factura
        subtotal_sin_impuestos = subtotal_15 + subtotal_0
        total_factura = subtotal_sin_impuestos + iva_15_acumulado

        factura.subtotal_15 = redondear(subtotal_15)
        factura.subtotal_0 = redondear(subtotal_0)
        factura.subtotal_sin_impuestos = redondear(subtotal_sin_impuestos)
        factura.descuento_total = redondear(descuento_acumulado)
        factura.iva_15 = redondear(iva_15_acumulado)
        factura.total = redondear(total_factura)
        factura.save()

        # Incrementar el secuencial del emisor para la siguiente factura
        emisor.secuencial_actual += 1
        emisor.save(update_fields=['secuencial_actual'])

        return factura


class InventarioService:
    """
    Servicio para operaciones manuales y trazabilidad de inventario.
    """

    @classmethod
    @transaction.atomic
    def agregar_stock(cls, producto: Producto, cantidad: Decimal, motivo: str = "Reabastecimiento") -> MovimientoInventario:
        """Incrementa el stock de un producto y registra en auditoría."""
        if cantidad <= Decimal('0.00'):
            raise ValidationError("La cantidad a ingresar debe ser mayor que 0.")

        stock_anterior = producto.stock
        stock_nuevo = stock_anterior + cantidad
        producto.stock = stock_nuevo
        producto.save(update_fields=['stock'])

        return MovimientoInventario.objects.create(
            producto=producto,
            tipo='INGRESO',
            cantidad=cantidad,
            stock_anterior=stock_anterior,
            stock_nuevo=stock_nuevo,
            motivo=motivo
        )

    @classmethod
    @transaction.atomic
    def ajustar_stock(cls, producto: Producto, nuevo_stock: Decimal, motivo: str = "Ajuste físico de inventario") -> MovimientoInventario:
        """Ajusta directamente el stock a un valor específico."""
        if nuevo_stock < Decimal('0.00'):
            raise ValidationError("El stock resultante no puede ser negativo.")

        stock_anterior = producto.stock
        diferencia = nuevo_stock - stock_anterior
        producto.stock = nuevo_stock
        producto.save(update_fields=['stock'])

        return MovimientoInventario.objects.create(
            producto=producto,
            tipo='AJUSTE',
            cantidad=abs(diferencia),
            stock_anterior=stock_anterior,
            stock_nuevo=nuevo_stock,
            motivo=f"{motivo} ({'+' if diferencia >= 0 else ''}{diferencia})"
        )
