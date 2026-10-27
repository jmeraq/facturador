# 🏛️ Arquitectura y Modelo de Datos: Facturador Simple Ecuador

Este documento describe la arquitectura de software, el diseño de la base de datos y los flujos de integración del sistema **Facturador Simple Ecuador**. Provee la visión estructural interna necesaria para desarrolladores e inteligencias artificiales antes de modificar o extender el código.

---

## 🏗️ 1. Arquitectura de Software: Patrón MVC / MVT en Django

El proyecto implementa el patrón **Modelo-Vista-Controlador (MVC)**, adaptado por Django bajo la terminología **Modelo-Vista-Template (MVT)** con una capa adicional de **Servicios de Negocio** para desacoplar responsabilidades:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       CAPA DE PRESENTACIÓN (V / T)                          │
│                                                                             │
│   ┌───────────────────────────────┐     ┌───────────────────────────────┐   │
│   │    Plantillas HTML (Bootstrap)│     │   Lógica Frontend (JS Vanilla)│   │
│   │    - base.html, factura_crear │     │   - Cálculo dinámico de IVA   │   │
│   │    - RIDE para impresión A4   │     │   - Actualización de totales  │   │
│   └───────────────▲───────────────┘     └───────────────▲───────────────┘   │
└───────────────────┼─────────────────────────────────────┼───────────────────┘
                    │ Petición HTTP / Respuesta           │ Eventos DOM
┌───────────────────▼─────────────────────────────────────▼───────────────────┐
│                        CAPA DE CONTROLADOR (Vistas)                         │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │ views.py (Thin Controllers)                                         │   │
│   │ - Manejo de sesión y autenticación (@login_required)                │   │
│   │ - Control de acceso por rol (@role_required)                        │   │
│   │ - Validación de entrada HTTP (POST / GET)                           │   │
│   └──────────────────────────────────▲──────────────────────────────────┘   │
└──────────────────────────────────────┼──────────────────────────────────────┘
                                       │ Orquesta la operación
┌──────────────────────────────────────▼──────────────────────────────────────┐
│                    CAPA DE SERVICIOS (Lógica de Negocio)                    │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │ FacturacionService (services.py)                                    │   │
│   │ - Orquestación de transacción ACID (@transaction.atomic)           │   │
│   │ - Bloqueo de fila para concurrencia (.select_for_update())          │   │
│   │ - Reglas tributarias y redondeo a 2 decimales (ROUND_HALF_UP)       │   │
│   └──────────────────────────────────▲──────────────────────────────────┘   │
└──────────────────────────────────────┼──────────────────────────────────────┘
                                       │ Persistencia / ORM
┌──────────────────────────────────────▼──────────────────────────────────────┐
│                        CAPA DE DOMINIO (Modelos M)                          │
│                                                                             │
│   ┌───────────────┐  ┌───────────────┐  ┌───────────────┐  ┌────────────┐   │
│   │    Emisor     │  │    Cliente    │  │   Producto    │  │  Factura   │   │
│   │ (Config SRI)  │  │(Validación ID)│  │ (Stock e IVA) │  │  (Cabecera)│   │
│   └───────────────┘  └───────────────┘  └───────────────┘  └──────┬─────┘   │
│                                                                   │         │
│   ┌───────────────────────────────┐     ┌─────────────────────────▼─────┐   │
│   │     MovimientoInventario      │     │        DetalleFactura         │   │
│   │       (Kardex Histórico)      │     │      (Renglones de Venta)     │   │
│   └───────────────────────────────┘     └───────────────────────────────┘   │
└──────────────────────────────────────▲──────────────────────────────────────┘
                                       │ SQL Nativo
