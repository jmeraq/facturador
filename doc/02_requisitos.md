# 📋 Especificación de Requisitos: Facturador Simple Ecuador

Este documento formaliza los **Requisitos Funcionales (RF)** y **No Funcionales (RNF)** del sistema de facturación e inventario. Constituye el contrato técnico de la solución y sirve como la especificación exacta para el equipo de desarrollo y los modelos de Inteligencia Artificial que colaboren en el proyecto.

---

## 🔍 Introducción: Fundamentos de Ingeniería de Requisitos

- **Requisitos Funcionales (RF)**: Definen *qué* debe hacer el sistema (las acciones, procesos, cálculos y comportamientos específicos ante entradas del usuario).
- **Requisitos No Funcionales (RNF)**: Definen *cómo* debe operar el sistema (atributos de calidad, restricciones técnicas, rendimiento, seguridad, concurrencia y normativas legales).

---

## ⚙️ 1. Requisitos Funcionales (RF)

### Módulo 1: Autenticación y Control de Acceso (RBAC)
* **RF-01: Inicio y Cierre de Sesión Seguro**
  * El sistema debe permitir el ingreso de usuarios registrados mediante nombre de usuario y contraseña cifrada.
  * Debe mantener una sesión segura y permitir el cierre explícito de la misma en cualquier momento.
* **RF-02: Control de Acceso Basado en Roles (RBAC)**
  * El sistema debe asignar a cada usuario exactamente un rol de los siguientes:
    1. `ADMINISTRADOR`: Acceso irrestricto a todos los módulos y opciones de configuración.
    2. `ASESOR`: Autorizado exclusivamente para consultar catálogo, gestionar clientes, emitir, anular e imprimir facturas.
    3. `BODEGUERO`: Autorizado exclusivamente para crear y editar productos, consultar inventarios y registrar movimientos manuales (entradas/ajustes).
* **RF-03: Restricción de Rutas y Menús**
  * La interfaz gráfica debe ocultar los botones e hipervínculos a los que el rol del usuario no tenga permiso.
  * Las vistas en el backend deben rechazar con código HTTP 403 (o redirección controlada) cualquier intento de acceso forzado por URL a módulos no autorizados.

### Módulo 2: Catálogo de Productos
* **RF-04: Gestión de Productos (CRUD)**
  * El sistema debe permitir registrar, listar, editar y deshabilitar productos con los siguientes datos mínimos: código/SKU (único), nombre, descripción, precio unitario sin IVA, tarifa de IVA aplicable y stock mínimo de seguridad.
* **RF-05: Tarifas de IVA por Producto**
  * Cada producto debe poder configurarse con tarifa de IVA `15.00%` (tarifa estándar vigente en Ecuador) o `0.00%` (bienes no gravados o exentos).
* **RF-06: Alertas de Stock Bajo**
  * El sistema debe identificar visualmente mediante insignias (*badges*) en color rojo y advertencias en el dashboard aquellos productos cuyo stock actual sea menor o igual al stock mínimo configurado.

### Módulo 3: Control de Inventario y Kardex
* **RF-07: Consulta de Existencias en Tiempo Real**
  * El sistema debe proveer una pantalla de inventario donde se visualice el stock actualizado de cada producto, el valor monetario valorizado del stock y su estado.
* **RF-08: Ajustes e Ingresos Manuales de Stock**
  * El usuario con rol Bodeguero o Administrador debe poder ingresar nuevas unidades de mercadería o realizar correcciones de inventario, debiendo especificar obligatoriamente un motivo o justificación.
* **RF-09: Trazabilidad y Kardex Histórico**
  * El sistema debe registrar un historial de movimientos inmutable (`MovimientoInventario`) por cada variación de existencias, catalogado según su tipo: `INGRESO`, `EGRESO_VENTA`, `AJUSTE` o `DEVOLUCION_ANULACION`.

### Módulo 4: Gestión de Clientes y Validación Tributaria (SRI)
* **RF-10: Mantenimiento de Clientes**
  * El sistema debe registrar clientes con tipo de documento, número de identificación, nombres/razón social, correo electrónico, teléfono y dirección.
