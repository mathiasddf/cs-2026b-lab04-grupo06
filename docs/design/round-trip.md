# Análisis Round-trip — RutaSIT Arequipa (E6)

Comparación entre el Diagrama de Clases diseñado manualmente (E1) y el Diagrama de Clases generado por ingeniería inversa mediante herramienta (`pyreverse` / `IntelliJ IDEA`).

## Cuadro Comparativo de Diferencias

| # | Elemento | Diagrama Original (E1) | Diagrama Generado (E6) | Causa de la Diferencia | Acción Tomada |
|---|----------|------------------------|------------------------|------------------------|---------------|
| 1 | **Multiplicidades explícitas** | Se especifican asociaciones explícitas (`1..*`, `0..*`) entre `Ruta` y `Paradero`. | Las relaciones se muestran como agregaciones/asociaciones genéricas sin cardinalidad explícita. | Las herramientas de ingeniería inversa estática no derivan multiplicidades numéricas exactas a partir del código type-hinted básico. | **Documentar la limitación:** Se mantiene la especificación de multiplicidades en el diagrama UML de diseño (E1). |
| 2 | **Interfaz / Puerto `IServicioMapas`** | Representada con el estereotipo `<<interface>>` y puerto desacoplado. | Generada como una clase abstracta (`ABC`) sin el estereotipo visual explícito de puerto UML. | Mapeo por defecto de Python (`abc.ABC`) hacia el parser UML. | **Corregir el código:** Se ajustaron los decoradores y typing para asegurar la visibilidad de la abstracción. |
| 3 | **Tipos Enums (`EstadoBus`)** | Representado como un bloque `<<enum>>` nativo. | Generado como una clase heredada de `Enum`. | Tratamiento estándar de lenguajes orientados a objetos donde Enums se representan como clases hijas de la librería base. | **Documentar la limitación:** Se acepta la representación nativa generada por la herramienta. |