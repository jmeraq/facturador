# 🚀 Plan de Implementación y Pruebas: Facturador Simple Ecuador

> **Guía Operativa y Hoja de Ruta de Ejecución (*Runbook / Execution Roadmap*)**  
> Este documento traduce las especificaciones conceptuales (objetivos, requisitos, casos de uso, arquitectura y base de datos) en una **secuencia estructurada de construcción y verificación**. Es la pieza final indispensable antes de instruir a un desarrollador o a un modelo de Inteligencia Artificial para que construya el sistema.

---

## ⚠️ 1. La Regla de Oro: ¿Por qué NO pedir todo el sistema en un solo mensaje?

Cuando un alumno comete el error de escribirle a una IA:  
> *"Lee la carpeta `doc/` y construye todo el sistema de una vez"*

El modelo de lenguaje sufrirá los siguientes problemas técnicos:
1. **Límite de Tokens de Salida**: Los LLMs tienen un límite estricto de generación por respuesta (generalmente entre 4,000 y 8,000 tokens). Un sistema completo de facturación requiere más de 3,500 líneas de código distribuidas en 25 archivos. Al acabarse los tokens, la IA truncará código crítico (`# TODO: implementar lógica...`).
2. **Degradación del Razonamiento**: Cuantas más tareas simultáneas intenta resolver la IA en una sola pasada, más propensa es a olvidar detalles tributarios (como el cálculo del 15% de IVA o el algoritmo de Módulo 10).
3. **Imposibilidad de Depuración**: Si algo falla tras generar 20 archivos al mismo tiempo, el estudiante no sabrá si el error está en la migración de base de datos, en el validador, en el servicio o en la plantilla HTML.

> 💡 **Metodología Profesional**:  
> **El software se construye en Fases Atómicas e Incrementales.** Cada fase se genera, se inspecciona, se prueba y se consolida antes de pasar a la siguiente.

---

## 🌳 2. Árbol de Archivos Objetivo (Target File Tree)

Para que la IA no improvise la ubicación del código, debe apegarse estrictamente a la siguiente estructura del repositorio:

```
facturador/
├── doc/                                          # Documentación de ingeniería de software
│   ├── README.md                                 # Índice general y guía metodológica
│   ├── 01_objetivos.md                           # Objetivos SMART
│   ├── 02_requisitos.md                          # Requisitos Funcionales y No Funcionales
│   ├── 03_casos_de_uso.md                        # Casos de uso formales y diagramas
│   ├── 04_stack_tecnologico.md                   # Justificación técnica y pedagógica
│   ├── 05_arquitectura_y_modelo_datos.md         # Patrón MVC, Servicios y flujo ACID
│   ├── 06_diseno_base_de_datos.md                # DER, Diccionario de datos y DDL SQL
│   ├── 07_guia_contexto_para_ia.md               # Guía didáctica de contexto para IA
│   └── 08_plan_de_implementacion_y_pruebas.md    # Este documento (Hoja de ruta)
├── src/                                          # Código fuente (src/ layout)
│   ├── config/                                   # Paquete de configuración Django
│   │   ├── __init__.py
│   │   ├── asgi.py
│   │   ├── settings.py                           # Parámetros, apps instaladas, DB, auth
│   │   ├── urls.py                               # Enrutador principal del proyecto
│   │   └── wsgi.py
│   └── facturador/                               # Aplicación principal del negocio
│       ├── __init__.py
│       ├── apps.py
│       ├── models.py                             # 7 entidades relacionales
│       ├── validators.py                         # Algoritmos Módulo 10 y 11 (SRI Ecuador)
│       ├── services.py                           # FacturacionService (@transaction.atomic)
│       ├── views.py                              # Vistas delgadas con decoradores RBAC
│       ├── urls.py                               # Rutas de la app facturador
│       ├── tests.py                              # Suite de pruebas unitarias (10 tests)
│       ├── management/
│       │   └── commands/
│       │       └── poblar_datos.py               # Comando de seeding de datos iniciales
│       └── migrations/
│           ├── __init__.py
│           └── 0001_initial.py                   # Migración inicial de tablas
├── templates/                                    # Plantillas HTML con Bootstrap 5.3
│   ├── base.html                                 # Layout maestro (Navbar, mensajes, footer)
│   └── facturador/
│       ├── login.html                            # Pantalla de login con botones rápidos
│       ├── dashboard.html                        # Dashboard de métricas y alertas
│       ├── producto_lista.html                   # Catálogo de productos
│       ├── producto_form.html                    # Formulario de alta/edición de producto
│       ├── inventario_dashboard.html             # Existencias y tabla de Kardex
│       ├── cliente_lista.html                    # Directorio de clientes
│       ├── cliente_form.html                     # Formulario con validación de cédula/RUC
│       ├── factura_lista.html                    # Historial de comprobantes
│       ├── factura_crear.html                    # Pantalla interactiva con cálculo en vivo
│       ├── factura_detalle.html                  # Comprobante RIDE con CSS @media print
│       └── emisor_form.html                      # Configuración de datos fiscales SRI
├── static/css/
│   └── style.css                                 # Estilos personalizados y reglas de impresión
├── manage.py                                     # Entry point de Django
├── pyproject.toml                                # Dependencias gestionadas por uv
├── uv.lock                                       # Archivo de bloqueo determinista
└── db.sqlite3                                    # Base de datos relacional SQLite
```

