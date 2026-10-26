# Bitácora de Interacciones con Inteligencia Artificial (E7)

## Resumen de Interacciones

| # | Fecha | Herramienta | Prompt (resumen) | Propuesta de la IA | Verificación / Corrección | Decisión |
|---|-------|-------------|------------------|---------------------|---------------------------|----------|
| 1 | 24/10/2026 | Gemini | Diseñar el patrón State para sustituir condicionales de `estado` en `Viaje`. | Creo jerarquía de clases `EstadoViajeBase` y subclases concretas. | Se verificó compilación y transiciones de estado básicas. | Aceptado |
| 2 | 24/10/2026 | Gemini | Implementar patrón Decorator para cachear respuestas del cliente LLM. | Propuso la clase `ConCacheLLM` envolviendo la llamada al cliente. | **Corrección por pruebas:** La prueba unitaria falló porque el caché no consideraba el parámetro del proveedor. Se corrigió la clave de caché. | Corregido y Aceptado |
| 3 | 24/10/2026 | Gemini | Diseñar la cadena de guardrails de calidad (Chain of Responsibility) para IA. | Creó eslabones `GuardrailLongitud` y `GuardrailAfirmaciones`. | Se validó que lanzara `ValueError` ante textos deshonestos o de >180 caracteres. | Aceptado |
| 4 | 24/10/2026 | Gemini | Implementar patrón Observer para publicar eventos de viaje anómalo o en ruta. | Creo `PublicadorEventos` y suscriptores (`NotificadorPushPasajero`, etc.). | Se verificó que permitiera suscribir nuevos auditores sin modificar `ServicioConsultas`. | Aceptado |
| 5 | 24/10/2026 | Gemini | Generar diagramas PlantUML para cada patrón aplicado con sus estereotipos. | Generó los diagramas `.puml` para Strategy, State y el componente de IA. | Se añadieron los estereotipos GoF (`<<Strategy>>`, `<<Adapter>>`, etc.) requeridos por la guía. | Aceptado |

---

## Detalle de Interacciones Clave

### Interacción 2 (Corrección detectada por pruebas unitarias)
* **Prompt:** "Implementa un decorador `ConCacheLLM` para evitar llamadas duplicadas a la API del LLM si el viaje y los eventos no han cambiado."
* **Propuesta inicial de la IA:** La IA implementó un diccionario usando solo `prompt` como clave.
* **Fallo detectado:** En `test_decorator_cache_llm_evita_llamadas_repetidas`, al cambiar de proveedor pero mantener el prompt, se retornaba la respuesta cacheada del proveedor anterior.
* **Ajuste realizado:** Se modificó la generación de la clave de caché para incluir la tupla `(proveedor, prompt)`, resolviendo la prueba unitaria.