┌──────────────────────────────────────▼──────────────────────────────────────┐
│                         MOTOR DE BASE DE DATOS                              │
│                                                                             │
│   SQLite 3 (db.sqlite3)  -- [Preparado para migrar a PostgreSQL en Producción]│
└─────────────────────────────────────────────────────────────────────────────┘
```

### Principio de Diseño: *Fat Models / Services, Thin Views*
* **Vistas delgadas (`views.py`)**: Se limitan a recibir la petición, verificar permisos del rol, invocar al servicio y retornar una respuesta HTML o JSON.
* **Capa de Servicios (`services.py`)**: Contiene la lógica compleja de negocio, asegurando que si mañana se agrega una API REST o una interfaz móvil, la lógica de emisión y descuento de inventario se reutilice sin duplicar código.

---

## 🗄️ 2. Diagrama Entidad - Relación (Mermaid)

El siguiente diagrama modela las entidades del sistema y sus relaciones cardinales:

```mermaid
erDiagram
    User ||--|| PerfilUsuario : "posee un rol"
    Emisor ||--o{ Factura : "emite"
    Cliente ||--o{ Factura : "es facturado"
    Factura ||--|{ DetalleFactura : "contiene renglones"
    Producto ||--o{ DetalleFactura : "es incluido en"
    Producto ||--o{ MovimientoInventario : "registra historial"
    Factura ||--o{ MovimientoInventario : "origina movimiento"

    PerfilUsuario {
        int id PK
        int user_id FK
        string rol "ADMINISTRADOR | ASESOR | BODEGUERO"
    }

    Emisor {
        int id PK
        string ruc "13 digitos"
        string razon_social
        string establecimiento "001"
        string punto_emision "001"
        int secuencial_actual
        decimal tarifa_iva_defecto "15.00"
    }

    Cliente {
        int id PK
        string tipo_identificacion "04, 05, 06, 07"
        string identificacion "Cédula o RUC único"
        string nombres
        string email
        string telefono
        string direccion
    }

    Producto {
        int id PK
        string codigo "SKU único"
        string nombre
        decimal precio_unitario
        decimal tarifa_iva "15.00 o 0.00"
        decimal stock "Existencias actuales"
        decimal stock_minimo "Umbral de alerta"
        boolean activo
    }

    Factura {
        int id PK
        string numero_factura "001-001-000000001"
        int secuencial
        int cliente_id FK
        datetime fecha_emision
        string forma_pago "01, 16, 19, 20"
        string estado "EMITIDA | ANULADA"
        decimal subtotal_15
        decimal subtotal_0
        decimal subtotal_sin_impuestos
        decimal descuento_total
        decimal iva_15
        decimal total
        text observaciones
    }

    DetalleFactura {
        int id PK
        int factura_id FK
        int producto_id FK
        string codigo_producto
        string nombre_producto
        decimal cantidad
        decimal precio_unitario
        decimal tarifa_iva
        decimal descuento
        decimal subtotal
        decimal valor_iva
        decimal total
    }

    MovimientoInventario {
        int id PK
        int producto_id FK
        int factura_id FK "Opcional"
        string tipo "INGRESO | EGRESO_VENTA | AJUSTE | DEVOLUCION_ANULACION"
        decimal cantidad
        decimal stock_anterior
        decimal stock_nuevo
        string motivo
        datetime fecha
    }
```

---

## ⚡ 3. Diagrama de Secuencia: Flujo Transaccional de Facturación (ACID)

La emisión de una factura involucra múltiples operaciones dependientes que deben ejecutarse como una **unidad atómica**. Si cualquiera de ellas falla, el sistema debe revertir todos los cambios (*Rollback*):

```mermaid
sequenceDiagram
    autonumber
    actor Vendedor as Asesor Comercial
    participant Navegador as Navegador (JS)
    participant Vista as views.factura_crear
    participant Servicio as FacturacionService
    participant BD as Base de Datos (SQLite)

    Vendedor->>Navegador: Selecciona Cliente y añade Ítems
    Navegador->>Navegador: Calcula Subtotales, IVA 15% y Total en vivo
    Vendedor->>Navegador: Clic en "Emitir Factura"
    Navegador->>Vista: POST /facturas/nueva/ (datos JSON/Form)
    
    activate Vista
    Vista->>Servicio: emitir_factura(cliente, items, forma_pago)
    activate Servicio
    
    Servicio->>BD: BEGIN TRANSACTION (transaction.atomic)
    Servicio->>BD: Obtener Emisor y generar Secuencial (001-001-...)
    Servicio->>BD: INSERT INTO Factura (estado='EMITIDA')
    
    loop Para cada producto solicitado
        Servicio->>BD: SELECT * FROM Producto WHERE id=X FOR UPDATE
        Note over Servicio,BD: Bloqueo de fila para control de concurrencia
        
        alt Stock insuficiente (stock < cantidad)
            Servicio-->>Vista: Lanza ValidationError("Stock insuficiente")
            Servicio->>BD: ROLLBACK TRANSACTION
            Vista-->>Navegador: Mensaje de error (No se cobró ni se descontó nada)
        else Stock suficiente
            Servicio->>BD: UPDATE Producto SET stock = stock - cantidad
            Servicio->>BD: INSERT INTO DetalleFactura (...)
            Servicio->>BD: INSERT INTO MovimientoInventario (tipo='EGRESO_VENTA')
        end
    end
    
    Servicio->>BD: UPDATE Emisor SET secuencial_actual = secuencial_actual + 1
    Servicio->>BD: COMMIT TRANSACTION
    Servicio-->>Vista: Retorna objeto Factura creada
    deactivate Servicio
    
    Vista-->>Navegador: Redirección a /facturas/<id>/ (Vista RIDE)
    deactivate Vista
    Navegador-->>Vendedor: Muestra Factura lista para imprimir
```

---

## 🔒 4. Integridad y Control de Concurrencia

1. **Bloqueo a Nivel de Fila (`select_for_update`)**:
   En entornos con múltiples asesores vendiendo al mismo tiempo, existe el riesgo de que dos personas vendan la última unidad existente simultáneamente (*condición de carrera*). El uso de `select_for_update` garantiza que el primer proceso que consulte el producto bloquee el registro hasta finalizar la transacción, obligando al segundo proceso a esperar y evaluar el stock actualizado.
2. **Uso de Tipo de Dato `Decimal`**:
   Para aplicaciones financieras y tributarias, los tipos de dato de punto flotante (`float`) son inadmisibles debido a los errores de redondeo binario. Toda la aplicación utiliza `Decimal` con redondeo estándar financiero `ROUND_HALF_UP`.
3. **Restricción de Borrado (`on_delete=models.PROTECT`)**:
   Ni los clientes ni los productos que ya cuenten con historial de facturación pueden ser eliminados físicamente de la base de datos, garantizando la preservación histórica y la validez de los reportes contables.