---

## 🧱 3. Plan de Construcción Modular en 7 Fases

Cada fase contiene sus entregables específicos y el **prompt sugerido** que el alumno debe proporcionar al asistente de IA:

---

### 🔹 Fase 1: Entorno de Ejecución y Configuración Base
* **Objetivo**: Inicializar el entorno virtual con `uv`, configurar Django en el directorio `src/` y verificar que el servidor levante.
* **Archivos a crear**:
  - `pyproject.toml` (dependencia: `django>=6.1.2`).
  - `manage.py` apuntando a `src/config/settings.py`.
  - `src/config/settings.py` (configurando `BASE_DIR`, `INSTALLED_APPS`, `DATABASES` SQLite, `TEMPLATES`, `STATICFILES_DIRS`, `LOGIN_URL = 'login'`).
  - `src/config/urls.py`.
* **Prompt para la IA**:
  > *"Fase 1: Configura el entorno base del proyecto usando Python 3.12 y uv siguiendo el documento doc/04_stack_tecnologico.md. Implementa el src/ layout con la app config en src/config/ y la app facturador en src/facturador/. Configura settings.py para trabajar con SQLite, plantillas en templates/ y archivos estáticos en static/."*
* **Criterio de éxito**: Ejecutar `uv run python manage.py check` y obtener `System check identified no issues`.

---

### 🔹 Fase 2: Capa de Dominio y Validadores Tributarios (SRI)
* **Objetivo**: Implementar los validadores matemáticos de identidad ecuatoriana y los modelos relacionales según el diseño de base de datos.
* **Archivos a crear**:
  - `src/facturador/validators.py`: Algoritmo de Módulo 10 para cédulas, Módulo 10/11 para RUCs y Consumidor Final (`9999999999999`).
  - `src/facturador/models.py`: Modelos `Emisor`, `Cliente`, `Producto`, `Factura`, `DetalleFactura`, `MovimientoInventario`, `PerfilUsuario` (según `doc/06_diseno_base_de_datos.md`).
  - Generación y ejecución de migraciones (`0001_initial.py`).
* **Prompt para la IA**:
  > *"Fase 2: Implementa la capa de dominio. Crea src/facturador/validators.py con la validación de Cédula y RUC de Ecuador bajo Módulo 10 y 11. Luego crea src/facturador/models.py siguiendo al pie de la letra el diccionario de datos de doc/06_diseno_base_de_datos.md, asegurando el uso de DecimalField para montos y models.PROTECT en claves foráneas. Genera y aplica las migraciones."*
* **Criterio de éxito**: `uv run python manage.py makemigrations && uv run python manage.py migrate` se ejecuta sin errores y crea todas las tablas en `db.sqlite3`.

---

### 🔹 Fase 3: Capa de Servicios y Transacciones ACID (El Corazón del Sistema)
* **Objetivo**: Implementar el orquestador transaccional que emite facturas, descuenta stock y registra auditoría en el Kardex.
* **Archivos a crear**:
  - `src/facturador/services.py`: Clase `FacturacionService` con método `emitir_factura` protegido con `@transaction.atomic` y `select_for_update()`.
  - Método `anular()` en el modelo `Factura` para reponer el stock automáticamente y registrar en el Kardex.
* **Prompt para la IA**:
  > *"Fase 3: Implementa la lógica transaccional en src/facturador/services.py siguiendo la especificación del Caso de Uso CU-05 (doc/03_casos_de_uso.md) y los diagramas de secuencia de doc/05_arquitectura_y_modelo_datos.md. Asegura el control de concurrencia con select_for_update, validación estricta de stock disponible, cálculo de IVA al 15% con Decimal y registro inmutable en MovimientoInventario."*
* **Criterio de éxito**: Probar desde la consola interactiva (`uv run python manage.py shell`) que una venta descuenta stock y que una venta con stock insuficiente arroja `ValidationError`.

---

