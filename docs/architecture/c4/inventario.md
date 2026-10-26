# Inventario de Elementos C4 - RutaSIT Arequipa

| Elemento | Tipo C4 | Origen |
|---|---|---|
| Pasajero, Operador | Persona | `docs/architecture/drivers.md` (Lab 04) |
| RutaSIT Arequipa | Sistema de software | Caso de estudio (`README.md`, Lab 04) |
| Dispositivos GPS de Buses, Servicio Externo de Mapas | Sistema externo | `docs/architecture/drivers.md`, `ADR-002` y `arquitectura.mmd` (Lab 04) |
| Aplicación de Pasajeros (PWA), Panel de Operaciones, API RutaSIT (Monolito Modular), Base de Datos | Contenedor | `ADR-001`, `ADR-002`, `ADR-003` y `despliegue.py` (Lab 04) |
| Módulo de Consultas, Módulo de Ubicaciones, Módulo de Rutas y Buses, Módulo de Cálculo de ETA, Módulo de Alertas | Componente (de la API) | `arquitectura.mmd` (Lab 04) y `paquetes.puml` (Lab 05) |
| Flujo "Consultar tiempo estimado de llegada (ETA)" | Vista dinámica | `secuencia-consultar-eta.puml` (Lab 05) |