# 🛠️ Stack Tecnológico: Facturador Simple Ecuador

Este documento detalla todas las tecnologías, librerías, herramientas y patrones arquitecturales seleccionados para el desarrollo del proyecto **Facturador Simple Ecuador**, junto con la justificación técnica y pedagógica de cada elección.

---

## 🗺️ 1. Visión General del Stack

El sistema está construido siguiendo la filosofía de **"Baterías Incluidas"** y **"Monolito Modular Limpio"**, priorizando la simplicidad operativa, la integridad transaccional y el cumplimiento estricto de las leyes fiscales del Ecuador sin sobrecargar el proyecto con dependencias innecesarias (*anti-overengineering*).

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          1. FRONTEND / PRESENTACIÓN                         │
│   • HTML5 Semántico  • Bootstrap 5.3 (CSS Framework)  • Bootstrap Icons     │
│   • JavaScript Vanilla (ES6+) para cálculo dinámico en tiempo real          │
│   • CSS3 @media print para generación e impresión del formato RIDE (A4)     │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ Peticiones HTTP / Renderizado DTL
┌──────────────────────────────────────▼──────────────────────────────────────┐
│                         2. BACKEND / LÓGICA DE NEGOCIO                       │
│   • Lenguaje: Python 3.12+ (Tipado estático con Type Hints y Decimales)     │
│   • Framework Web: Django 6.1.2 (Patrón MVC / MVT)                          │
│   • Capa de Servicios: FacturacionService (Orquestador Transaccional)        │
│   • Control de Concurrencia: transaction.atomic() y select_for_update()     │
│   • Algoritmos SRI: Módulo 10 y Módulo 11 para Cédula y RUC de Ecuador      │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ Django ORM (Object-Relational Mapping)
┌──────────────────────────────────────▼──────────────────────────────────────┐
│                        3. PERSISTENCIA / BASE DE DATOS                      │
│   • Base de Datos: SQLite 3 (db.sqlite3)                                    │
│   • Compatibilidad de producción: Migrable de forma transparente a PostgreSQL│
│   • Integridad Referencial: Claves Foráneas con models.PROTECT en auditoría  │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ Entorno de Ejecución
┌──────────────────────────────────────▼──────────────────────────────────────┐
│                         4. TOOLING / DEVOPS / TESTING                       │
│   • Gestor de Entorno y Paquetes: uv (Astral) - Ultra rápido en Rust         │
│   • Control de Versiones: Git con estructura moderna src/ layout            │
│   • Suite de Pruebas: Django Test Runner (Pruebas unitarias automatizadas)   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🐍 2. Backend y Lógica de Negocio

### 2.1. Python (Versión 3.12+)
* **Rol**: Lenguaje de programación principal.
* **Justificación**:
  * **Tipado enriquecido**: Permite documentar contratos claros en funciones mediante type hints (`def emitir_factura(cliente: Cliente, items: list[dict]) -> Factura:`).
  * **Precisión Matemática**: Incorpora la librería nativa `decimal`, esencial para cálculos monetarios donde los números de punto flotante (`float`) generarían pérdidas de centavos por redondeo binario.
  * **Rendimiento mejorado**: CPython 3.12 introduce mejoras significativas en el recolector de basura y velocidad de ejecución del intérprete.

### 2.2. Django (Versión 6.1.2)
* **Rol**: Framework web full-stack.
* **Justificación**:
  * **Arquitectura Probada (MVT/MVC)**: Separa nítidamente el Modelo de Datos, la Lógica de Control y la Presentación.
  * **Seguridad Nativa**: Protección automática contra vulnerabilidades comunes del Top 10 de OWASP:
    * Inyección SQL (gracias al ORM parametrizado).
    * Falsificación de Petición en Sitios Cruzados (CSRF mediante tokens `{% csrf_token %}`).
    * Secuencias de Comandos en Sitios Cruzados (XSS mediante auto-escape en plantillas).
    * Almacenamiento de contraseñas mediante hash robusto **PBKDF2 con SHA-256**.
  * **ORM Potente y Migraciones Declarativas**: Facilita la evolución del esquema de la base de datos sin necesidad de escribir scripts SQL manuales propensos a error.

