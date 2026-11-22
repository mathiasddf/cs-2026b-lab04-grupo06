# Notas de trabajo del agente

- ISSUE-03 | Archivos revisados: issues/ISSUE-03.md, src/consultas/proveedores_gps.py (L91-L104). Hipótesis: normalizar_trama_gps indexa trama['lat'], trama['lon'] y trama['velocidad'] sin validar que trama sea un dict no vacío ni que las claves obligatorias existan y sean numéricas no nulas. Plan: agregar validación y lanzar DatosGPSIncompletosError, usando defaults antiguedad_seg=0 y en_corredor=True cuando sean None o ausentes.