* **RF-11: Validación Algorítmica de Identificaciones del Ecuador**
  * El sistema debe validar matemáticamente la cédula o RUC antes de permitir el guardado:
    * **Cédula (10 dígitos)**: Algoritmo de Módulo 10 con coeficientes 2-1-2-1-2-1-2-1-2 y código de provincia (01 a 24 o 30).
    * **RUC Persona Natural (13 dígitos)**: Los primeros 10 dígitos deben formar una cédula válida y los últimos tres deben ser `>= 001`.
    * **RUC Sociedad Privada (13 dígitos)**: Tercer dígito igual a 9, algoritmo de Módulo 11 con coeficientes 4-3-2-7-6-5-4-3-2 y sufijo `>= 001`.
    * **RUC Entidad Pública (13 dígitos)**: Tercer dígito igual a 6, algoritmo de Módulo 11 con coeficientes 3-2-7-6-5-4-3-2 y sufijo `>= 0001`.
    * **Consumidor Final**: Identificación obligatoria `9999999999999`.

### Módulo 5: Facturación y Descuento Automático
* **RF-12: Pantalla Dinámica de Emisión**
  * La pantalla de emisión debe permitir seleccionar el cliente, la fecha de emisión, la forma de pago SRI y agregar múltiples renglones de productos.
  * Debe calcular en tiempo real (vía JavaScript en el navegador) los subtotales al 15%, subtotales al 0%, descuentos, IVA y total final.
* **RF-13: Verificación Estricta de Disponibilidad de Stock**
  * Antes de procesar la venta, el sistema debe comprobar que para cada ítem solicitado exista existencias suficientes (`stock >= cantidad_solicitada`). De lo contrario, la transacción debe ser rechazada con un mensaje de error descriptivo.
* **RF-14: Descuento Automático de Inventario**
  * Al emitirse la factura de manera exitosa, el sistema debe decrementar automáticamente el stock del producto en la base de datos y registrar el movimiento de salida en el Kardex.
* **RF-15: Numeración Oficial Secuencial SRI**
  * La factura debe generarse con el formato oficial del SRI: `EEE-PPP-NNNNNNNNN` (Ejemplo: `001-001-000000001`), donde `EEE` es el establecimiento (3 dígitos), `PPP` es el punto de emisión (3 dígitos) y `NNNNNNNNN` es el número secuencial correlativo de 9 dígitos rellenado con ceros a la izquierda.
* **RF-16: Formas de Pago Homologadas SRI**
  * Se deben soportar los códigos del SRI:
    * `01`: Efectivo (Sin utilización del sistema financiero).
    * `16`: Tarjeta de Débito.
    * `19`: Tarjeta de Crédito.
    * `20`: Otros con utilización del sistema financiero (Transferencias / Depósitos).

### Módulo 6: Anulación de Facturas y Reposición de Stock
* **RF-17: Anulación de Comprobante con Reposición Transaccional**
  * El sistema debe permitir a un Asesor o Administrador anular una factura emitida.
  * Al anularla, el estado debe cambiar a `ANULADA` y de forma automática e inmediata se debe devolver la cantidad facturada al inventario de cada producto, registrando el movimiento de `DEVOLUCION_ANULACION` en el Kardex.

### Módulo 7: Impresión de Facturas y Formato RIDE
* **RF-18: Impresión Física RIDE (Estándar SRI)**
  * El sistema debe generar una vista detallada optimizada para impresión en papel estándar A4 mediante estilos `@media print`.
  * La impresión debe ocultar botones, barras de navegación y menús, mostrando un membrete limpio con los datos del emisor, cliente, desglose de ítems, forma de pago y el desglose tributario (Subtotal 15%, Subtotal 0%, IVA 15%, Total).

### Módulo 8: Configuración del Emisor
* **RF-19: Parametrización de Datos Fiscales**
  * El Administrador debe poder configurar la Razón Social, Nombre Comercial, RUC del emisor, Dirección Matriz, Código de Establecimiento, Punto de Emisión y la tarifa de IVA por defecto.

---

## 🛡️ 2. Requisitos No Funcionales (RNF)