### 🔹 Fase 4: Autenticación, Roles (RBAC) y Layout Base
* **Objetivo**: Proveer el sistema de login/logout, proteger rutas por roles y diseñar el layout visual maestro.
* **Archivos a crear**:
  - `src/facturador/views.py`: Vistas de autenticación (`login_view`, `logout_view`, `dashboard`) y decorador `@role_required`.
  - `templates/base.html`: Barra de navegación responsive con menú filtrado por rol, alertas `messages` y CDN de Bootstrap 5.3 y Bootstrap Icons.
  - `templates/facturador/login.html`: Pantalla de inicio de sesión con botones de acceso rápido para pruebas.
  - `static/css/style.css`: Estilos visuales complementarios.
* **Prompt para la IA**:
  > *"Fase 4: Configura la autenticación y el control de roles RBAC según doc/02_requisitos.md (RF-01 a RF-03). Crea un decorador @role_required para vistas de Administrador, Asesor y Bodeguero. Implementa templates/base.html con Bootstrap 5.3 y templates/facturador/login.html con botones rápidos para alternar entre roles."*
* **Criterio de éxito**: Iniciar sesión en el navegador y verificar que el Asesor solo ve Facturación y Clientes, mientras que el Bodeguero solo ve Inventario y Productos.

---

### 🔹 Fase 5: Módulos de Catálogo, Inventario y Clientes
* **Objetivo**: Desarrollar la gestión de productos con stock mínimo, registro manual de entradas en Kardex y directorio de clientes.
* **Archivos a crear**:
  - Vistas y plantillas de Productos: `producto_lista.html`, `producto_form.html`.
  - Vistas y plantillas de Inventario: `inventario_dashboard.html` (monitoreo de stock bajo y tabla histórica de movimientos).
  - Vistas y plantillas de Clientes: `cliente_lista.html`, `cliente_form.html` (captura de errores del validador de cédula).
* **Prompt para la IA**:
  > *"Fase 5: Desarrolla los módulos de soporte: Catálogo de Productos con alerta de stock mínimo (CU-02, CU-09), Gestión de Inventario con historial de Kardex y registro de ajustes manuales (CU-03), y Directorio de Clientes con captura visual de errores de validación de Cédula/RUC (CU-04)."*
* **Criterio de éxito**: Intentar registrar un cliente con cédula inválida `1710034060` y verificar que el formulario impida el guardado mostrando la alerta adecuada.

---

### 🔹 Fase 6: Módulo de Facturación Dinámica y RIDE
* **Objetivo**: Construir la pantalla interactiva de venta con cálculo dinámico en el navegador e impresión RIDE adaptada a hoja A4.
* **Archivos a crear**:
  - `templates/facturador/factura_crear.html`: Tabla dinámica con JavaScript Vanilla que recalcula Subtotal 15%, Subtotal 0%, IVA y Total en tiempo real.
  - `templates/facturador/factura_lista.html`: Historial de comprobantes emitidos y anulados.
  - `templates/facturador/factura_detalle.html`: Comprobante RIDE con reglas CSS `@media print` para impresión física limpia.
* **Prompt para la IA**:
  > *"Fase 6: Construye el módulo de facturación. En factura_crear.html, implementa una tabla dinámica con JavaScript Vanilla que permita añadir renglones de productos y recalcule en tiempo real subtotales, IVA 15% y Total. Conecta la emisión con FacturacionService. Luego crea factura_detalle.html con diseño RIDE y reglas CSS @media print para impresión en formato A4 (CU-05, CU-07, RF-18)."*
* **Criterio de éxito**: Emitir una factura con 2 productos, verificar que el inventario se descuenta en la base de datos, presionar "Imprimir" y comprobar que la vista de impresión oculte botones y menús.

---

### 🔹 Fase 7: Datos de Prueba y Suite de Pruebas Automatizadas
* **Objetivo**: Automatizar la carga de datos de prueba y escribir pruebas unitarias de regresión.
* **Archivos a crear**:
  - `src/facturador/management/commands/poblar_datos.py`: Seeding de usuarios (`admin`, `asesor`, `bodeguero`), catálogo inicial y clientes.
  - `src/facturador/tests.py`: 10 pruebas unitarias cubriendo emisión, control de stock, anulación, módulo 10/11 y RBAC.
* **Prompt para la IA**:
  > *"Fase 7: Automatiza el aseguramiento de calidad. Crea un comando management poblar_datos para crear usuarios y productos de prueba. Luego implementa en src/facturador/tests.py una suite de pruebas unitarias que valide: 1) emisión con descuento de stock, 2) rechazo por stock insuficiente, 3) anulación con reposición, 4) validador de cédula ecuatoriana y 5) permisos RBAC."*
* **Criterio de éxito**: Ejecutar `uv run python manage.py test` y obtener `Ran 10 tests in 0.8s ... OK`.

