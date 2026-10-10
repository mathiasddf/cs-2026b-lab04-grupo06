# Revisión de Consistencia — RutaSIT Arequipa (E7)

Informe de validación cruzada y análisis de consistencia entre los diagramas del sistema aplicando las reglas C1 a C5 del auditor de diseño (Prompt IA 3).

## Tabla de Consistencia (`consistencia.md`)

| Regla | Hallazgo de la IA | Verificación del equipo |
|---|---|---|
| **C2** | La transición de cambio de estado en el diagrama de estados de Bus no corresponde a ninguna operación explícita de la clase. | **Correcto:** Se añade el método `actualizarEstado()` en la clase `Bus` para solventar la transición reportada. |
| **C1** | `ubicaciones.calcularEta()` se invoca desde el flujo de secuencia del pasajero, pero no existe una asociación directa explícita entre las clases involucradas. | **Falso positivo:** El componente accede al cálculo de ETA a través de la interfaz del puerto `IServicioMapas` y la navegación por módulos (asociación válida). |
| **C4** | El paquete `ubicaciones` presenta una supuesta dependencia directa hacia el paquete `eta`. | **Falso:** La IA leyó erróneamente la dirección de la traza de dependencias desde el paquete compartido. Se rechaza el hallazgo tras verificar el diagrama de paquetes. |
| **C3** | Las multiplicidades entre `Ruta` y `Paradero` no reflejan el orden secuencial de la iteración de paradas. | **Correcto:** Se especifican formalmente las cardinalidades `1` a `1..*` en el diagrama de clases para mayor claridad. |
| **C5** | Inconsistencia de nomenclatura entre el atributo `id_bus` y la referencia en los mensajes de actividad. | **Correcto:** Se unifica la nomenclatura estándar de los identificadores en todos los artefactos. |