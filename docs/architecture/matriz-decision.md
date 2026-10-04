# Matriz de decisión — RutaSIT Arequipa

## Alternativas

- **A. Monolito modular:** Una única aplicación desplegable organizada internamente en módulos para recepción GPS, buses y rutas, cálculo de ETA, alertas y consultas. Reduce la complejidad de desarrollo y despliegue, aunque limita el escalamiento independiente de sus componentes.

- **B. Arquitectura orientada a eventos:** Las actualizaciones de posición GPS se procesan como eventos y son consumidas por componentes desacoplados encargados del cálculo de ETA, alertas y actualización de ubicaciones. Favorece el procesamiento asíncrono y la escalabilidad, pero introduce mayor complejidad operativa.

- **C. Microservicios:** El sistema se divide en servicios independientes para ubicación, rutas, ETA, alertas y consultas. Permite desplegar y escalar componentes por separado, pero aumenta la complejidad de comunicación, despliegue y monitoreo.

## Criterios y pesos (deben sumar 100 %)

| Criterio | Peso | Justificación (driver relacionado) |
|---|---:|---|
| Rendimiento en tiempo real | 25 % | QA-01: es el atributo crítico; el sistema debe procesar las posiciones de 300 buses enviadas cada 10 segundos y actualizar el ETA en un máximo de 15 segundos. |
| Tiempo y facilidad de implementación | 25 % | R-01 y R-02: el MVP debe estar en producción en 1 mes y será desarrollado por un equipo de solo 2 integrantes. |
| Simplicidad operativa | 15 % | R-02: un equipo de 2 integrantes debe poder desplegar, supervisar y mantener la solución sin asumir una infraestructura excesivamente compleja. |
| Escalabilidad | 15 % | QA-01: el flujo continuo de posiciones de 300 buses exige considerar el crecimiento de la carga sin comprometer el rendimiento crítico. |
| Fiabilidad y disponibilidad | 10 % | QA-02 y QA-03: el servicio debe mantenerse disponible durante su operación y procesar correctamente las actualizaciones válidas de posición. |
| Modificabilidad | 10 % | R-01 y R-02: con un plazo de 1 mes y un equipo de 2 integrantes, los cambios en rutas, reglas de cálculo y funcionalidades deben poder realizarse sin modificaciones extensas en todo el sistema. |
| **Total** | **100 %** | |

## Matriz (puntaje 1 = muy malo — 5 = excelente)

| Criterio (peso) | A | B | C |
|---|---:|---:|---:|
| Rendimiento en tiempo real (25 %) | 4 | 5 | 4 |
| Tiempo y facilidad de implementación (25 %) | 5 | 3 | 2 |
| Simplicidad operativa (15 %) | 5 | 3 | 2 |
| Escalabilidad (15 %) | 3 | 5 | 5 |
| Fiabilidad y disponibilidad (10 %) | 4 | 4 | 4 |
| Modificabilidad (10 %) | 4 | 4 | 5 |
| **Total ponderado** | **4.25** | **4.00** | **3.45** |

Total ponderado = Σ (peso × puntaje).

- **A:** 0.25×4 + 0.25×5 + 0.15×5 + 0.15×3 + 0.10×4 + 0.10×4 = **4.25**
- **B:** 0.25×5 + 0.25×3 + 0.15×3 + 0.15×5 + 0.10×4 + 0.10×4 = **4.00**
- **C:** 0.25×4 + 0.25×2 + 0.15×2 + 0.15×5 + 0.10×4 + 0.10×5 = **3.45**

## Revisión crítica de la respuesta de IA

La IA señaló que una arquitectura orientada a eventos o basada en microservicios ofrece mayores posibilidades de escalabilidad que un monolito modular. Aunque esta afirmación es válida como característica general de dichos estilos, sería exagerado concluir que RutaSIT necesita una arquitectura distribuida únicamente por la carga indicada en el caso.

Se verificó esta afirmación utilizando el driver de rendimiento de RutaSIT. Si 300 buses envían una posición cada 10 segundos, el sistema recibe en promedio:

**300 / 10 = 30 actualizaciones de posición por segundo.**

Este valor por sí solo no demuestra que un monolito modular sea incapaz de satisfacer el requisito. Además, el caso no especifica el tamaño de los mensajes, cantidad de usuarios concurrentes, complejidad del cálculo de ETA ni características de la infraestructura, por lo que no sería correcto inferir una necesidad de microservicios únicamente a partir de las 30 actualizaciones por segundo.

Por ello, el equipo considera la escalabilidad como un criterio importante, pero no suficiente para justificar la complejidad adicional de una arquitectura distribuida durante el MVP.

## Conclusión

Elegimos **A. Monolito modular**, con un resultado ponderado de **4.25/5**, frente a **4.00/5** de la arquitectura orientada a eventos y **3.45/5** de microservicios.

La alternativa seleccionada ofrece el mejor equilibrio para los drivers actuales de RutaSIT. Aunque la arquitectura orientada a eventos obtiene ventajas en rendimiento y escalabilidad, el monolito modular presenta una mayor adecuación al plazo de **1 mes**, al equipo de **2 integrantes** y al presupuesto limitado, reduciendo la complejidad de implementación y operación del MVP.

La decisión no implica descartar mecanismos asíncronos en el futuro. Los módulos se mantendrán claramente separados para facilitar la evolución del sistema y permitir que componentes con necesidades particulares de escalabilidad puedan desacoplarse posteriormente si las mediciones reales de carga lo justifican.

Ver [ADR-001](adr/001-estilo-arquitectonico.md).