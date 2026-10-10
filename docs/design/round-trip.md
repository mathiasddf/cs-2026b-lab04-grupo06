# Round-Trip: Comparación Código vs Diseño (E6)

Al aplicar ingeniería inversa con `pyreverse` sobre el código de `src/ubicaciones/dominio.py`, se detectaron las siguientes diferencias en comparación con el diagrama original de diseño (`clases.puml`):

| Diferencia observada | Causa | Acción |
|----------------------|-------|--------|
| **No aparecen los estereotipos `<<puerto>>` y `<<adaptador>>`** | La herramienta `pyreverse` no soporta estereotipos personalizados de UML. | Ninguna: limitación de la herramienta; el diagrama de diseño en PlantUML se mantiene. |
| **No hay multiplicidades ni se dibuja la relación entre `Bus` y `PosicionGPS`** | `pyreverse` no infiere asociaciones directamente desde colecciones tipadas (`List[PosicionGPS]`), las muestra como atributos de texto. | Ninguna: el código Python no expresa multiplicidades por defecto. El diagrama de diseño es el correcto. |
| **La interfaz `ServicioMapasExterno` aparece como clase normal** | Python implementa las interfaces utilizando Abstract Base Classes (`ABC`), por lo que la herramienta las dibuja como clases estándar. | Aceptable en Python; se documenta la limitación técnica de representación. |