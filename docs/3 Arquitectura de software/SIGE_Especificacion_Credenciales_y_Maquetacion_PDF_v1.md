# SIGE — Especificación Técnica de Credenciales y Maquetación PDF
### Sistema Integral de Gestión Escolar · Escuela Secundaria Mixta 5
**Versión:** 1.0 | **Estado:** Aprobado para Planificación e Implementación  
**Módulos:** CRE (Credencialización) / QR (Identificación criptográfica)  
**Trazabilidad:** RF-CRE-01, RF-CRE-02, RN-CRE-01, RN-CRE-02, RN-CRE-03, RN-QR-01 a 06, OE-01, KPI-06  

---

## 1. Contexto Operativo y Justificación del Cambio

Durante la etapa inicial de pilotaje y transición de SIGE, se utilizó la generación de códigos QR compactos en formato PNG para imprimirse como **stickers térmicos adhesivos**. Dicha solución permitió incorporar rápidamente la tecnología de escaneo de asistencia a los estudiantes que ya portaban una credencial física plastificada otorgada en ciclos anteriores.

Habiéndose cubierto dicha fase y con miras a la atención de **estudiantes de nuevo ingreso** (quienes carecen por completo de credencial) y de **reposiciones integrales por extravío o deterioro**, la dirección y administración escolar establecieron que SIGE debe encargarse de la **generación física completa de la credencial escolar (anverso y reverso)**.

A partir de esta versión:
1. **Se descarta el uso de stickers provisionales** como método de credencialización estándar o de reposición.
2. Toda credencial física producida por SIGE contiene dos caras: **Parte Frontal (Anverso)** y **Parte Trasera (Reverso)** con el código QR criptográfico incorporado de origen.
3. Se implementan dos modalidades operativas nativas:
   - **Modalidad Masiva por Lote:** orientada a nuevo ingreso y grupos completos, consolidada en documentos PDF tamaño Carta en formato horizontal (Landscape) que contienen 4 credenciales completas por página (8 caras en total).
   - **Modalidad Individual:** orientada a reposiciones excepcionales (pérdida, robo o daño) y altas extemporáneas, emitiendo la credencial completa actualizada con su nuevo token QR.

---

## 2. Geometría y Maquetación de la Hoja de Impresión

### 2.1 Sustrato y Dimensiones Generales
- **Tamaño de página:** Carta estadounidense (**Letter: 215.9 mm × 279.4 mm** / 8.5 × 11 pulgadas).
- **Orientación:** **Horizontal (Landscape: 279.4 mm de ancho × 215.9 mm de alto)**.
- **Resolución gráfica:** 300 DPI estándar (11.811 píxeles por milímetro) para nitidez tipográfica y decodificación óptica de alta velocidad.
- **Estándar de tarjeta:** **CR-80 vertical** (dimensiones físicas finales de corte: **54.0 mm de ancho × 85.6 mm de alto**).

### 2.2 Distribución en Matriz 2×4 (4 Credenciales Completas por Página)
Cada página Carta horizontal alberga exactamente **4 credenciales escolares completas**, lo que equivale a **8 caras individuales** (4 anversos y 4 reversos). 

Para garantizar un tamaño físico contundente y óptimo para portarse en micas estándar de credencial escolar (65 × 95 mm o 70 × 100 mm), las dimensiones impresas se ampliaron a **61.5 mm de ancho × 97.4 mm de alto** (+30 % de superficie útil respecto al estándar base CR-80 de PVC).

Para facilitar el corte con guillotina y permitir el doblado tipo folleto (*fold-over*) o laminación directa por pares, **el anverso (frente) y el reverso (detrás) de cada estudiante se colocan de forma horizontalmente contigua**:

```
+-----------------------------------------------------------------------------------------------+
|  Margen Superior: 9.0 mm (Encabezado institucional en y = 209.4 mm)                           |
|                                                                                               |
|  +----------------+  +----------------+    +----------------+  +----------------+             |
|  |                |  |                |    |                |  |                |             |
|  |  ESTUDIANTE 1  |  |  ESTUDIANTE 1  |    |  ESTUDIANTE 2  |  |  ESTUDIANTE 2  |             |
|  |     FRENTE     |  |     DETRÁS     |    |     FRENTE     |  |     DETRÁS     |             |
|  |   (Anverso)    |  |   (Reverso)    |    |   (Anverso)    |  |   (Reverso)    |             |
|  | 61.5 × 97.4 mm |  | 61.5 × 97.4 mm |    | 61.5 × 97.4 mm |  | 61.5 × 97.4 mm |             |
|  +----------------+  +----------------+    +----------------+  +----------------+             |
|                                                                                               |
|  Espaciado Vertical entre Filas: 4.3 mm                                                       |
|                                                                                               |
|  +----------------+  +----------------+    +----------------+  +----------------+             |
|  |                |  |                |    |                |  |                |             |
|  |  ESTUDIANTE 3  |  |  ESTUDIANTE 3  |    |  ESTUDIANTE 4  |  |  ESTUDIANTE 4  |             |
|  |     FRENTE     |  |     DETRÁS     |    |     FRENTE     |  |     DETRÁS     |             |
|  |   (Anverso)    |  |   (Reverso)    |    |   (Anverso)    |  |   (Reverso)    |             |
|  | 61.5 × 97.4 mm |  | 61.5 × 97.4 mm |    | 61.5 × 97.4 mm |  | 61.5 × 97.4 mm |             |
|  +----------------+  +----------------+    +----------------+  +----------------+             |
|                                                                                               |
|  Margen Inferior: 7.8 mm                                                                      |
+-----------------------------------------------------------------------------------------------+
   |<- 8.0 mm ->|        |<- 5.8 mm ->|        |<- 5.8 mm ->|        |<- 5.8 mm ->|   |<- 8.0 mm ->|
```

### 2.3 Cálculo Milimétrico de Posicionamiento

| Eje | Dimensión Total Hoja | Espacio Ocupado por Tarjetas | Margen Disponible | Distribución de Espaciado |
| :--- | :--- | :--- | :--- | :--- |
| **Horizontal (X)** | 279.4 mm | 4 tarjetas × 61.5 mm = **246.0 mm** | **33.4 mm** | Márgenes laterales: **8.0 mm** c/u.<br>Separaciones entre columnas (3): **5.80 mm** c/u. |
| **Vertical (Y)** | 215.9 mm | 2 filas × 97.4 mm = **194.8 mm** | **21.1 mm** | Margen superior: **9.0 mm**.<br>Margen inferior: **7.8 mm**.<br>Separación central entre filas (1): **4.30 mm**. |

- **Guías de corte:** Líneas continuas tenues de color gris neutro (`#94A3B8`, grosor 0.5 pt) impresas alrededor de cada cara y en los vértices exteriores de la hoja para guiar la guillotina sin invadir el arte.
- **Manejo de remanentes (Páginas incompletas):** Si el número total de alumnos a imprimir en un grupo no es múltiplo de 4 (ej. 38 alumnos en un grupo de 2° o 3°), las primeras 9 páginas contienen 4 alumnos completos (36 alumnos = 72 caras). La décima página contendrá a los 2 alumnos restantes ocupando la Fila 1 (4 caras), dejando los 4 cuadrantes de la Fila 2 completamente en blanco pero preservando las líneas guía de corte.

---

## 3. Especificación Gráfica y Contenido de las Caras

### 3.1 Cara Frontal (Anverso) — Identidad del Alumno con Foto y QR Contiguos
Diseñada con base en la plantilla institucional histórica (`Plantilla de credenciales.xlsx`), integrando la fotografía oficial del alumno y su código QR de forma contigua en el cuerpo central, con tipografías extra grandes y de alto contraste para máxima legibilidad física:

```
+-------------------------------------------------------------+
|  [LOGO JALISCO]                          [ESCUDO OFICIAL]   |  <- Cabecera institucional
|  SECUNDARIA 5 MIXTA                    C.C.T. 14EES0336D   |  <- CCT a 25 pt negrita
|-------------------------------------------------------------|
|  [ ALUMNO · MATRÍCULA: 16092179 ]    [ 2° D · MATUTINO ]    |  <- Insignias a 23 pt negrita
|-------------------------------------------------------------|
|                                                             |
|   +-------------------+          +-------------------+      |
|   |                   |          | # # # # # # # # # |      |
|   |    FOTOGRAFÍA     |          | #   CÓDIGO QR   # |      |  <- FOTO Y QR CONTIGUOS
|   |      OFICIAL      |          | #  ASISTENCIA   # |      |     (Resolución 300 DPI)
|   |     DEL ALUMNO    |          | #   EN PUERTA   # |      |
|   |    (22 × 26 mm)   |          | # # # # # # # # # |      |
|   +-------------------+          +-------------------+      |
|    Fotografía Oficial            Código de Asistencia       |
|                                                             |
|=============================================================|
|             IBARRA MEJÍA CARMEN SCARLTT                     |  <- Nombre del alumno (34 pt negrita)
|=============================================================|
|  CALLE: AV. CONSTITUCIÓN No. 450                            |  <- Ficha amarilla (#FFFF9B)
|  COLONIA: CENTRO BARRANQUITAS                               |     Tipografías extra grandes
|  CIUDAD: GUADALAJARA, JAL.                 C.P.: 44280      |     a 25-28 pt negrita
|  TEL: 33-3614-2289                         SANGRE: O+       |
|  ALERGIAS: NINGUNA                                          |
|  CICLO: 2026-2027                      VENCE: JULIO 2028    |
+-------------------------------------------------------------+
```