### 2.3. Capa de Servicios de Negocio (`FacturacionService`)
* **Rol**: Desacoplamiento de la lógica transaccional.
* **Justificación**:
  * Evita el antipatrón de las **"Vistas Gordas" (*Fat Views*)**, asegurando que las vistas HTTP solo orquesten peticiones y respuestas, mientras que el servicio centraliza las reglas de negocio (descuento de stock, validación tributaria y generación de comprobantes).
  * Permite reutilizar la lógica de facturación desde comandos CLI, tareas en segundo plano o futuras APIs REST sin duplicar una sola línea de código.

### 2.4. Control de Transacciones ACID y Concurrencia
* **`transaction.atomic()`**: Garantiza que si ocurre un fallo al descontar el inventario de un producto o al crear una línea de factura, la base de datos revierta automáticamente todos los cambios (*Rollback*), impidiendo facturas incompletas o stocks desfasados.
* **`select_for_update()`**: Aplica un bloqueo de fila a nivel de base de datos durante la consulta del producto, evitando condiciones de carrera (*race conditions*) cuando dos vendedores intentan facturar la última unidad existente de forma simultánea.

---

## 💾 3. Base de Datos y Persistencia

### 3.1. SQLite 3
* **Rol**: Motor de base de datos relacional predeterminado (`db.sqlite3`).
* **Justificación Técnica y Pedagógica**:
  * **Cero Configuración (*Zero-Config*)**: No requiere instalar ni configurar servidores pesados como PostgreSQL o MySQL para que los alumnos comiencen a trabajar inmediatamente.
  * **Autocontenida y Portable**: Toda la base de datos vive en un único archivo, lo que permite clonar el repositorio y levantar el sistema en cualquier máquina en segundos.
  * **Conformidad ACID Completa**: Soporta transacciones atómicas, claves foráneas e integridad referencial estricta.
  * **Fácil Transición a Producción**: Al estar gestionada mediante el ORM de Django, migrar a PostgreSQL o MariaDB en un entorno productivo requiere únicamente modificar 5 líneas de configuración en `src/config/settings.py`.

---

## 🎨 4. Frontend y Experiencia de Usuario

### 4.1. Bootstrap 5.3 (CSS Framework)
* **Rol**: Sistema de diseño responsivo y componentes de interfaz.
* **Justificación**:
  * Proporciona una interfaz moderna, limpia y altamente legible para terminales de Punto de Venta (POS), tablets y computadoras de escritorio.
  * Componentes prediseñados y probados: tablas dinámicas, modales de confirmación, tarjetas de métricas, insignias de estado (*badges*) y alertas contextuales.
  * Consumo vía CDN de alta disponibilidad para no saturar el repositorio de archivos estáticos pesados.

### 4.2. Bootstrap Icons (Versión 1.11.3)
* **Rol**: Iconografía vectorial SVG.
* **Justificación**:
  * Mejora la usabilidad y la carga cognitiva del usuario, permitiendo identificar rápidamente acciones clave (imprimir, anular, nuevo producto, alerta de stock bajo).

### 4.3. JavaScript Vanilla (ES6+)
* **Rol**: Interactividad y cálculo dinámico en el navegador del cliente.
* **Justificación**:
  * **Cero Dependencias**: No requiere compilar con Webpack, Vite ni Node.js.
  * **Cálculo en Tiempo Real**: Ejecuta el cálculo instantáneo de subtotales (15% y 0%), descuentos, IVA y total a pagar conforme el usuario agrega productos o altera cantidades en la pantalla de facturación, brindando una experiencia fluida e interactiva.

### 4.4. CSS3 `@media print` (Estándar RIDE de Facturación)
* **Rol**: Motor de adaptación para impresión física y generación de PDF.
* **Justificación**:
  * Al pulsar "Imprimir Factura", las reglas CSS `@media print` ocultan automáticamente barras de navegación, botones de acción y fondos, ajustando la tipografía y los márgenes a una hoja estándar **A4**.
  * Cumple con la distribución exigida por el SRI para el RIDE (*Representación Impresa de un Documento Electrónico*).

