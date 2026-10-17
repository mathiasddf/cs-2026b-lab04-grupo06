# Bitácora de uso de IA — RutaSIT Arequipa (Laboratorio 05)

| # | Fecha | Herramienta | Prompt (resumen) | Qué propuso la IA | Qué verificamos o corregimos | Decisión |
|---|-------|-------------|------------------|-------------------|------------------------------|----------|
| 1 | 10/10/2026 | Gemini | Generar el diagrama de clases en PlantUML para el entregable E1 basado en el ADR-001 (monolito modular) y la historia de usuario de consulta de ETA.[cite: 1] | Propuso las entidades clave (`Bus`, `Ruta`, `Paradero`, `Viaje`, `PosicionGPS`), una enumeración y un servicio base de ubicaciones.[cite: 1] | Se revisó la lista de verificación: se aseguraron multiplicidades explícitas en ambos extremos de todas las asociaciones, se tiparon los atributos con visibilidad y se estructuró el puerto `ServicioMapasExterno`.[cite: 1] | Aceptada[cite: 1] |
| 2 | 10/10/2026 | Gemini | Generar el diagrama de secuencia en PlantUML para el entregable E2 correspondiente al flujo crítico de cálculo de ETA (HU-03). | Propuso la secuencia de interacciones entre los componentes del sistema para procesar el cálculo de tiempos en menos de 15 segundos. | Se verificó que cada mensaje enviado corresponda exactamente a una operación expuesta en las clases receptoras definidas en el E1. | Aceptada |
| 3 | 10/10/2026 | Gemini | Generar el diagrama de actividades en PlantUML para el entregable E4 enfocado en el proceso de "Detección y aviso de un desvío" para RutaSIT Arequipa. | Propuso un flujo con particiones (swimlanes), decisiones condicionales y un bloque paralelo (`fork / end fork`) para la detección de desvío y cálculo de ETA. | Se validó que cumpliera estrictamente con la tabla de la guía (mínimo 3 particiones, decisiones y fork/join) y se ajustó con la retroalimentación de validación del proceso real con el compañero. | Aceptada |
| 4 | 10/10/2026 | Gemini | Generar el diagrama de paquetes en PlantUML para el entregable E5 basado en el ADR-001 (monolito modular) de RutaSIT Arequipa. | Propuso los paquetes modulares (`buses`, `rutas`, `ubicaciones`, `eta`, `compartido`), relaciones etiquetadas y una nota explicando la regla de dependencias (C4 sin ciclos). | Se verificó que no existieran dependencias circulares entre los paquetes y que se correspondiera directamente con la arquitectura de módulos definida en el ADR-001. | Aceptada |
| 5 | 10/10/2026 | Gemini | Aplicar el Prompt IA 3 (Auditor de consistencia) para evaluar la coherencia cruzada y las reglas C1 a C5 entre los diagramas del laboratorio (E7). | Propuso una matriz de hallazgos comparando los diagramas e identificando una aparente inconsistencia en transiciones de estado. | Se contrastó el informe de la IA con los diagramas E3 y E4, validando correctamente que se trataba de un falso positivo de la IA y documentándolo. | Aceptada |

## Anexo: prompts completos

### Prompt 1 (E1: Diagrama de Clases)

Actúa como un Arquitecto de Software experto. Basándote en la decisión tomada en nuestro ADR-001 de usar un monolito modular para *RutaSIT Arequipa* (enfocado en procesar 300 buses cada 10 segundos y calcular el ETA en menos de 15 segundos) y en la historia de usuario sobre la consulta de la ubicación y ETA del bus, genera un diagrama de clases en PlantUML que represente los módulos internos (ubicaciones, rutas, buses y cálculo de ETA), incluyendo al menos 6 clases, 1 interfaz como puerto hacia servicios externos (como mapas), una enumeración para los estados del bus, y atributos tipados con visibilidad.

### Prompt 2 (E2: Diagrama de Secuencia)

Actúa como un Arquitecto de Software experto. Basándote en el diseño de clases anterior y en la historia de usuario de consulta de ETA (HU-03) para *RutaSIT Arequipa*, genera un diagrama de secuencia en PlantUML para el flujo crítico de cálculo de ETA, mostrando la interacción entre los actores y los módulos del monolito modular.

### Prompt 3 (E4: Diagrama de Actividades)

Actúa como un Arquitecto de Software experto. Basándote en el caso *RutaSIT Arequipa* y en la tabla de la guía de laboratorio, genera un diagrama de actividades en PlantUML para el proceso de **"Detección y aviso de un desvío"** (E4), asegurando que incluya al menos 3 particiones (swimlanes), 2 o más decisiones con `if / else`, y una ejecución paralela con `fork / end fork`.

### Prompt 4 (E5: Diagrama de Paquetes)

Actúa como un Arquitecto de Software experto. Basándote en el ADR-001 de RutaSIT Arequipa (monolito modular) y en la tabla de la guía de laboratorio, genera un diagrama de paquetes en PlantUML para el entregable E5 que incluya los paquetes correspondientes a cada módulo (ubicaciones, rutas, buses y cálculo de ETA), un paquete compartido, relaciones y dependencias etiquetadas, y una nota explícita con la regla de dependencias (C4 sin ciclos).

### Prompt 5 (E7: Auditor de Consistencia)

Actúa como revisor de diseño. Te paso cinco diagramas UML en PlantUML: [adjuntar diagramas]. Verifica estas reglas y responde en una tabla (regla, elemento, problema, corrección sugerida): C1 cada mensaje de secuencia es una operación de la clase receptora; C2 cada transición de estados corresponde a una operación de la clase; C3 multiplicidades coherentes con los criterios de aceptación; C4 paquetes sin ciclos; C5 nombres consistentes. No reescribas los diagramas; solo reporta hallazgos y cita la línea.