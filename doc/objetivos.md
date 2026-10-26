# 🎯 Objetivos del Proyecto: Facturador Simple Ecuador

Este documento establece el marco de referencia y las metas del proyecto **Facturador Simple Ecuador**. La correcta definición de objetivos al inicio de un desarrollo permite alinear las expectativas de negocio, definir el alcance tecnológico y servir como directriz inmutable al guiar herramientas de Inteligencia Artificial para la generación de código.

---

## 📌 1. Objetivo General

> **Desarrollar e implementar una aplicación web de facturación e inventario orientada al entorno comercial de Ecuador, aplicando el patrón arquitectural Modelo-Vista-Controlador (MVC) con Python y Django, persistencia en SQLite y una interfaz responsiva en Bootstrap 5, que garantice la deducción y reposición atómica de stock en tiempo real, el cumplimiento estricto de las normativas de validación de comprobantes e identificaciones del Servicio de Rentas Internas (SRI), y la segregación de funciones mediante un esquema de Control de Acceso Basado en Roles (RBAC).**

---

## 🎯 2. Objetivos Específicos

Para alcanzar el objetivo general, el proyecto se desglosa en los siguientes tres objetivos específicos:

### Objetivo Específico 1: Sincronización Transaccional del Inventario (Kardex y ACID)
* **Descripción**: Diseñar e implementar un motor de persistencia transaccional que vincule la facturación directamente con el control de inventarios, asegurando que cada emisión de factura reste inmediatamente las existencias del catálogo y que cada anulación las restablezca de forma automática.
* **Métrica / Criterio de Logro**: 
  - Ejecutar todas las operaciones de inventario bajo bloques atómicos (`transaction.atomic`) y bloqueos a nivel de fila (`select_for_update`) para evitar condiciones de carrera (*race conditions*).
  - Registrar el 100% de las entradas, salidas y anulaciones en un historial de movimientos (Kardex) trazable con fecha, usuario, tipo y variación de stock anterior vs. nuevo.

### Objetivo Específico 2: Cumplimiento Tributario y Algoritmos de Validación SRI Ecuador
* **Descripción**: Integrar los estándares y algoritmos tributarios exigidos por el Servicio de Rentas Internas (SRI) del Ecuador para la emisión de comprobantes de venta.
* **Métrica / Criterio de Logro**:
  - Validar identificaciones ecuatorianas mediante código algorítmico: Cédula de 10 dígitos (módulo 10), RUC de persona natural (cédula + '001'), RUC de sociedades privadas/extranjeras (módulo 11 con tercer dígito 9), RUC de entidades públicas (módulo 11 con tercer dígito 6) y Consumidor Final (`9999999999999`).
  - Calcular correctamente los importes fiscales aplicando la tarifa vigente de IVA (15% o 0%), subtotal sin impuestos, descuento y total a pagar.
  - Generar el secuencial oficial de factura de 15 caracteres (`001-001-000000001`) y el diseño para impresión física en formato RIDE (hoja A4).

### Objetivo Específico 3: Seguridad, Segregación de Roles (RBAC) y Experiencia de Usuario
* **Descripción**: Construir un sistema de autenticación y autorización que proteja los recursos sensibles mediante la separación de responsabilidades y ofrezca una interfaz fluida e intuitiva.
* **Métrica / Criterio de Logro**:
  - Implementar tres roles bien delimitados:
    - **Administrador**: Control total sobre catálogo, inventario, facturas, clientes, configuración de la empresa emisora y usuarios.
    - **Asesor Comercial**: Emisión, consulta e impresión de facturas y gestión de clientes.
    - **Bodeguero**: Alta/edición de productos y ejecución de ajustes o ingresos manuales de existencias.
  - Ofrecer una pantalla de facturación dinámica con cálculo automático de totales mediante JavaScript en tiempo real y alertas visuales para stock bajo.

---

## 👨‍🏫 Nota Pedagógica para los Estudiantes

### ¿Por qué redactar objetivos antes de codificar?
En la industria del software, un proyecto sin objetivos claros sufre de **"Scope Creep"** (expansión incontrolada del alcance): el programador agrega funcionalidades al azar, la base de datos pierde consistencia y el cliente nunca recibe lo que realmente requería.

### ¿Cómo ayudan los objetivos a la Inteligencia Artificial?
Cuando alimentamos una IA (como Antigravity o ChatGPT) con un objetivo general y objetivos específicos claros:
1. **Delimitan el contexto**: La IA sabe qué librerías o tecnologías usar (Django, SQLite, Bootstrap 5) y qué evitar (evita agregar frameworks pesados o librerías innecesarias).
2. **Definen reglas de negocio no negociables**: Por ejemplo, al especificar *“Ecuador / SRI / IVA 15% / Módulo 10”*, evitamos que la IA asuma normativas fiscales de otros países (como el RUT de Chile o el RFC de México).
3. **Establecen el criterio de término de la tarea**: La IA puede evaluar si su implementación satisface los criterios técnicos de aceptación.
