from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from facturacion.models import Emisor, Cliente, Producto, MovimientoInventario, PerfilUsuario


class Command(BaseCommand):
    help = "Puebla datos iniciales de prueba para el facturador ecuatoriano (Usuarios con Roles, Emisor, Clientes, Productos e Inventario)."

    def handle(self, *args, **options):
        self.stdout.write("Creando usuarios con roles de acceso...")
        usuarios_data = [
            {
                'username': 'admin',
                'password': 'admin123',
                'first_name': 'Administrador',
                'last_name': 'General',
                'email': 'admin@facturador.ec',
                'is_staff': True,
                'is_superuser': True,
                'rol': PerfilUsuario.ROL_ADMIN,
            },
            {
                'username': 'asesor',
                'password': 'asesor123',
                'first_name': 'Asesor',
                'last_name': 'Comercial',
                'email': 'asesor@facturador.ec',
                'is_staff': False,
                'is_superuser': False,
                'rol': PerfilUsuario.ROL_ASESOR,
            },
            {
                'username': 'bodeguero',
                'password': 'bodeguero123',
                'first_name': 'Bodeguero',
                'last_name': 'Almacén',
                'email': 'bodeguero@facturador.ec',
                'is_staff': False,
                'is_superuser': False,
                'rol': PerfilUsuario.ROL_BODEGUERO,
            },
        ]

        for u_data in usuarios_data:
            rol = u_data.pop('rol')
            password = u_data.pop('password')
            user, created = User.objects.get_or_create(username=u_data['username'], defaults=u_data)
            user.set_password(password)
            for k, v in u_data.items():
                setattr(user, k, v)
            user.save()

            perfil, _ = PerfilUsuario.objects.get_or_create(usuario=user)
            perfil.rol = rol
            perfil.save()
            self.stdout.write(f"  ✓ Usuario '{user.username}' configurado con rol: {perfil.get_rol_display()}")

        self.stdout.write("Configurando datos del Emisor...")
        emisor = Emisor.get_emisor()
        emisor.ruc = "1790012345001"
        emisor.razon_social = "DISTRIBUIDORA COMERCIAL ANDINA S.A.S."
        emisor.nombre_comercial = "ANDINA TECH ECUADOR"
        emisor.direccion_matriz = "Av. Amazonas N36-152 y Naciones Unidas, Edificio Titanium, Quito - Ecuador"
        emisor.establecimiento = "001"
        emisor.punto_emision = "001"
        emisor.tarifa_iva_defecto = Decimal('15.00')
        emisor.obligado_contabilidad = True
        emisor.es_contribuyente_rimpe = True
        emisor.save()

        self.stdout.write("Registrando clientes de ejemplo...")
        clientes_data = [
            {
                'tipo_identificacion': '07',
                'identificacion': '9999999999999',
                'nombres': 'CONSUMIDOR FINAL',
                'email': 'consumidor@final.ec',
                'telefono': '0999999999',
                'direccion': 'Ecuador'
            },
            {
                'tipo_identificacion': '05',
                'identificacion': '1710034065',
                'nombres': 'ING. CARLOS ANDRÉS MERA ZAMBRANO',
                'email': 'carlos.mera@ejemplo.com',
                'telefono': '0984567890',
                'direccion': 'Cumbayá, Paseo San Francisco, Quito'
            },
            {
                'tipo_identificacion': '04',
                'identificacion': '1710034065001',
                'nombres': 'TECNOLOGÍA & SERVICIOS INTEGRALES S.A.',
                'email': 'facturacion@tecnointegrales.ec',
                'telefono': '022345678',
                'direccion': 'Av. República del Salvador y Shirys, Quito'
            }
        ]

        for c_data in clientes_data:
            Cliente.objects.update_or_create(
                identificacion=c_data['identificacion'],
                defaults=c_data
            )

        self.stdout.write("Registrando catálogo de productos e inicializando inventario...")
        productos_data = [
            {
                'codigo': 'LAP-001',
                'nombre': 'Laptop HP ProBook 450 G9 (16GB RAM, 512GB SSD)',
                'descripcion': 'Procesador Intel Core i7 12va Gen, Pantalla 15.6 FHD, Windows 11 Pro',
                'precio_unitario': Decimal('780.00'),
                'tarifa_iva': Decimal('15.00'),
                'stock': Decimal('12.00'),
                'stock_minimo': Decimal('3.00'),
            },
            {
                'codigo': 'MOU-002',
                'nombre': 'Mouse Inalámbrico Logitech M170 Óptico',
                'descripcion': 'Conexión 2.4GHz USB nanoreceptor, batería hasta 12 meses',
                'precio_unitario': Decimal('12.50'),
                'tarifa_iva': Decimal('15.00'),
                'stock': Decimal('45.00'),
                'stock_minimo': Decimal('10.00'),
            },
            {
                'codigo': 'MON-003',
                'nombre': 'Monitor Dell 24" UltraSharp IPS Full HD',
                'descripcion': 'Resolución 1920x1080, HDMI, DisplayPort, base ajustable en altura',
                'precio_unitario': Decimal('185.00'),
                'tarifa_iva': Decimal('15.00'),
                'stock': Decimal('7.00'),
                'stock_minimo': Decimal('2.00'),
            },
            {
                'codigo': 'TEC-004',
                'nombre': 'Teclado Mecánico RGB Redragon Switch Azul',
                'descripcion': 'Teclado compacto para oficina y gaming con retroiluminación',
                'precio_unitario': Decimal('39.00'),
                'tarifa_iva': Decimal('15.00'),
                'stock': Decimal('18.00'),
                'stock_minimo': Decimal('5.00'),
            },
            {
                'codigo': 'MED-005',
                'nombre': 'Botiquín de Primeros Auxilios / Insumos Médicos',
                'descripcion': 'Kit completo para empresas con gasas, alcohol, vendas (Tarifa IVA 0%)',
                'precio_unitario': Decimal('25.00'),
                'tarifa_iva': Decimal('0.00'), # Tarifa 0% para probar ambas tarifas
                'stock': Decimal('25.00'),
                'stock_minimo': Decimal('5.00'),
            },
            {
                'codigo': 'IMP-006',
                'nombre': 'Impresora Multifunción Epson EcoTank L3250 WiFi',
                'descripcion': 'Sistema de tanque de tinta continuo, escáner, copiadora, conectividad WiFi',
                'precio_unitario': Decimal('210.00'),
                'tarifa_iva': Decimal('15.00'),
                'stock': Decimal('3.00'), # Alerta de stock bajo!
                'stock_minimo': Decimal('5.00'),
            },
            {
                'codigo': 'SSD-007',
                'nombre': 'Disco Sólido SSD NVMe Kingston 1TB PCIe 4.0',
                'descripcion': 'Velocidad hasta 3500MB/s de lectura',
                'precio_unitario': Decimal('72.00'),
                'tarifa_iva': Decimal('15.00'),
                'stock': Decimal('0.00'), # Agotado para probar validación
                'stock_minimo': Decimal('5.00'),
            },
        ]

        for p_data in productos_data:
            stock_inicial = p_data['stock']
            producto, created = Producto.objects.update_or_create(
                codigo=p_data['codigo'],
                defaults=p_data
            )
            if created and stock_inicial > Decimal('0.00'):
                MovimientoInventario.objects.create(
                    producto=producto,
                    tipo='INGRESO',
                    cantidad=stock_inicial,
                    stock_anterior=Decimal('0.00'),
                    stock_nuevo=stock_inicial,
                    motivo="Inventario inicial cargado por comando del sistema"
                )

        self.stdout.write(self.style.SUCCESS("✓ Datos iniciales de prueba cargados exitosamente."))