---

## ⚡ 5. Gestor de Paquetes y Entorno de Desarrollo (Tooling)

### 5.1. `uv` (Astral Software)
* **Rol**: Gestor de versiones de Python, dependencias y entornos virtuales.
* **Justificación**:
  * Desarrollado en **Rust**, es entre **10x y 100x más rápido** que herramientas tradicionales como `pip`, `poetry` o `pipenv`.
  * Genera un archivo de bloqueo determinista ([`uv.lock`](file:///Users/junior.mera@latam.com/Personal/facturador/uv.lock)) que garantiza que todos los estudiantes del curso trabajen con exactamente las mismas versiones de librerías, eliminando el clásico problema: *"En mi máquina sí funcionaba"*.
  * Permite ejecutar comandos directamente dentro del entorno virtual sin necesidad de activarlo manualmente (`uv run python manage.py ...`).

### 5.2. Estructura de Proyecto con `src/` Layout
* **Rol**: Organización física del código fuente.
* **Justificación**:
  * El patrón `src/` layout es el estándar moderno recomendado por la comunidad de Python para evitar la importación accidental de módulos locales desde el directorio raíz y asegurar que el código se ejecute tal cual como si estuviera instalado como un paquete formal.

---

## 🇪🇨 6. Especificación Normativa y Tributaria (SRI Ecuador)

El stack técnico incorpora de manera nativa la lógica fiscal del Ecuador sin intermediarios:

| Parámetro Tributario | Implementación en el Stack | Base Legal / Técnica |
| :--- | :--- | :--- |
| **Tarifa de IVA General (15%)** | Configuración nativa con clase `Decimal('15.00')` y `DecimalField`. | Ley Orgánica de Eficiencia Económica y Generación de Empleo. |
| **Tarifa de IVA Cero (0%)** | Soporte para bienes de primera necesidad y medicinas (`0.00%`). | Ley de Régimen Tributario Interno. |
| **Validación de Cédula** | Algoritmo de Módulo 10 sobre los 10 dígitos y código de provincia (01 a 24). | Norma del Registro Civil y SRI. |
| **Validación de RUC** | Algoritmos de Módulo 10 y Módulo 11 según el tercer dígito (Natural, Privada o Pública). | Ficha Técnica de Comprobantes Electrónicos SRI. |
| **Secuencial Oficial** | Formato de 15 caracteres `001-001-000000001` (Establecimiento - Punto de Emisión - Secuencial). | Reglamento de Comprobantes de Venta y Retención. |
| **Formas de Pago SRI** | Códigos estandarizados: `01` (Efectivo), `16` (Débito), `19` (Crédito), `20` (Transferencia). | Catálogo oficial de formas de pago SRI. |

---

## 👨‍🏫 7. Lección Pedagógica: ¿Por qué este Stack y no uno con React / Microservicios?

Un error muy común en estudiantes universitarios es caer en el **"Complejo de Sobreingeniería" (*Overengineering*)**: intentar resolver un problema de facturación local implementando microservicios en Docker, Kubernetes, React, Redux, Tailwind y bases de datos NoSQL.

### La Regla de Oro de la Arquitectura de Software:
> *"La mejor arquitectura no es la que usa la mayor cantidad de tecnologías de moda, sino la más simple que resuelve el 100% de los requisitos del negocio con la máxima confiabilidad y mantenibilidad."*

1. **Facilidad de Razonamiento**: Un monolito modular en Django permite entender el flujo completo de una venta en un solo archivo de servicio (`services.py`).
2. **Contexto Perfecto para la Inteligencia Artificial**: Un stack limpio, estandarizado y sin dependencias superfluas permite que asistentes de IA (como Antigravity o ChatGPT) generen código altamente preciso, sin confundir versiones incompatibles de paquetes de Node.js o librerías de estilos.
3. **Foco en el Negocio**: El valor de este proyecto está en la **lógica transaccional de inventarios y el cumplimiento del SRI**, no en configurar herramientas complejas de compilación de frontend.