---

## 🧪 4. Matriz de Datos de Prueba para Validación (QA Checklist)

Para que los alumnos y la IA verifiquen el sistema con datos reales de Ecuador:

### Datos de Identificación Ecuatoriana para Pruebas:
| Tipo | Número de Identificación | Resultado Esperado | Justificación Técnica |
| :--- | :--- | :---: | :--- |
| **Cédula Válida** | `1710034065` | ✅ ACEPTAR | Provincia 17 (Pichincha), dígito verificador 5 válido por Módulo 10. |
| **Cédula Válida** | `0910000000` *(o real de Guayas)* | ✅ ACEPTAR | Cumple algoritmo Módulo 10. |
| **Cédula Inválida** | `1710034060` | ❌ RECHAZAR | Dígito verificador erróneo (debería ser 5, no 0). |
| **Cédula Inválida** | `2500000001` | ❌ RECHAZAR | Código de provincia 25 inexistente (Ecuador tiene del 01 al 24 y 30). |
| **RUC Natural Válido** | `1710034065001` | ✅ ACEPTAR | Cédula válida + establecimiento `001`. |
| **RUC Sociedad Privada** | `1790011674001` | ✅ ACEPTAR | Tercer dígito 9, válido por Módulo 11. |
| **Consumidor Final** | `9999999999999` | ✅ ACEPTAR | Identificación estándar permitida por el SRI para ventas menores. |

### Casos de Prueba de Facturación e Inventario:
| ID Prueba | Escenario de Prueba | Acción Realizada | Resultado Esperado |
| :---: | :--- | :--- | :--- |
| **TC-01** | Venta normal con stock suficiente | Vender 2 unidades de producto con stock = 10. | Factura en estado `EMITIDA`. Stock queda en 8. Se crea Kardex `EGRESO_VENTA`. |
| **TC-02** | Venta con sobregiro de inventario | Vender 15 unidades de producto con stock = 10. | Se interrumpe la transacción con `ValidationError`. Stock permanece en 10. Factura NO se crea. |
| **TC-03** | Anulación de comprobante | Anular factura emitida con 2 unidades. | Factura pasa a estado `ANULADA`. Stock regresa a 10. Se crea Kardex `DEVOLUCION_ANULACION`. |
| **TC-04** | Cálculo de IVA 15% | Vender producto de $100.00 gravado con IVA 15%. | Subtotal 15%: $100.00, IVA 15%: $15.00, Total: $115.00. |
| **TC-05** | Cálculo de IVA 0% | Vender medicina/alimento de $50.00 gravado con IVA 0%. | Subtotal 0%: $50.00, IVA 15%: $0.00, Total: $50.00. |
| **TC-06** | Factura Mixta (15% y 0%) | Renglón A ($100 al 15%) + Renglón B ($50 al 0%). | Subtotal sin impuestos: $150.00, IVA: $15.00, Total: $165.00. |
| **TC-07** | Control de Concurrencia | Dos ventas simultáneas de la última unidad (stock = 1). | El bloqueo `select_for_update` atiende la primera y rechaza la segunda sin dejar stock negativo. |
| **TC-08** | Seguridad RBAC | Usuario `bodeguero` intenta acceder a `/facturas/nueva/`. | El decorador intercepta el acceso y retorna HTTP 403 / Redirección. |

---

## 🤖 5. El Meta-Prompt Maestro para Iniciar el Proyecto con una IA

Este es el prompt que el profesor o alumno debe copiar y pegar para arrancar el proyecto de manera controlada con cualquier asistente de IA:

```text
Hola. Vamos a desarrollar el proyecto "Facturador Simple Ecuador" en Python/Django siguiendo
estrictamente las especificaciones de ingeniería de software almacenadas en la carpeta doc/.

Por favor realiza lo siguiente:
1. Lee los documentos en orden de prioridad:
   - doc/01_objetivos.md
   - doc/02_requisitos.md
   - doc/03_casos_de_uso.md
   - doc/04_stack_tecnologico.md
   - doc/05_arquitectura_y_modelo_datos.md
   - doc/06_diseno_base_de_datos.md
   - doc/08_plan_de_implementacion_y_pruebas.md

2. NO intentes construir todo el sistema en un solo paso. Nos apegaremos al plan modular
   por fases de doc/08_plan_de_implementacion_y_pruebas.md y al árbol de directorios exacto.

3. Para comenzar, limítate EXCLUSIVAMENTE a ejecutar la FASE 1 (Entorno de Ejecución y
   Configuración Base con layout src/). Una vez que verifiquemos que la Fase 1 funciona,
   te pediré la Fase 2.

¿Entendido? Confírmame el plan y presenta los entregables de la Fase 1.
```
