# Matriz de Olores de Código Identificados (E1) - Módulo Consultas

| Olor Detectado | Complejidad Radon | Patrón GoF Propuesto | Principio SOLID | Decisión del Equipo | Justificación |
| :--- | :---: | :--- | :--- | :---: | :--- |
| Condicionales para bifurcar la lectura según el proveedor GPS (`GPS_SIT` vs `GPS_MUNICIPAL`) | B (8) | Strategy + Adapter | Open/Closed (OCP) | **Aceptado** | Permite incorporar nuevos proveedores GPS extendiendo adaptadores sin modificar el servicio de consultas. |
| Condicionales anidados sobre el atributo `estado_bus` (`CANCELADO`, `FINALIZADO`, etc.) | B (8) | State | Single Responsibility (SRP) | **Aceptado** | Encapsula el comportamiento y las reglas de transición del viaje en clases independientes. |
| Registro manual de alertas/eventos en listas internas | N/A | Observer | Single Responsibility (SRP) | **Aceptado** | Desacopla la lógica central de desvíos respecto a las notificaciones o publicaciones. |
| "Implementar el servicio de consultas o fábrica de GPS como Singleton" | N/A | Singleton | N/A | **Rechazado** | **Rechazado:** Introduce un punto único de falla y estado global oculto, dificultando la inyección de dependencias y las pruebas aisladas en pytest. |