- **Paleta de color:**
  - Azul Institucional: `#1A365D` (cabeceras y elementos primarios).
  - Dorado Institucional: `#D69E2E` (filetes decorativos y realces).
  - Fondo: Blanco puro (`#FFFFFF`) o Marfil suave (`#F8FAFC`).
  - Tipografía: Familia Sans-Serif limpia del sistema (`Segoe UI`, `Arial` o `DejaVu Sans`).

- **Procesamiento e Integración Fotográfica (RN-CRE-04):**
  - **Origen de la imagen:** Se consulta la ruta física indexada en la columna `photo_path` de la entidad `STUDENT` en la base de datos PostgreSQL.
  - **Pipeline gráfico:** La imagen binaria se carga en memoria mediante Pillow (`PIL.Image`), se verifica su integridad contra `photo_sha256`, se aplica transposición de orientación EXIF (`ImageOps.exif_transpose`) y se convierte a espacio de color RGB.
  - **Ajuste y escalado:** La imagen se re-escala con interpolación bicúbica (`LANCZOS`) a resolución nativa de 300 DPI para encajar perfectamente en el recuadro delimitador de **26.0 mm de ancho × 32.5 mm de alto** (proporción 4:5 / `73.7 pt × 92.1 pt` en ReportLab), evitando cualquier deformación anamórfica.
  - **Marco contenedor:** Se dibuja un marco perimetral fino de 0.5 pt en color gris suave (`#CBD5E0`) con esquinas ligeramente redondeadas (radio de curvatura de 1.5 mm).
  - **Manejo de excepciones:** Si el archivo en `photo_path` no existe en disco o se encuentra corrupto, el motor de credencialización aborta la inclusión de ese estudiante e incluye la incidencia `ERROR_ARCHIVO_FOTOGRAFIA` en la respuesta de validación previa (RN-CRE-01).

### 3.2 Cara Trasera (Reverso) — Código QR y Datos de Seguridad Médica
Diseñada para validación en el punto de control de asistencia y respuesta ante emergencias escolares:

```
+------------------------------------+
|  SISTEMA INTEGRAL DE GESTIÓN (SIGE)|  <- Encabezado de seguridad
|====================================|
|                                    |
|        +------------------+        |
|        |                  |        |
|        |    CÓDIGO QR     |        |  <- Token QR criptográfico (HMAC-SHA256)
|        |    ASISTENCIA    |        |     Alta resolución con quiet zone
|        |                  |        |     (Tamaño nativo ~32 × 32 mm)
|        +------------------+        |
|       CÓDIGO DE ASISTENCIA         |
|                                    |
|   TIPO DE SANGRE: O+               |  <- Datos médicos esenciales
|   ALERGIAS: NINGUNA                |     para protocolos de protección civil
|                                    |
|   CONTACTO DE EMERGENCIA:          |  <- Datos del tutor legal principal
|   MONICA CASILLAS (TUTOR)          |
|   TEL: 33-3403-3752                |
|                                    |
| Esta credencial es personal e      |  <- Leyenda legal de validez oficial
| intransferible. Válida únicamente  |
| durante el ciclo escolar indicado. |
+------------------------------------+
```

- **Privacidad del código QR (RNF-SEG-02 / RN-QR-02):** El código QR codifica **únicamente el token UUIDv4 opaco** emitido y firmado por el backend. No almacena texto con nombre, matrícula, CURP ni teléfono en claro, impidiendo la lectura no autorizada por aplicaciones comerciales de escaneo.
- **Calibración óptica OpenCV:** La generación de la imagen QR en el reverso utiliza la rutina adaptativa probada de SIGE (`ERROR_CORRECT_Q` / `ERROR_CORRECT_M` con `box_size=8`, `border=3`), asegurando el 100 % de legibilidad ante el detector de OpenCV y cámaras de terminales móviles.

