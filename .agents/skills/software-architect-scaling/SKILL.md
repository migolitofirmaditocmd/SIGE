---
name: software-architect-scaling
description: Anti-spaghetti architecture, modular scalability, strict versioning control, clean domain boundaries, and incremental growth without massive rewrites.
---

# Modular Scalability & Anti-Spaghetti Architecture
**Master Standards**: Ibrahim García / Suite Atelier & Enterprise Projects  
**Philosophy**: High Cohesion, Low Coupling, Additive Growth, Semantic Versioning

---

## 🧭 1. El Manifiesto Anti-Spaghetti

El código espagueti no nace grande: nace cuando un desarrollador o una IA añade un "pequeño parche rápido" con un `if` anidado en una función existente, en lugar de modelar una capa modular. Con el tiempo, una función de 20 líneas se convierte en un monstruo de 600 líneas con 14 responsabilidades distintas.

### 🚫 Patrones Espagueti Estrictamente Prohibidos:
1. **Mega-Funciones Dios**: Funciones que validan entradas, consultan bases de datos, computan lógica de negocio, formatean UI y envían notificaciones al mismo tiempo.
2. **Efectos Secundarios Ocultos**: Modificar variables o estados globales dentro de funciones que aparentan ser de solo lectura o de cálculo.
3. **Acoplamiento Directo entre Módulos**: Hacer que el módulo A conozca la estructura interna de las celdas o tablas del módulo B, en lugar de pasar por un adaptador o contrato de interfaz.
4. **Parches de "Bandeja de Entrada"**: Resolver nuevos requerimientos apilando `else if` interminables en lugar de usar composición, mapas de estrategia (*Strategy Pattern*) o handlers dedicados.

---

## 🏗️ 2. Principios de Escalabilidad Modular

1. **Crecimiento Aditivo (Open-Closed Principle - Anti-Reescrituras MANDATORIO)**:
   - El sistema debe estar **abierto a la extensión pero cerrado a la modificación**.
   - **Queda terminantemente prohibido usar patrones rígidos que requieran rehacer o reescribir todo el sistema o partes críticas de él al implementar algo nuevo, agregar sucursales o features.**
   - Toda nueva funcionalidad debe integrarse de forma automática y transparente como una capa acumulativa desacoplada sin tocar ni desestabilizar el núcleo existente ya probado.
2. **Patrón de Resguardo Transaccional Obligatorio (Backup en RAM / Celdas)**:
   - En cualquier proceso de migración, reparación, reestructuración o inserción masiva que deba limpiar o reconstruir formatos y celdas, **es MANDATORIO capturar y guardar previamente el estado de las variables y valores de celdas en memoria RAM (matriz bidimensional) o propiedades**, para restaurarlas de forma íntegra e instantánea una vez finalizado el proceso (ej: patrón implementado en `repararSistemaTienda()`, `_reconstruirKardexConRespaldo()` y `reconstruirMaestroConRespaldo()`).
3. **Separación Estricta de Capas**:
   - **Capa de Transporte / I/O**: Lectura y escritura cruda (Google Sheets API, Supabase, LocalStorage, HTTP).
   - **Capa de Dominio / Negocio**: Lógica pura, cálculos matemáticos y validaciones. Cero llamadas a APIs externas aquí; opera solo con datos limpios en memoria.
   - **Capa de Presentación / UI**: Modales HTML, vistas móviles, renderizado visual.
4. **Contratos e Interfaces Claras**:
   - Cada módulo debe exponer funciones públicas claras con parámetros bien definidos y retornar estructuras previsibles.
   - Nada de pasar objetos amorfos con 40 propiedades no documentadas.

---

## 📦 3. Control de Versiones y Protocolo de Releases

### A. SemVer + Nomenclatura por Épocas (Epoch System)
- **MAJOR (`X.0.0`)**: Cambios de época de arquitectura o breaking changes fundamentales. Requiere plan previo y aprobación explícita.
- **MINOR (`1.X.0`)**: Nuevas features, módulos o pantallas que no rompen lo existente.
- **PATCH (`1.0.X`)**: Corrección de bugs o mejoras de rendimiento internas.
- **HOTFIX ITERATIVO (`1.0.1a`, `1.0.1b`)**: Sufijos de letras para pruebas y estabilización local.

### B. Doble Versionado Mandatorio
Todo cambio debe registrarse en dos dimensiones:
1. **Changelog Técnico Tradicional** (`documentacion/historial_versiones.md`): Con jerga técnica completa, funciones modificadas, parámetros y arquitectura.
2. **Changelog Público / Operativo** (`CHANGELOG_PUBLIC.md`): En formato **Beneficio Operativo (User-Friendly)** libre de jerga de código, enfocado en el valor real para tiendas, gerencias y dirección.

### C. Regla de Oro de Git
- **Queda estrictamente prohibido hacer `git commit` o `git push` a GitHub** sin confirmación explícita previa de Ibrahim.
