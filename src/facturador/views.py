import json
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from django.core.exceptions import ValidationError

from .models import Emisor, Cliente, Producto, Factura, DetalleFactura, MovimientoInventario, PerfilUsuario
from .forms import ProductoForm, ClienteForm, EmisorForm, InventarioMovimientoForm
from .services import FacturacionService, InventarioService
from .decorators import rol_requerido, admin_requerido, asesor_o_admin, bodeguero_o_admin


# ==========================================
# 0. AUTENTICACIÓN (LOGIN / LOGOUT)
# ==========================================
def login_view(request):
    """Inicio de sesión con soporte de roles."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            # Asegurar perfil
            perfil, _ = PerfilUsuario.objects.get_or_create(
                usuario=user,
                defaults={'rol': PerfilUsuario.ROL_ADMIN if user.is_superuser else PerfilUsuario.ROL_ASESOR}
            )
            messages.success(request, f"¡Bienvenido, {user.first_name or user.username}! Sesión iniciada con rol: {perfil.get_rol_display()}.")
            next_url = request.GET.get('next') or request.POST.get('next') or 'dashboard'
            return redirect(next_url)
        else:
            messages.error(request, "Usuario o contraseña incorrectos. Verifica tus credenciales.")

    return render(request, 'facturador/login.html')


def logout_view(request):
    """Cierre de sesión seguro."""
    auth_logout(request)
    messages.info(request, "Has cerrado tu sesión de forma segura.")
    return redirect('login')


# ==========================================
# 1. DASHBOARD
# ==========================================
@login_required
def dashboard(request):
    """Vista principal con métricas y accesos directos según el rol."""
    hoy = timezone.now()
    inicio_mes = hoy.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Métricas
    facturas_mes = Factura.objects.filter(fecha_emision__gte=inicio_mes, estado='EMITIDA')
    total_facturado_mes = facturas_mes.aggregate(total=Sum('total'))['total'] or Decimal('0.00')
    num_facturas_mes = facturas_mes.count()

    total_productos = Producto.objects.filter(activo=True).count()
    num_productos_bajo_stock = Producto.objects.filter(activo=True, stock__lte=F('stock_minimo')).count()
    productos_alerta = list(Producto.objects.filter(activo=True, stock__lte=F('stock_minimo')).order_by('stock')[:5])

    ultimas_facturas = Factura.objects.select_related('cliente').order_by('-fecha_emision')[:6]
    ultimos_movimientos = MovimientoInventario.objects.select_related('producto', 'factura').order_by('-fecha')[:6]

    context = {
        'total_facturado_mes': total_facturado_mes,
        'num_facturas_mes': num_facturas_mes,
        'total_productos': total_productos,
        'num_productos_bajo_stock': num_productos_bajo_stock,
        'productos_alerta': productos_alerta,
        'ultimas_facturas': ultimas_facturas,
        'ultimos_movimientos': ultimos_movimientos,
        'emisor': Emisor.get_emisor(),
    }
    return render(request, 'facturador/dashboard.html', context)


# ==========================================
# 2. PRODUCTOS
# ==========================================
@login_required
def producto_lista(request):
    """
    Listado y filtro de productos.
    Accesible para todos los roles (Asesor puede consultar precios/stock, Bodeguero y Admin pueden gestionar).
    """
    q = request.GET.get('q', '').strip()
    filtro_stock = request.GET.get('stock', '')

    productos = Producto.objects.all().order_by('nombre')
    if q:
        productos = productos.filter(Q(nombre__icontains=q) | Q(codigo__icontains=q) | Q(descripcion__icontains=q))

    if filtro_stock == 'bajo':
        productos = [p for p in productos if p.stock_bajo]
    elif filtro_stock == 'agotado':
        productos = productos.filter(stock__lte=0)

    context = {
        'productos': productos,
        'q': q,
        'filtro_stock': filtro_stock,
    }
    return render(request, 'facturador/producto_lista.html', context)


@bodeguero_o_admin
def producto_crear(request):
    """Crear un nuevo producto (Bodeguero o Administrador)."""
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            producto = form.save()
            if producto.stock > Decimal('0.00'):
                MovimientoInventario.objects.create(
                    producto=producto,
                    tipo='INGRESO',
                    cantidad=producto.stock,
                    stock_anterior=Decimal('0.00'),
                    stock_nuevo=producto.stock,
                    motivo=f"Inventario inicial registrado por {request.user.username}"
                )
            messages.success(request, f"Producto '{producto.nombre}' creado con éxito.")
            return redirect('producto_lista')
    else:
        form = ProductoForm()

    return render(request, 'facturador/producto_form.html', {'form': form, 'titulo': 'Nuevo Producto'})


@bodeguero_o_admin
def producto_editar(request, pk):
    """Editar producto existente (Bodeguero o Administrador)."""
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, f"Producto '{producto.nombre}' actualizado.")
            return redirect('producto_lista')
    else:
        form = ProductoForm(instance=producto)

    return render(request, 'facturador/producto_form.html', {'form': form, 'titulo': 'Editar Producto', 'producto': producto})


@bodeguero_o_admin
def producto_eliminar(request, pk):
    """Desactiva o elimina un producto (Bodeguero o Administrador)."""
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        nombre = producto.nombre
        if producto.detalles_factura.exists():
            producto.activo = False
            producto.save(update_fields=['activo'])
            messages.info(request, f"El producto '{nombre}' tiene facturas asociadas, por lo que fue desactivado.")
        else:
            producto.delete()
            messages.success(request, f"Producto '{nombre}' eliminado correctamente.")
        return redirect('producto_lista')

    return render(request, 'facturador/confirmar_eliminar.html', {
        'objeto': producto,
        'tipo': 'Producto',
        'cancelar_url': 'producto_lista'
    })


# ==========================================
# 3. INVENTARIO (KARDEX & AJUSTES)
# ==========================================
@bodeguero_o_admin
def inventario_dashboard(request):
    """Vista de control de inventario y Kardex (Bodeguero o Administrador)."""
    if request.method == 'POST':
        form = InventarioMovimientoForm(request.POST)
        if form.is_valid():
            producto = form.cleaned_data['producto']
            tipo_op = form.cleaned_data['tipo_operacion']
            cantidad = form.cleaned_data['cantidad']
            motivo = form.cleaned_data['motivo']
            motivo_completo = f"{motivo} (registrado por {request.user.username})"

            try:
                if tipo_op == 'INGRESO':
                    InventarioService.agregar_stock(producto, cantidad, motivo_completo)
                    messages.success(request, f"Se agregaron {cantidad} unidades al producto '{producto.nombre}'.")
                elif tipo_op == 'AJUSTE':
                    InventarioService.ajustar_stock(producto, cantidad, motivo_completo)
                    messages.success(request, f"Se ajustó el stock de '{producto.nombre}' a {cantidad} unidades.")
                return redirect('inventario_dashboard')
            except ValidationError as e:
                messages.error(request, str(e))
    else:
        form = InventarioMovimientoForm()

    # Filtro de movimientos
    prod_filter = request.GET.get('producto_id', '')
    movimientos = MovimientoInventario.objects.select_related('producto', 'factura').all()
    if prod_filter:
        movimientos = movimientos.filter(producto_id=prod_filter)

    productos = Producto.objects.filter(activo=True).order_by('nombre')
    productos_alerta = [p for p in productos if p.stock_bajo]

    context = {
        'form': form,
        'movimientos': movimientos[:50],
        'productos': productos,
        'productos_alerta': productos_alerta,
        'prod_filter': prod_filter,
    }
    return render(request, 'facturador/inventario_dashboard.html', context)


# ==========================================
# 4. CLIENTES
# ==========================================
@asesor_o_admin
def cliente_lista(request):
    """Listado de clientes registrados (Asesor o Administrador)."""
    q = request.GET.get('q', '').strip()
    clientes = Cliente.objects.all().order_by('nombres')
    if q:
        clientes = clientes.filter(Q(nombres__icontains=q) | Q(identificacion__icontains=q))

    return render(request, 'facturador/cliente_lista.html', {'clientes': clientes, 'q': q})


@asesor_o_admin
def cliente_crear(request):
    """Crear un nuevo cliente (Asesor o Administrador)."""
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save()
            messages.success(request, f"Cliente '{cliente.nombres}' registrado correctamente.")
            return redirect('cliente_lista')
    else:
        form = ClienteForm()

    return render(request, 'facturador/cliente_form.html', {'form': form, 'titulo': 'Nuevo Cliente'})


@asesor_o_admin
def cliente_editar(request, pk):
    """Editar datos de cliente (Asesor o Administrador)."""
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, f"Datos de '{cliente.nombres}' actualizados.")
            return redirect('cliente_lista')
    else:
        form = ClienteForm(instance=cliente)

    return render(request, 'facturador/cliente_form.html', {'form': form, 'titulo': 'Editar Cliente', 'cliente': cliente})


# ==========================================
# 5. FACTURACIÓN
# ==========================================
@asesor_o_admin
def factura_lista(request):
    """Historial de facturas emitidas (Asesor o Administrador)."""
    q = request.GET.get('q', '').strip()
    estado = request.GET.get('estado', '')

    facturas = Factura.objects.select_related('cliente').all().order_by('-fecha_emision')
    if q:
        facturas = facturas.filter(
            Q(numero_factura__icontains=q) |
            Q(cliente__nombres__icontains=q) |
            Q(cliente__identificacion__icontains=q)
        )
    if estado:
        facturas = facturas.filter(estado=estado)

    context = {
        'facturas': facturas,
        'q': q,
        'estado': estado,
    }
    return render(request, 'facturador/factura_lista.html', context)


@asesor_o_admin
def factura_crear(request):
    """
    Formulario dinámico para emitir facturas con reducción automática de inventario.
    Accesible para Asesor o Administrador.
    """
    emisor = Emisor.get_emisor()
    clientes = Cliente.objects.all().order_by('nombres')
    productos = Producto.objects.filter(activo=True).order_by('nombre')

    # Garantizar que exista Consumidor Final
    consumidor_final, _ = Cliente.objects.get_or_create(
        identificacion='9999999999999',
        defaults={
            'tipo_identificacion': '07',
            'nombres': 'CONSUMIDOR FINAL',
            'direccion': 'Ecuador',
            'email': 'consumidor@final.ec'
        }
    )

    if request.method == 'POST':
        cliente_id = request.POST.get('cliente_id')
        forma_pago = request.POST.get('forma_pago', '01')
        observaciones = request.POST.get('observaciones', '')
        items_json = request.POST.get('items_json', '[]')

        try:
            if not cliente_id:
                raise ValidationError("Debe seleccionar un cliente.")

            cliente = Cliente.objects.get(id=cliente_id)
            items = json.loads(items_json)

            if not items:
                raise ValidationError("Debe agregar al menos un ítem a la factura.")

            # Llamada al servicio transaccional que valida stock y lo descuenta
            factura = FacturacionService.emitir_factura(
                cliente=cliente,
                items=items,
                forma_pago=forma_pago,
                observaciones=observaciones
            )

            messages.success(
                request,
                f"Factura #{factura.numero_factura} emitida con éxito. "
                f"El inventario de los productos facturados ha sido reducido automáticamente."
            )
            return redirect('factura_detalle', pk=factura.pk)

        except Cliente.DoesNotExist:
            messages.error(request, "El cliente seleccionado no existe.")
        except ValidationError as e:
            messages.error(request, str(e.message if hasattr(e, 'message') else e))
        except Exception as e:
            messages.error(request, f"Error al emitir factura: {str(e)}")

    context = {
        'emisor': emisor,
        'clientes': clientes,
        'productos': productos,
        'consumidor_final': consumidor_final,
        'siguiente_numero': emisor.obtener_siguiente_numero(),
        'formas_pago': Factura.FORMA_PAGO_CHOICES,
    }
    return render(request, 'facturador/factura_crear.html', context)


@login_required
def factura_detalle(request, pk):
    """
    Vista detallada de la factura, con formato listo para imprimir (RIDE SRI Ecuador).
    Accesible para todos los usuarios autenticados.
    """
    factura = get_object_or_404(Factura.objects.select_related('cliente'), pk=pk)
    detalles = factura.detalles.select_related('producto').all()
    emisor = Emisor.get_emisor()

    context = {
        'factura': factura,
        'detalles': detalles,
        'emisor': emisor,
    }
    return render(request, 'facturador/factura_detalle.html', context)


@asesor_o_admin
def factura_anular(request, pk):
    """
    Anula una factura emitida y repone automáticamente el inventario.
    Accesible para Asesor o Administrador.
    """
    factura = get_object_or_404(Factura, pk=pk)
    if request.method == 'POST':
        motivo = request.POST.get('motivo', 'Anulación solicitada por el usuario')
        try:
            factura.anular(motivo=f"{motivo} (por {request.user.username})")
            messages.warning(
                request,
                f"Factura #{factura.numero_factura} anulada exitosamente. "
                f"El inventario ha sido reabastecido automáticamente."
            )
        except ValidationError as e:
            messages.error(request, str(e))
        return redirect('factura_detalle', pk=factura.pk)

    return render(request, 'facturador/factura_anular_modal.html', {'factura': factura})


# ==========================================
# 6. CONFIGURACIÓN EMISOR
# ==========================================
@admin_requerido
def emisor_configuracion(request):
    """Configuración de datos de la empresa emisora (Solo Administrador)."""
    emisor = Emisor.get_emisor()
    if request.method == 'POST':
        form = EmisorForm(request.POST, instance=emisor)
        if form.is_valid():
            form.save()
            messages.success(request, "Datos de la empresa emisora actualizados.")
            return redirect('emisor_configuracion')
    else:
        form = EmisorForm(instance=emisor)

    return render(request, 'facturador/emisor_form.html', {'form': form, 'emisor': emisor})


# ==========================================
# 7. ENDPOINTS JSON / API PARA EL FRONTEND
# ==========================================
@login_required
def api_productos(request):
    """Retorna lista de productos activos con su stock en tiempo real."""
    productos = Producto.objects.filter(activo=True).values(
        'id', 'codigo', 'nombre', 'precio_unitario', 'tarifa_iva', 'stock'
    )
    return JsonResponse({'productos': list(productos)})
