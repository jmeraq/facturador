from decimal import Decimal
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.urls import reverse

from django.contrib.auth.models import User
from .models import Emisor, Cliente, Producto, Factura, DetalleFactura, MovimientoInventario, PerfilUsuario
from .services import FacturacionService, InventarioService
from .validators import validar_cedula_ecuador, validar_ruc_ecuador


class FacturadorEcuadorTestCase(TestCase):
    def setUp(self):
        # 1. Configurar Emisor
        self.emisor = Emisor.get_emisor()
        self.emisor.ruc = "1790012345001"
        self.emisor.razon_social = "PRUEBAS CORP S.A."
        self.emisor.secuencial_actual = 1
        self.emisor.save()

        # 2. Configurar Clientes
        self.cliente_final = Cliente.objects.create(
            tipo_identificacion='07',
            identificacion='9999999999999',
            nombres='CONSUMIDOR FINAL'
        )

        self.cliente_natural = Cliente.objects.create(
            tipo_identificacion='05',
            identificacion='1710034065',
            nombres='JUAN PEREZ'
        )

        # 3. Configurar Productos e Inventario
        self.prod_laptop = Producto.objects.create(
            codigo='LAP-TEST',
            nombre='Laptop de Prueba',
            precio_unitario=Decimal('100.00'),
            tarifa_iva=Decimal('15.00'),
            stock=Decimal('10.00'),
            stock_minimo=Decimal('2.00')
        )

        self.prod_medicina = Producto.objects.create(
            codigo='MED-TEST',
            nombre='Medicina Tarifa 0%',
            precio_unitario=Decimal('50.00'),
            tarifa_iva=Decimal('0.00'),
            stock=Decimal('20.00'),
            stock_minimo=Decimal('5.00')
        )

    def test_validador_cedula_ecuador(self):
        """Verifica la validación del algoritmo de cédula ecuatoriana."""
        self.assertTrue(validar_cedula_ecuador('1710034065'))
        self.assertFalse(validar_cedula_ecuador('1710034066'))  # dígito verificador inválido
        self.assertFalse(validar_cedula_ecuador('9999999999'))
        self.assertFalse(validar_cedula_ecuador('123'))

    def test_validador_ruc_ecuador(self):
        """Verifica validación de RUC personas naturales, jurídicas y consumidor final."""
        self.assertTrue(validar_ruc_ecuador('1710034065001'))  # Persona natural
        self.assertTrue(validar_ruc_ecuador('9999999999999'))  # Consumidor final
        self.assertFalse(validar_ruc_ecuador('1710034065000')) # Sucursal 000 es inválida

    def test_emision_factura_reduce_inventario(self):
        """
        Regla central: Al emitir una factura, el inventario del producto
        debe reducirse en la cantidad facturada de forma atómica.
        """
        stock_inicial = self.prod_laptop.stock  # 10

        items = [
            {
                'producto_id': self.prod_laptop.id,
                'cantidad': Decimal('3.00'),
                'precio_unitario': self.prod_laptop.precio_unitario,
                'descuento': Decimal('0.00')
            }
        ]

        factura = FacturacionService.emitir_factura(
            cliente=self.cliente_natural,
            items=items,
            forma_pago='01',
            observaciones="Venta de prueba"
        )

        # 1. Verificar número de factura
        self.assertEqual(factura.numero_factura, "001-001-000000001")
        self.assertEqual(factura.estado, 'EMITIDA')

        # 2. Verificar reducción de stock
        self.prod_laptop.refresh_from_db()
        self.assertEqual(self.prod_laptop.stock, Decimal('7.00'))  # 10 - 3 = 7

        # 3. Verificar cálculo de IVA 15% y Totales
        # Subtotal: 3 * 100 = 300.00
        # IVA 15%: 300 * 0.15 = 45.00
        # Total: 345.00
        self.assertEqual(factura.subtotal_15, Decimal('300.00'))
        self.assertEqual(factura.subtotal_0, Decimal('0.00'))
        self.assertEqual(factura.subtotal_sin_impuestos, Decimal('300.00'))
        self.assertEqual(factura.iva_15, Decimal('45.00'))
        self.assertEqual(factura.total, Decimal('345.00'))

        # 4. Verificar registro en el Kardex / Auditoría de Inventario
        mov = MovimientoInventario.objects.filter(factura=factura).first()
        self.assertIsNotNone(mov)
        self.assertEqual(mov.tipo, 'EGRESO_VENTA')
        self.assertEqual(mov.cantidad, Decimal('3.00'))
        self.assertEqual(mov.stock_anterior, Decimal('10.00'))
        self.assertEqual(mov.stock_nuevo, Decimal('7.00'))

    def test_factura_mixta_iva15_y_iva0(self):
        """Verifica el cálculo de factura con productos de IVA 15% e IVA 0%."""
        items = [
            {'producto_id': self.prod_laptop.id, 'cantidad': Decimal('1.00')},   # $100 + 15% IVA = $115
            {'producto_id': self.prod_medicina.id, 'cantidad': Decimal('2.00')}, # 2 * $50 = $100 (0% IVA)
        ]

        factura = FacturacionService.emitir_factura(
            cliente=self.cliente_final,
            items=items
        )

        self.assertEqual(factura.subtotal_15, Decimal('100.00'))
        self.assertEqual(factura.subtotal_0, Decimal('100.00'))
        self.assertEqual(factura.subtotal_sin_impuestos, Decimal('200.00'))
        self.assertEqual(factura.iva_15, Decimal('15.00'))
        self.assertEqual(factura.total, Decimal('215.00'))

    def test_rechazo_por_stock_insuficiente(self):
        """Si se intenta facturar más de lo disponible, debe lanzar error y no modificar el stock."""
        items = [
            {'producto_id': self.prod_laptop.id, 'cantidad': Decimal('50.00')}  # Solo hay 10
        ]

        with self.assertRaises(ValidationError):
            FacturacionService.emitir_factura(cliente=self.cliente_natural, items=items)

        # El stock no debe haber cambiado
        self.prod_laptop.refresh_from_db()
        self.assertEqual(self.prod_laptop.stock, Decimal('10.00'))

    def test_anular_factura_repone_inventario(self):
        """Al anular una factura, los productos deben reponerse en el inventario."""
        items = [{'producto_id': self.prod_laptop.id, 'cantidad': Decimal('4.00')}]
        factura = FacturacionService.emitir_factura(cliente=self.cliente_natural, items=items)

        self.prod_laptop.refresh_from_db()
        self.assertEqual(self.prod_laptop.stock, Decimal('6.00'))

        # Anular factura
        factura.anular(motivo="Cliente canceló compra")
        self.assertEqual(factura.estado, 'ANULADA')

        # Stock debe volver a 10
        self.prod_laptop.refresh_from_db()
        self.assertEqual(self.prod_laptop.stock, Decimal('10.00'))

        # Registro de devolución en inventario
        mov_anulacion = MovimientoInventario.objects.filter(tipo='DEVOLUCION_ANULACION', factura=factura).first()
        self.assertIsNotNone(mov_anulacion)
        self.assertEqual(mov_anulacion.stock_nuevo, Decimal('10.00'))

    def test_vistas_requieren_autenticacion(self):
        """Verifica que las rutas protegidas redirigen al login si el usuario no está autenticado."""
        response_dash = self.client.get(reverse('dashboard'))
        self.assertRedirects(response_dash, f"{reverse('login')}?next={reverse('dashboard')}")

        response_fac = self.client.get(reverse('factura_crear'))
        self.assertRedirects(response_fac, reverse('login'))

    def test_rol_administrador_acceso_total(self):
        """El administrador tiene acceso irrestricto a todos los módulos."""
        admin_user = User.objects.create_user(username='admin_test', password='123')
        admin_user.perfil.rol = PerfilUsuario.ROL_ADMIN
        admin_user.perfil.save()
        self.client.login(username='admin_test', password='123')

        # Puede acceder a Dashboard, Productos, Inventario, Facturación y Configuración
        for url_name in ['dashboard', 'producto_lista', 'producto_crear', 'inventario_dashboard', 'factura_lista', 'factura_crear', 'emisor_configuracion']:
            resp = self.client.get(reverse(url_name))
            self.assertEqual(resp.status_code, 200, f"Admin no pudo acceder a {url_name}")

    def test_rol_asesor_permisos_y_restricciones(self):
        """El asesor puede facturar y ver clientes, pero no puede gestionar inventario ni emisor."""
        asesor_user = User.objects.create_user(username='asesor_test', password='123')
        asesor_user.perfil.rol = PerfilUsuario.ROL_ASESOR
        asesor_user.perfil.save()
        self.client.login(username='asesor_test', password='123')

        # Permitido: Facturas y Clientes
        self.assertEqual(self.client.get(reverse('factura_crear')).status_code, 200)
        self.assertEqual(self.client.get(reverse('factura_lista')).status_code, 200)
        self.assertEqual(self.client.get(reverse('cliente_lista')).status_code, 200)

        # Denegado: Inventario, crear producto, configuración emisor -> Redirigen a dashboard
        resp_inv = self.client.get(reverse('inventario_dashboard'))
        self.assertRedirects(resp_inv, reverse('dashboard'))

        resp_prod_crear = self.client.get(reverse('producto_crear'))
        self.assertRedirects(resp_prod_crear, reverse('dashboard'))

        resp_emisor = self.client.get(reverse('emisor_configuracion'))
        self.assertRedirects(resp_emisor, reverse('dashboard'))

    def test_rol_bodeguero_permisos_y_restricciones(self):
        """El bodeguero gestiona inventario y productos, pero no puede facturar ni configurar emisor."""
        bodeguero_user = User.objects.create_user(username='bodeguero_test', password='123')
        bodeguero_user.perfil.rol = PerfilUsuario.ROL_BODEGUERO
        bodeguero_user.perfil.save()
        self.client.login(username='bodeguero_test', password='123')

        # Permitido: Inventario y gestión de productos
        self.assertEqual(self.client.get(reverse('inventario_dashboard')).status_code, 200)
        self.assertEqual(self.client.get(reverse('producto_lista')).status_code, 200)
        self.assertEqual(self.client.get(reverse('producto_crear')).status_code, 200)

        # Denegado: Facturación y configuración de emisor -> Redirigen a dashboard
        resp_fac = self.client.get(reverse('factura_crear'))
        self.assertRedirects(resp_fac, reverse('dashboard'))

        resp_emisor = self.client.get(reverse('emisor_configuracion'))
        self.assertRedirects(resp_emisor, reverse('dashboard'))
