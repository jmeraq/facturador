# 📚 Documentación del Proyecto: Facturador Simple Ecuador

Bienvenido a la carpeta de documentación (`doc/`) del sistema **Facturador Simple para Ecuador**. 

Este conjunto de documentos ha sido estructurado con un doble propósito pedagógico:
1. **Fundamentos de Ingeniería de Software**: Demostrar a los estudiantes cómo se conceptualiza, planifica y especifica formalmente un sistema antes de tirar una sola línea de código.
2. **Contexto Esencial para Inteligencia Artificial**: Ilustrar cómo la especificación formal de requerimientos actúa como la **Fuente Única de Verdad (*Ground Truth*)** para alimentar y guiar asistentes de IA (como Antigravity, Claude, ChatGPT o Copilot), reduciendo alucinaciones y garantizando código coherente con la normativa tributaria local (SRI) y las mejores prácticas de arquitectura.

---

## 🗂️ Orden de Creación y Prioridad de Documentos

El orden numérico de los archivos representa la **secuencia metodológica** que se debe seguir en la ingeniería de software antes y durante el desarrollo asistido por Inteligencia Artificial:

| Prioridad / Orden | Documento | Propósito en el Ciclo de Vida |
| :---: | :--- | :--- |
| **01** | **[01_objetivos.md](file:///Users/junior.mera@latam.com/Personal/facturador/doc/01_objetivos.md)** | **Paso 1: Delimitar el Rumbo**. Define el objetivo general y los objetivos específicos (SMART). Sin metas claras, el proyecto pierde el rumbo. |
| **02** | **[02_requisitos.md](file:///Users/junior.mera@latam.com/Personal/facturador/doc/02_requisitos.md)** | **Paso 2: Especificar el Contrato**. Detalla qué debe hacer el software (RF) y sus restricciones de calidad, seguridad y leyes SRI (RNF). |
| **03** | **[03_casos_de_uso.md](file:///Users/junior.mera@latam.com/Personal/facturador/doc/03_casos_de_uso.md)** | **Paso 3: Modelar Procesos**. Define la interacción paso a paso entre actores y sistema, con flujos principales, alternativos y excepciones. |
| **04** | **[04_stack_tecnologico.md](file:///Users/junior.mera@latam.com/Personal/facturador/doc/04_stack_tecnologico.md)** | **Paso 4: Seleccionar Plataforma**. Justifica las herramientas elegidas (Python 3.12, Django 6, SQLite, Bootstrap 5, `uv`) y evita la sobreingeniería. |
| **05** | **[05_arquitectura_y_modelo_datos.md](file:///Users/junior.mera@latam.com/Personal/facturador/doc/05_arquitectura_y_modelo_datos.md)** | **Paso 5: Estructurar la Solución**. Diseña la arquitectura MVC/MVT, la capa de servicios desacoplada y los flujos transaccionales ACID. |
| **06** | **[06_diseno_base_de_datos.md](file:///Users/junior.mera@latam.com/Personal/facturador/doc/06_diseno_base_de_datos.md)** | **Paso 6: Modelar la Persistencia**. Define el DER físico, diccionario de datos, inmutabilidad contable (*snapshotting*), índices y DDL SQL. |
| **07** | **[07_guia_contexto_para_ia.md](file:///Users/junior.mera@latam.com/Personal/facturador/doc/07_guia_contexto_para_ia.md)** | **Paso 7: Conectar con la IA**. Guía pedagógica sobre cómo usar los documentos anteriores como contexto (*prompt engineering*) para evitar alucinaciones. |
| **08** | **[08_plan_de_implementacion_y_pruebas.md](file:///Users/junior.mera@latam.com/Personal/facturador/doc/08_plan_de_implementacion_y_pruebas.md)** | **Paso 8: Ejecutar y Validar**. Hoja de ruta modular en 7 fases, árbol de archivos exacto, casos de prueba (QA) y Meta-Prompt para la IA. |

---

## 💡 Mensaje para los Alumnos

> *"El código es la última fase de la ingeniería de software, no la primera. Quien no sabe con exactitud lo que va a construir, tampoco sabrá evaluar si la Inteligencia Artificial le ha entregado una solución correcta o un problema disfrazado de código."*
