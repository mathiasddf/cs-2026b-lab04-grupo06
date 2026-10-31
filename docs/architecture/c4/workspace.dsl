workspace "RutaSIT Arequipa 2.0" "Arquitectura guiada por atributos de calidad (Lab 08 - ADD 3.0, ATAM-lite y Fitness Functions)" {
    model {
        pasajero = person "Pasajero del SIT" "Ciudadano de Arequipa que consulta en tiempo real el ETA y desvíos de su bus."
        operadorSit = person "Operador Municipal SIT" "Supervisa la flota de 1200 buses y configura desvíos viales sin desplegar código."

        sdkConecta = softwareSystem "SDK GPS ConectaAQP" "Proveedor externo de telemetría GPS de la concesionaria A (JSON km/h)." "External"
        sdkTransCayma = softwareSystem "SDK GPS TransCayma" "Proveedor externo de telemetría GPS de la concesionaria B (HTTP tuple m/s)." "External"
        proveedorLlm = softwareSystem "Proveedor LLM (Claude / Local)" "Modelo de lenguaje externo para explicar motivos de retraso." "External"

        rutasit = softwareSystem "RutaSIT Arequipa 2.0 (Multiconcesionaria)" "Sistema de seguimiento de 1200 buses, cálculo de ETA para 50 000 consultas/h y alertas en tiempo real." {

            pwaPasajero = container "PWA Pasajero Offline-First" "React + Service Worker + IndexedDB" "Muestra último mapa y ETA sin señal en <= 200 ms y reconecta por SSE [QA-03]." "Web Browser"
            panelOperador = container "Panel Operador SIT" "Web SPA" "Monitorea anomalías y actualiza trazados/desvíos GTFS en <= 2 h sin desplegar código [QA-06]." "Web Browser"

            apiMonolito = container "API Monolito Modular" "Python 3.12 / FastAPI + JWT + SSE" "Orquesta Consultas, Ubicaciones, Rutas, ETA y Alertas. Valida claim concesionaria_id en JWT [QA-01, QA-02, QA-04]." {
                compConsultas = component "ServicioConsultas" "Python Class" "Flujo crítico consultar_eta y explicar_retraso [QA-01, QA-04]."
                compResiliencia = component "ConCircuitBreakerGPS" "Decorator (Lab 07/08)" "Abre el circuito tras 3 timeouts y sirve última posición válida desde PostgreSQL [QA-02]."
                compAdaptadoresGps = component "Adaptadores ProveedorGPS" "Adapter + Factory (Lab 07)" "Traduce SDKs de concesionarias sin tocar el dominio [QA-07]."
                compEstrategiasEta = component "Estrategias de ETA" "Strategy + Factory (Lab 07)" "Calcula ETA en flujo libre, hora punta o lluvia [QA-01]."
                compEstadosViaje = component "Máquina de Estados Viaje" "State (Lab 07)" "Gestiona PROGRAMADO, EN_RUTA, DESVIADO, DETENIDO y FINALIZADO."
                compEventos = component "PublicadorEventos" "Observer (Lab 07)" "Despacha eventos hacia SSE de paraderos y alertas push."
                compExplicadorIa = component "ExplicadorRetrasosIA" "Strategy + Cache + Guardrails (Lab 07)" "Aísla el LLM y bloquea tiempos inventados."
            }

            cacheRedis = container "Caché en Memoria" "Redis 7" "Cachea ETA por (paradero, ruta) con TTL de 10 s para soportar 50 000 consultas/h [QA-01]." "Database"
            baseDatos = container "Base de Datos Geoespacial" "PostgreSQL 16 + PostGIS + RLS" "Índices compuestos [QA-01], tabla ultima_posicion_bus [QA-02], políticas RLS por concesionaria [QA-04] y geometrías GTFS [QA-06]." "Database"
        }

        # Relaciones a nivel de Contenedores con trazabilidad a escenarios [QA-xx]
        pasajero -> pwaPasajero "Consulta ETA y recibe alertas en paraderos [HTTPS]"
        operadorSit -> panelOperador "Configura desvíos viales y audita flota [HTTPS]"
        pwaPasajero -> apiMonolito "Consulta ETA y mantiene stream SSE con Last-Event-ID [HTTPS/SSE] [QA-01, QA-03]"
        panelOperador -> apiMonolito "Actualiza geometrías GTFS y consulta panel con JWT [HTTPS/JSON] [QA-04, QA-06]"

        apiMonolito -> cacheRedis "Lee y escribe ETA cacheado con TTL 10 s [RESP] [QA-01]"
        apiMonolito -> baseDatos "Lee con índice geoespacial, aplica RLS y guarda última posición conocida [SQL] [QA-01, QA-02, QA-04, QA-06]"
        apiMonolito -> sdkConecta "Consulta telemetría con reintentos y circuit breaker [HTTPS] [QA-02, QA-07]"
        apiMonolito -> sdkTransCayma "Consulta telemetría con reintentos y circuit breaker [HTTPS] [QA-02, QA-07]"
        apiMonolito -> proveedorLlm "Solicita explicación de retraso validada por guardrails [HTTPS]"

        # Relaciones internas de Componentes
        compConsultas -> compResiliencia "Obtiene lectura GPS resiliente [QA-02]"
        compResiliencia -> compAdaptadoresGps "Envuelve adaptadores con circuit breaker [QA-02]"
        compResiliencia -> baseDatos "Lee/actualiza tabla ultima_posicion_bus en caída [QA-02]"
        compAdaptadoresGps -> sdkConecta "Adapta dict km/h [QA-07]"
        compAdaptadoresGps -> sdkTransCayma "Adapta tupla m/s [QA-07]"
        compConsultas -> compEstrategiasEta "Calcula minutos de llegada [QA-01]"
        compConsultas -> compEstadosViaje "Actualiza estado del viaje"
        compConsultas -> compEventos "Publica eventos de ruta"
        compConsultas -> compExplicadorIa "Delega explicación con caché y guardrails"
    }

    views {
        systemContext rutasit "Contexto" {
            include *
            autoLayout lr
        }

        container rutasit "Contenedores" {
            include *
            autoLayout lr
        }

        component apiMonolito "Componentes" {
            include *
            autoLayout tb
        }

        styles {
            element "Person" {
                shape Person
                background #08427B
                color #ffffff
            }
            element "Software System" {
                background #1168BD
                color #ffffff
            }
            element "External" {
                background #999999
                color #ffffff
            }
            element "Container" {
                background #438DD5
                color #ffffff
            }
            element "Database" {
                shape Cylinder
                background #2E6DA4
                color #ffffff
            }
            element "Component" {
                background #85BBF0
                color #000000
            }
        }
    }
}