---

## 4. Modalidades del Motor de Generación (Módulo CRE)

### 4.1 Modalidad A: Generación Masiva por Lotes (`CREDENCIAL_LOTE`)
- **Disparador:** Solicitud administrativa para un grupo escolar completo (ej. nuevo ingreso de 1° de secundaria o apertura de ciclo escolar).
- **Proceso:**
  1. Filtra estudiantes en estatus `ACTIVO` pertenecientes al `group_id` indicado.
  2. Valida precondiciones (RN-CRE-01): debe contar con token QR `VIGENTE` y fotografía oficial cargada en el expediente.
  3. Quienes no cumplan la condición se excluyen y se registran en la lista de pendientes (`SIN_FOTOGRAFIA` o `SIN_QR_VIGENTE`).
  4. Agrupa a los estudiantes en bloques de 4 personas por página.
  5. Renderiza el documento PDF en ReportLab colocando para cada estudiante su anverso y reverso contiguos en la cuadrícula 2×4.
  6. Entrega el archivo en streaming binario (`application/pdf`) nombrado según el grupo: `credenciales_<grado><letra>_<turno>.pdf`.

### 4.2 Modalidad B: Reposición Individual (`CREDENCIAL_INDIVIDUAL`)
- **Disparador:** Reposición por pérdida, robo, deterioro físico o corrección de datos tras una revocación formal de token (RF-QR-03 / RN-CRE-03).
- **Proceso:**
  1. Recibe el `entity_id` del estudiante afectado.
  2. Verifica que tenga un nuevo token QR `VIGENTE` (emitido al revocar el anterior).
  3. Renderiza de forma exclusiva las dos caras del estudiante:
     - **Opción PDF Individual:** Hoja tamaño Carta con el par Frente y Reverso centrado y marcas de corte para impresión rápida en oficina.
     - **Opción PNG de Alta Resolución:** Archivo comprimido con `frente.png` y `reverso.png` a 300 DPI estándar para alimentación en impresoras térmicas de PVC (tarjetas pre-cortadas).
  4. Entrega el archivo directamente al operador sin necesidad de regenerar el lote del grupo.

---

## 5. Matriz de Trazabilidad de Reglas de Negocio

| Regla de Negocio | Enunciado Técnico | Implementación en Maquetación |
| :--- | :--- | :--- |
| **RN-CRE-01** | Solo estudiantes `ACTIVO` con QR `VIGENTE` y fotografía cargada son elegibles para credencialización completa. | El motor de exportación valida la tríada `(ACTIVO, QR_VIGENTE, PHOTO_PATH IS NOT NULL)`. Cualquier omisión excluye al estudiante del PDF y lo lista en la respuesta de vista previa (`SIN_FOTOGRAFIA` o `SIN_QR_VIGENTE`). |
| **RN-CRE-02** | Maquetación masiva en hoja Carta horizontal con 4 credenciales completas por página (matriz 2×4). | Canvas de ReportLab configurado a `pagesize=(279.4*mm, 215.9*mm)`, ubicando a los estudiantes de 4 en 4 con anverso y reverso contiguos por fila. |
| **RN-CRE-03** | Toda reposición por pérdida, robo o daño emite la credencial completa (anverso y reverso) de forma individual. | Endpoint `/credentials/exports/` procesa `mode=CREDENCIAL_INDIVIDUAL` emitiendo ambas caras con el nuevo token vigente, prohibiendo stickers parciales. |
| **RN-CRE-04** | Integración automatizada de la fotografía oficial del estudiante desde la base de datos. | Lectura de `photo_path`, verificación de hash `photo_sha256`, corrección EXIF y renderizado a 300 DPI en recuadro frontal de 26 × 32.5 mm. |
| **RN-QR-02** | El código QR no contiene datos personales legibles en claro. | El payload codificado en el QR del reverso es estrictamente el UUIDv4 opaco verificado con HMAC-SHA256. |
| **RN-TRX-01/02** | Principio de minimización y protección de datos de menores. | No se almacenan copias PDF de las credenciales generadas en el disco del servidor; se transmiten directamente al cliente en memoria. |