| Identificador | Categoría | Requisito / Especificación Técnica | Criterio de Aceptación |
| :--- | :--- | :--- | :--- |
| **RNF-01** | **Rendimiento** | La emisión de una factura y el recálculo dinámico en el navegador deben procesarse en menos de 500 ms en condiciones normales de uso. | El usuario no experimenta bloqueos en el navegador; el cálculo en JavaScript es instantáneo al modificar cantidades o productos. |
| **RNF-02** | **Integridad Transaccional (ACID)** | Toda operación de emisión o anulación debe ejecutarse dentro de un bloque atómico (`transaction.atomic`) y con bloqueo de fila (`select_for_update`). | Nunca se generará una factura si falla el descuento de stock. Es imposible que dos ventas simultáneas dejen el stock en negativo (*anti race condition*). |
| **RNF-03** | **Seguridad** | Las contraseñas se almacenan mediante algoritmos de hash seguros (PBKDF2 con SHA-256). Todas las peticiones POST deben estar protegidas contra CSRF (*Cross-Site Request Forgery*). | No se almacenan contraseñas en texto plano. Cada formulario HTML incluye el token `{% csrf_token %}`. |
| **RNF-04** | **Usabilidad y Adaptabilidad** | La interfaz gráfica debe estar basada en Bootstrap 5 con un diseño responsivo y tipografía moderna, legible tanto en computadoras de escritorio como en terminales de punto de venta y tablets. | Interfaz adaptable a resoluciones mínimas de 768px; diseño limpio y estructurado con tarjetas e iconos visuales. |
| **RNF-05** | **Arquitectura y Limpieza de Código** | Debe implementarse el patrón arquitectural MVC/MVT, separando la lógica de negocio en una capa de servicios (`FacturacionService`) y manteniendo el código fuente organizado dentro de `src/`. | Las vistas son delgadas (*thin views*), delegando la orquestación transaccional al servicio correspondiente. |
| **RNF-06** | **Portabilidad y Despliegue Sencillo** | El proyecto debe ser compatible con Python 3.12+ y gestionarse con la herramienta ultrarrápida `uv`. La base de datos por defecto es SQLite para facilitar el entorno pedagógico y local, con soporte para migrar a PostgreSQL. | Un nuevo alumno puede clonar el repositorio, ejecutar `uv run python manage.py migrate` y tener la aplicación corriendo en menos de 2 minutos. |
| **RNF-07** | **Cumplimiento Legal (SRI Ecuador)** | El sistema debe cumplir con la tarifa del 15% de IVA (Ley Orgánica de Eficiencia Económica y Generación de Empleo) y los formatos de codificación numérica de comprobantes oficiales del Ecuador. | Las fórmulas de cálculo matemático de IVA y los dígitos verificadores cumplen la normativa oficial del SRI. |
| **RNF-08** | **Manejo Robusto de Errores** | El sistema debe interceptar excepciones de negocio (ej. falta de stock, cliente duplicado, cédula errónea) y presentarlas al usuario mediante mensajes informativos amigables (`messages.error`). | El sistema nunca debe arrojar pantallas amarillas de error 500 al usuario final ante fallos de validación. |

---

## 📊 3. Matriz de Trazabilidad: Requisitos vs. Roles del Sistema

| Módulo / Requisito | Administrador | Asesor Comercial | Bodeguero |
| :--- | :---: | :---: | :---: |
| **RF-01 / RF-02 / RF-03**: Autenticación y RBAC | ✅ | ✅ | ✅ |
| **RF-04 / RF-05 / RF-06**: Gestión de Catálogo de Productos | ✅ | 👁️ (Solo lectura) | ✅ |
| **RF-07 / RF-08 / RF-09**: Inventario y Ajustes Manuales (Kardex) | ✅ | ❌ | ✅ |
| **RF-10 / RF-11**: Gestión de Clientes y Validación SRI | ✅ | ✅ | ❌ |
| **RF-12 / RF-13 / RF-14 / RF-15**: Emisión de Facturas y Stock | ✅ | ✅ | ❌ |
| **RF-16 / RF-17**: Anulación de Facturas y Reposición | ✅ | ✅ | ❌ |
| **RF-18**: Consulta e Impresión RIDE | ✅ | ✅ | ❌ |
| **RF-19**: Configuración Fiscal del Emisor | ✅ | ❌ | ❌ |

---

## 👨‍🏫 Nota Pedagógica para los Estudiantes

### ¿Por qué esta lista de requisitos es oro puro para la Inteligencia Artificial?
Si le dices a una IA: *"Hazme un sistema de facturación"*, la IA asumirá inventarios sin Kardex, calculará el IVA de su país de entrenamiento (usualmente 16% o 21%), permitirá vender con stock negativo y usará identificaciones genéricas.

En cambio, si le entregas este documento de requisitos:
1. La IA sabe con precisión matemática qué excepciones capturar (`ValidationError` si `stock < cantidad`).
2. Sabe qué roles programar y qué vistas proteger (`@role_required`).
3. Sabe exactamente cómo calcular y redondear los valores monetarios con `Decimal` y `ROUND_HALF_UP`.
