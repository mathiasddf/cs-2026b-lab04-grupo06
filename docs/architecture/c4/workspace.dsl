workspace "RutaSIT Arequipa" "Modelo C4 del sistema de seguimiento en tiempo real de buses del SIT Arequipa" {

    !identifiers hierarchical

    model {
        pasajero = person "Pasajero" "Ciudadano de Arequipa que consulta la ubicación de los buses, el ETA a su paradero y recibe alertas."
        operador = person "Operador" "Personal del SIT que supervisa la flota en ruta y monitorea alertas de desvío o congestión."

        gpsBuses = softwareSystem "Dispositivos GPS de Buses" "Hardware embarcado en los 300 buses que transmite coordenadas y velocidad cada 10 segundos." "Externo"
        mapas = softwareSystem "Servicio Externo de Mapas" "Proveedor cartográfico externo (OpenStreetMap / API de rutas) para visualización y matrices de distancia." "Externo"

        rutasit = softwareSystem "RutaSIT Arequipa" "Permite el seguimiento de buses en tiempo real, cálculo de tiempos estimados de llegada (ETA) y gestión de alertas de desvío o congestión." {
            pwa = container "Aplicación de Pasajeros (PWA)" "Interfaz web progresiva para que el pasajero visualice el mapa, consulte paraderos y reciba alertas." "HTML5 / JS / SSE Client" "Web Browser"
            panel = container "Panel de Operaciones" "Aplicación web para el monitoreo de la flota, supervisión de rutas y gestión de alertas." "HTML5 / JavaScript" "Web Browser"
            api = container "API RutaSIT" "Monolito modular que recibe la telemetría GPS, calcula el ETA, detecta anomalías y sirve consultas." "Python 3.12 / FastAPI" {
                consultas = component "Módulo de Consultas" "Orquesta las peticiones de ubicación y ETA de pasajeros y operadores, y emite eventos SSE." "Paquete Python (consultas)"
                ubicaciones = component "Módulo de Ubicaciones" "Recibe, valida y procesa las posiciones GPS enviadas por los 300 buses cada 10 segundos." "Paquete Python (ubicaciones)"
                rutasBuses = component "Módulo de Rutas y Buses" "Gestiona el catálogo de rutas, paraderos, unidades de transporte y el ciclo de vida del Viaje." "Paquete Python (rutas_buses)"
                calculoEta = component "Módulo de Cálculo de ETA" "Calcula y ajusta el tiempo estimado de llegada por segmento de ruta en menos de 15 segundos." "Paquete Python (calculo_eta)"
                alertas = component "Módulo de Alertas" "Detecta desvíos de ruta o detenciones prolongadas (>60s) y genera avisos operativos." "Paquete Python (alertas)"
            }
            db = container "Base de Datos" "Almacena rutas, paraderos, flota de buses, viajes activos, historial reciente de posiciones GPS y alertas." "MySQL 8.0" "Database"
        }

        # Relaciones de Contexto (Nivel 1)
        pasajero -> rutasit "Consulta ubicación de buses, ETA por paradero y recibe alertas de desvío"
        operador -> rutasit "Supervisa el estado de la flota y consulta desvíos o congestión"
        gpsBuses -> rutasit "Envía posición geográfica y velocidad cada 10 segundos" "HTTP/REST (JSON)"
        rutasit -> mapas "Consulta cartografía y matrices de distancia entre coordenadas y paraderos" "HTTPS/JSON"

        # Relaciones de Contenedores (Nivel 2)
        pasajero -> rutasit.pwa "Consulta mapa, paraderos y ETA en" "HTTPS"
        operador -> rutasit.panel "Monitorea unidades e incidentes en" "HTTPS"
        rutasit.pwa -> rutasit.api "Solicita ETA y recibe actualizaciones en tiempo real de" "HTTPS/JSON y SSE"
        rutasit.panel -> rutasit.api "Consulta estado de flota y alertas en" "HTTPS/JSON (REST)"
        gpsBuses -> rutasit.api "Envía telemetría de posición periódica a" "HTTP/REST (JSON)"
        rutasit.api -> rutasit.db "Lee y escribe viajes, posiciones, rutas y alertas en" "SQL/TCP"
        rutasit.api -> mapas "Obtiene distancias en ruta desde" "HTTPS/JSON"
        rutasit.pwa -> mapas "Renderiza teselas de mapa desde" "HTTPS"

        # Relaciones de Componentes (Nivel 3 - Sin ciclos, coherente con Lab 04 y Lab 05)
        gpsBuses -> rutasit.api.ubicaciones "Envía lote de coordenadas GPS a" "HTTP/REST (JSON)"
        rutasit.pwa -> rutasit.api.consultas "Solicita ETA y abre canal de eventos en" "HTTPS/JSON y SSE"
        rutasit.panel -> rutasit.api.consultas "Consulta estado de viajes y alertas en" "HTTPS/JSON"

        rutasit.api.consultas -> rutasit.api.calculoEta "Solicita cálculo de tiempo estimado a"
        rutasit.api.consultas -> rutasit.api.alertas "Consulta anomalías activas o dispara avisos en"
        rutasit.api.consultas -> rutasit.api.rutasBuses "Busca viaje activo y paraderos en"

        rutasit.api.calculoEta -> rutasit.api.ubicaciones "Obtiene última posición válida de"
        rutasit.api.calculoEta -> rutasit.api.rutasBuses "Obtiene trazado y paraderos de la ruta de"

        rutasit.api.alertas -> rutasit.api.ubicaciones "Verifica tiempo sin señal y coordenadas en"
        rutasit.api.alertas -> rutasit.api.rutasBuses "Compara posición con el corredor permitido de"

        rutasit.api.ubicaciones -> rutasit.db "Registra posición GPS y actualiza estado en" "SQL/TCP"
        rutasit.api.rutasBuses -> rutasit.db "Lee y actualiza viajes, buses y paraderos en" "SQL/TCP"
        rutasit.api.calculoEta -> rutasit.db "Persiste ETA actualizado en" "SQL/TCP"
        rutasit.api.alertas -> rutasit.db "Registra alertas de desvío o detención en" "SQL/TCP"
        rutasit.api.consultas -> rutasit.db "Lee proyecciones de consulta en" "SQL/TCP"

        rutasit.api.calculoEta -> mapas "Calcula distancia mediante puerto IServicioMapas en" "HTTPS/JSON"

        # Entorno de Despliegue (Nivel Despliegue - E5)
        produccion = deploymentEnvironment "Producción" {
            deploymentNode "Smartphone / PC del Pasajero" "" "Android / iOS / Navegador Web" {
                containerInstance rutasit.pwa
            }
            deploymentNode "PC de Centro de Control SIT" "" "Windows / Linux - Navegador Web" {
                containerInstance rutasit.panel
            }
            deploymentNode "Servidor VPS RutaSIT" "" "Ubuntu 24.04 LTS (2 vCPU, 4 GB RAM - Bajo costo)" {
                deploymentNode "Proxy Inverso" "" "Nginx" {
                    # Recibe tráfico HTTPS/SSE y redirige al contenedor de la API
                }
                deploymentNode "Entorno de Ejecución Docker" "" "Docker Engine + Docker Compose" {
                    containerInstance rutasit.api
                    containerInstance rutasit.db
                }
            }
        }
    }

    views {
        systemContext rutasit "Contexto" "Nivel 1: Diagrama de contexto del sistema RutaSIT Arequipa." {
            include *
            autolayout lr
        }

        container rutasit "Contenedores" "Nivel 2: Diagrama de contenedores de RutaSIT Arequipa." {
            include *
            autolayout lr
        }

        component rutasit.api "Componentes" "Nivel 3: Diagrama de componentes del monolito modular API RutaSIT." {
            include *
            autolayout tb
        }

        dynamic rutasit.api "ConsultarETA" "Vista dinámica: Flujo crítico de consulta de ETA por paradero (HU-03)." {
            rutasit.pwa -> rutasit.api.consultas "1. Solicita ETA (GET /eta?busId&paraderoId)"
            rutasit.api.consultas -> rutasit.api.rutasBuses "2. Busca viaje activo del bus"
            rutasit.api.rutasBuses -> rutasit.db "3. Lee datos del viaje y ruta asignada"
            rutasit.api.consultas -> rutasit.api.calculoEta "4. Solicita calcular ETA hacia el paradero"
            rutasit.api.calculoEta -> rutasit.api.ubicaciones "5. Obtiene última posición GPS registrada"
            rutasit.api.calculoEta -> mapas "6. Consulta matriz de distancia por segmentos pendientes"
            rutasit.api.consultas -> rutasit.api.alertas "7. Verifica si el viaje presenta desvío o detención para adjuntar alerta"
            autolayout lr
        }

        deployment rutasit produccion "Despliegue" "Vista de despliegue en el entorno de Producción (MVP de bajo presupuesto)." {
            include *
            autolayout lr
        }

        styles {
            element "Person" {
                shape person
                background #08427B
                color #ffffff
            }
            element "Software System" {
                background #1168BD
                color #ffffff
            }
            element "Externo" {
                background #999999
                color #ffffff
            }
            element "Container" {
                background #438DD5
                color #ffffff
            }
            element "Component" {
                background #85BBF0
                color #000000
            }
            element "Database" {
                shape cylinder
            }
            element "Web Browser" {
                shape WebBrowser
            }
        }
    }
}