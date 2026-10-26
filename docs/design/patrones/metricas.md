# Métricas de Refactorización (`radon`) y Análisis de Trade-off — RutaSIT Arequipa (E6)

## 1. Comandos ejecutados para la medición

```bash
radon cc -s -a src/consultas/antes/servicio.py
radon cc -s -a src/consultas/servicio.py src/consultas/proveedores_gps.py src/consultas/estrategias_eta.py src/consultas/estados.py src/consultas/eventos.py src/consultas/ia.py
radon raw -s src/consultas/
radon mi -s src/consultas/
```

## 2. Tabla Comparativa de Complejidad Ciclomática (radon cc) y Tamaño (SLOC)

| Archivo / Método evaluado | Antes (antes/servicio.py) | Después (Con Patrones GoF) | Variación / Mejora |
| :--- | :--- | :--- | :--- |
| **ServicioConsultas.consultar_eta()** | 24 (Rango D — Complejidad muy alta) | 8 (Rango B) / 4 (Rango A con Factory ETA) | Reducción drástica (> 66% a 83% menos caminos) |
| **ServicioConsultas.explicar_retraso()** | 8 (Rango B) | 1 (Rango A — Delegación pura a ExplicadorRetrasosIA) | -87.5% (Baja 7 puntos) |
| **ConReintentosGPS.obtener_lectura()** *(proveedores_gps.py)* | *(Mezclado y duplicado en consultar_eta)* | 3 (Rango A) | Aislado en un único Decorator |
| **EstadoViajeBase y subclases** *(estados.py)* | *(Mezclado en consultar_eta)* | 1 a 2 (Rango A) | Polimorfismo sin condicionales if/elif |
| **PublicadorEventos y suscriptores** *(eventos.py)* | *(Mezclado en consultar_eta)* | 1 a 2 (Rango A) | Desacoplado en 3 suscriptores |
| **ExplicadorRetrasosIA y Guardrail** *(ia.py)* | *(Mezclado en explicar_retraso)* | 1 a 4 (Rango A) | Validación en cadena determinista |
| **Complejidad Ciclomática Promedio** *(Average complexity)* | 8.67 (Rango B) | 1.68 (Rango A) | -80.6% de reducción en complejidad promedio |
| **Índice de Mantenibilidad** *(radon mi)* | 58.42 (Rango A) | 85.40 promedio (Rango A) | +26.98 puntos de mantenibilidad |
| **Líneas de código efectivas** *(SLOC - radon raw)* | 110 SLOC (en 1 archivo) | 338 SLOC (distribuidas en 6 archivos) | +228 SLOC (+5 archivos) por indirección |
| **Métodos a modificar en ServicioConsultas** ante un nuevo operador GPS, suscriptor o proveedor IA | 2 métodos (`__init__` y método principal) | 0 métodos (cumple Open/Closed) | Extensión sin modificación |

## 3. Análisis del Trade-off: ¿Qué ganamos, qué costó y cuándo bastaba la versión antes?

Con la refactorización hacia patrones GoF ganamos que el flujo crítico `consultar_eta()` redujera su complejidad ciclomática de 24 (rango D, difícil de mantener y probar) a un nivel simple (rango A/B <= 8), llevando el promedio del módulo de 8.67 (B) a 1.68 (A) y eliminando la duplicación de bucles try/except de reintentos. Además, logramos cumplimiento real del principio Abierto/Cerrado (OCP) e Inversión de Dependencias (DIP): ahora es posible registrar un nuevo operador GPS de Arequipa, añadir un suscriptor de auditoría o cambiar el proveedor de IA sin modificar `ServicioConsultas`, manteniendo la IA aislada, con caché y protegida por guardrails sin usar claves de API. 

A cambio, el costo asumido fue pasar de 110 SLOC en 1 solo archivo a 338 SLOC repartidas en 6 archivos, incrementando la cantidad de clases e indirección que el equipo debe navegar. Si RutaSIT Arequipa fuera un sistema estático con un único proveedor de GPS, una sola fórmula fija de velocidad, sin notificaciones diferenciadas y sin explicaciones generadas por IA, la versión `antes/servicio.py` habría sido suficiente y más directa para el MVP. Los patrones aplicados se justifican exclusivamente por los cambios previstos en el dominio del Sistema Integrado de Transporte.

## 4. Patrones que el Equipo Decidió NO Aplicar y Justificación

*   **Singleton** *(Rechazado para FabricaGPS / FabricaProveedoresGPS y PublicadorEventos)*:
    *   *Propuesta de la IA:* La IA sugirió implementar las fábricas de operadores GPS y el publicador de eventos como un Singleton para tener una instancia global accesible desde cualquier módulo.
    *   *Por qué se rechazó:* Introduce estado global oculto que acopla las pruebas unitarias entre sí dentro de `pytest` (un suscriptor o un operador falso registrado en un test contaminaría los siguientes tests) y dificulta inyectar dobles de prueba con fallas simuladas (`GpsConectaSDK(fallas=2)` o `MockClienteLLM`). En su lugar, aplicamos inyección de dependencias por constructor con valores por defecto.

*   **Abstract Factory** *(Rechazado frente a Factory de registro simple)*:
    *   *Propuesta de la IA:* Crear una jerarquía `FabricaOperadorAbstracta` donde cada empresa de buses (`ConectaFactory`, `TransCaymaFactory`) creara una familia acoplada de (`AdaptadorGPS`, `EstrategiaETA`, `Notificador`).
    *   *Por qué se rechazó:* Es un caso típico de "patternitis" (sobreingeniería), porque en RutaSIT Arequipa el algoritmo de cálculo de ETA (`FLUJO_LIBRE`, `HORA_PUNTA`, `CLIMA_LLUVIA`) depende de la hora y el clima de la ciudad, no de la empresa concesionaria del bus. Una fábrica de registro simple con diccionario resuelve la creación sin multiplicar clases innecesariamente.
