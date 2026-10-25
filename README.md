# Facturador Simple para Ecuador (Django + SQLite + Bootstrap 5)

Sistema web de facturación electrónica y gestión de inventario adaptado a la normativa tributaria del **SRI (Ecuador)**.

## Características Principales

1. **Catálogo de Productos**:
   - Código/SKU, nombre, descripción, precio unitario sin IVA.
   - Tarifa de IVA ecuatoriana: **15% (vigente)** y **0% (bienes básicos/medicinas)**.
   - Alertas visuales de stock mínimo y agotado.
2. **Control de Inventario y Kardex Automatizado**:
   - **Reducción automática de stock** al emitir cada factura mediante transacciones atómicas (`ACID`).
   - Bloqueo a nivel de fila (`select_for_update`) para evitar condiciones de carrera o sobreventas.
   - Validación estricta: No permite facturar cantidades superiores al stock disponible.
   - Historial de movimientos (Kardex): registro de ventas, compras/entradas, ajustes físicos y devoluciones.
   - **Reposición automática de stock** al anular facturas.
3. **Facturación Adaptada a Ecuador (SRI)**:
   - Formato secuencial oficial: `Establecimiento-PuntoEmision-Secuencial` (ej. `001-001-000000001`).
   - Validación de documentos de identidad con algoritmo de módulo 10/11:
     - **Cédula de Identidad** (10 dígitos).
     - **RUC** Personas Naturales, Privadas y Públicas (13 dígitos).
     - **Consumidor Final** (`9999999999999`).
     - Pasaporte.
   - Desglose tributario: Subtotal 15%, Subtotal 0%, Subtotal sin impuestos, Descuento, IVA 15% y Total.
   - Formas de pago del SRI (Efectivo, Tarjeta de Débito, Tarjeta de Crédito, Transferencia bancaria).
   - Vista de comprobante oficial en formato **RIDE** con clave de acceso simulada de 49 dígitos y estilos de impresión (`@media print` para A4).
4. **Control de Acceso Basado en Roles (RBAC)**:
   - **Administrador**: Acceso total al sistema (Ventas, Inventario, Clientes, Configuración de Emisor SRI).
   - **Asesor Comercial**: Especializado en ventas (Emisión de facturas, clientes, consulta de catálogo y precios).
   - **Bodeguero**: Especializado en inventario (Alta/edición de productos, Kardex, compras y ajustes de stock).
5. **Arquitectura MVC con Layout `src/`**:
   - **Modelos (M)**: [src/facturador/models.py](file:///Users/junior.mera@latam.com/Personal/facturador/src/facturador/models.py) (`Emisor`, `Cliente`, `Producto`, `Factura`, `DetalleFactura`, `MovimientoInventario`, `PerfilUsuario`).
   - **Controladores / Servicios (C)**: [src/facturador/views.py](file:///Users/junior.mera@latam.com/Personal/facturador/src/facturador/views.py) y [src/facturador/services.py](file:///Users/junior.mera@latam.com/Personal/facturador/src/facturador/services.py).
   - **Configuración**: [src/config/settings.py](file:///Users/junior.mera@latam.com/Personal/facturador/src/config/settings.py) y [src/config/urls.py](file:///Users/junior.mera@latam.com/Personal/facturador/src/config/urls.py).
   - **Vistas / Plantillas (V)**: `templates/` con **Bootstrap 5.3** y Bootstrap Icons.
6. **Base de Datos**:
   - SQLite (`db.sqlite3`).

---

## Usuarios y Credenciales de Prueba

El comando `uv run python manage.py poblar_datos` crea los siguientes usuarios listos para usar:

| Rol | Usuario | Contraseña | Permisos |
| :--- | :--- | :--- | :--- |
| **Administrador** | `admin` | `admin123` | **Acceso Total**: Facturación, Inventario, Productos, Clientes y Configuración SRI. |
| **Asesor** | `asesor` | `asesor123` | **Facturación & Ventas**: Emisión de facturas, gestión de clientes y consulta de catálogo. |
| **Bodeguero** | `bodeguero` | `bodeguero123` | **Gestión de Inventario**: Altas/edición de productos, entradas, ajustes físicos y Kardex. |

*Nota: La pantalla de inicio de sesión (`/login/`) incluye botones de autocompletado rápido para alternar entre roles con un solo clic.*

---

## Requisitos y Ejecución con `uv`

El proyecto utiliza [`uv`](https://github.com/astral-sh/uv), el gestor ultra-rápido de paquetes para Python.

### 1. Iniciar el Servidor de Desarrollo
```bash
uv run python manage.py runserver 0.0.0.0:8000
```
Abre tu navegador en: **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**

### 2. Cargar Datos de Prueba (Opcional)
Para cargar productos, clientes de prueba (incluyendo Consumidor Final) y stock inicial:
```bash
uv run python manage.py poblar_datos
```

### 3. Ejecutar la Suite de Pruebas Automatizadas
```bash
uv run python manage.py test
```

---

## Estructura de Rutas y Módulos

| Ruta | Descripción |
| :--- | :--- |
| `/` | **Dashboard**: Métricas de ventas, accesos directos, alertas de stock bajo y últimas facturas. |
| `/productos/` | **Tabla de Productos**: Catálogo con precios, tarifas de IVA y niveles de stock. |
| `/productos/nuevo/` | Alta de nuevos productos e inventario inicial. |
| `/inventario/` | **Inventario & Kardex**: Auditoría de movimientos (entradas, ventas y ajustes directos). |
| `/clientes/` | **Directorio de Clientes**: Gestión con validadores para Ecuador. |
| `/facturas/nueva/` | **Emitir Factura**: Formulario interactivo con cálculo dinámico y validación de stock. |
| `/facturas/` | **Historial de Facturas**: Listado de comprobantes emitidos y anulados. |
| `/facturas/<id>/` | **Comprobante RIDE**: Visualización e impresión formato A4/PDF según el SRI. |
| `/configuracion/` | **Configuración del Emisor**: RUC, razón social, establecimiento y puntos de emisión. |
