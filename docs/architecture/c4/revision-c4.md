# Revisión de Diagramas con Lista Oficial C4 e IA - RutaSIT Arequipa

## 1. Evaluación con la lista de revisión oficial (c4model.com)

| Vista | Grupo | Pregunta de revisión | ¿Cumple? | Evidencia en el modelo |
|---|---|---|---|---|
| **Todas (5 vistas)** | General | ¿Tiene título, alcance claro y leyenda? | **Sí** | Todas las vistas exportadas desde `workspace.dsl` incluyen título, descripción de nivel/alcance y bloque `Legend` automático. |
| **1. Contexto** | Elementos | ¿Cada elemento tiene nombre, tipo y descripción sin mostrar tecnologías internas? | **Sí** | `Pasajero` y `Operador` figuran como `Person`; `RutaSIT Arequipa` como `Software System` y `Dispositivos GPS` / `Servicio Externo de Mapas` como sistemas externos sin exponer Python ni MySQL. |
| **1. Contexto** | Relaciones | ¿Cada flecha tiene un verbo que describe la intención? | **Sí** | Se usan frases activas: *"Consulta ubicación de buses, ETA por paradero..."*, *"Supervisa el estado de la flota..."*, *"Envía posición geográfica..."*. |
| **2. Contenedores** | Elementos | ¿Todos los contenedores indican su tecnología concreta y descripción? | **Sí** | Se especifican `HTML5 / JS / SSE Client`, `HTML5 / JavaScript`, `Python 3.12 / FastAPI` y `MySQL 8.0`. Ningún contenedor se llama "Docker" o "Servidor". |
| **2. Contenedores** | Relaciones | ¿Todas las flechas indican el protocolo de comunicación? | **Sí** | Se detallan `HTTPS`, `HTTPS/JSON y SSE`, `HTTPS/JSON (REST)`, `HTTP/REST (JSON)` y `SQL/TCP`, alineados con ADR-002 y ADR-003. |
| **3. Componentes** | Elementos | ¿Los componentes coinciden con los módulos del Lab 04/05 y no tienen ciclos? | **Sí** | Los 5 componentes (`Consultas`, `Ubicaciones`, `Rutas y Buses`, `Cálculo de ETA`, `Alertas`) coinciden con `paquetes.puml` y forman un grafo acíclico dirigido (DAG). |
| **4. Dinámica** | Relaciones | ¿Los pasos están numerados y corresponden a relaciones existentes en el modelo? | **Sí** | Contiene 7 pasos numerados para el flujo `ConsultarETA` y Structurizr validó que cada paso corresponde a una relación estática declarada en `model`. |
| **5. Despliegue** | Elementos | ¿Muestra nodos anidados con tecnología y contiene instancias de todos los contenedores? | **Sí** | Incluye `Smartphone / PC del Pasajero`, `PC de Centro de Control SIT` y `Servidor VPS RutaSIT` (`Ubuntu 24.04 LTS`, `Nginx`, `Docker Compose`) con `containerInstance` de los 4 contenedores. |

---

## 2. Hallazgos de la auditoría con IA (incluye detección de Falso Positivo)

| Vista | Hallazgo reportado por la IA | Verificación del equipo | Decisión |
|---|---|---|---|
| **Contexto** | *"Falta especificar el protocolo tecnológico (HTTPS) en las relaciones entre las personas (`Pasajero`, `Operador`) y el sistema `RutaSIT Arequipa`."* | **Falso positivo:** En el Nivel 1 (Contexto) el público incluye perfiles no técnicos y las personas interactúan con el sistema como caja negra; los protocolos de interfaz (`HTTPS`) corresponden recién al Nivel 2 (hacia la PWA y el Panel). | **Rechazada** (se mantiene sin protocolo en Nivel 1 según guía oficial C4). |
| **Contenedores** | *"La relación entre la PWA y la API incluye dos mecanismos (`HTTPS/JSON y SSE`). Se recomienda aclarar en la descripción que solicita datos y recibe eventos."* | **Correcto:** Aunque ambos viajan sobre HTTPS, cumplen intenciones complementarias (consulta REST y suscripción SSE según ADR-003). | **Aceptada** (se precisó la etiqueta *"Solicita ETA y recibe actualizaciones en tiempo real de"*). |
| **Componentes** | *"El módulo `Compartido` del diagrama de paquetes del Lab 05 no aparece como componente en la vista de Nivel 3."* | **Falso positivo parcial:** En C4, un componente representa una agrupación funcional con interfaz de negocio; las enumeraciones o utilidades transversales (`EstadoBus`) son detalles de código (Nivel 4) que no deben ensuciar el diagrama de componentes. | **Rechazada** (se conservan los 5 componentes funcionales de negocio). |
| **Despliegue** | *"El nodo `Proxy Inverso (Nginx)` no contiene un `containerInstance` dentro del bloque."* | **Correcto:** Nginx es parte de la infraestructura del servidor VPS (representado en `despliegue.py` del Lab 04), no un contenedor de software de aplicación desarrollado por el equipo. | **Documentada** (se mantiene como `deploymentNode` de infraestructura dentro del VPS). |