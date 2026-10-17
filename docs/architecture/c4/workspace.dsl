workspace "RutaSIT Arequipa" "Modelo C4 del sistema de seguimiento en tiempo real de buses del SIT Arequipa" {

    !identifiers hierarchical

    model {
        pasajero = person "Pasajero" "Ciudadano de Arequipa que consulta la ubicación de los buses, el ETA a su paradero y recibe alertas."
        operador = person "Operador" "Personal del SIT que supervisa la flota en ruta y monitorea alertas de desvío o congestión."

        gpsBuses = softwareSystem "Dispositivos GPS de Buses" "Hardware embarcado en los 300 buses que transmite coordenadas y velocidad cada 10 segundos." "Externo"
        mapas = softwareSystem "Servicio Externo de Mapas" "Proveedor cartográfico externo (OpenStreetMap / API de rutas) para visualización y matrices de distancia." "Externo"

        rutasit = softwareSystem "RutaSIT Arequipa" "Permite el seguimiento de buses en tiempo real, cálculo de tiempos estimados de llegada (ETA) y gestión de alertas de desvío o congestión."

        # Relaciones de Contexto (Nivel 1)
        pasajero -> rutasit "Consulta ubicación de buses, ETA por paradero y recibe alertas de desvío"
        operador -> rutasit "Supervisa el estado de la flota y consulta desvíos o congestión"
        gpsBuses -> rutasit "Envía posición geográfica y velocidad cada 10 segundos" "HTTP/REST (JSON)"
        rutasit -> mapas "Consulta cartografía y matrices de distancia entre coordenadas y paraderos" "HTTPS/JSON"
    }

    views {
        systemContext rutasit "Contexto" "Nivel 1: Diagrama de contexto del sistema RutaSIT Arequipa." {
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
        }
    }
}