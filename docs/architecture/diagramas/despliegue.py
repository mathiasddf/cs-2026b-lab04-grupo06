from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.client import Users
from diagrams.onprem.compute import Server
from diagrams.onprem.database import MySQL
from diagrams.onprem.network import Nginx
from diagrams.onprem.monitoring import Prometheus
from diagrams.generic.device import Mobile
from diagrams.generic.compute import Rack
from diagrams.generic.network import Router


with Diagram(
    "RutaSIT Arequipa - Vista de despliegue",
    filename="docs/architecture/diagramas/img/despliegue",
    show=False,
    direction="LR"
):
    # Usuarios y dispositivos
    pasajeros = Mobile("Pasajeros")
    operador = Users("Operador")
    gps = Rack("Buses / GPS")

    internet = Router("Internet")

    # Infraestructura principal
    with Cluster("Servidor RutaSIT"):
        proxy = Nginx("Proxy / Nginx")
        app = Server("Aplicacion RutaSIT")
        db = MySQL("Base de datos")
        monitor = Prometheus("Monitoreo")

        proxy >> Edge(label="HTTP interno") >> app
        app >> Edge(label="SQL") >> db
        monitor << Edge(label="metricas") << app

    # Servicio externo
    mapas = Server("Servicio externo\nde mapas")

    # Conexiones externas
    pasajeros >> Edge(label="HTTPS / SSE") >> internet
    operador >> Edge(label="HTTPS") >> internet
    gps >> Edge(label="HTTP / REST") >> internet

    internet >> Edge(label="HTTPS") >> proxy

    app >> Edge(label="API HTTPS") >> mapas