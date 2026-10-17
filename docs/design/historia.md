# Historia de Usuario - RutaSIT Arequipa

## HU-03: Consultar el tiempo estimado de llegada (ETA) del bus

**Como** pasajero del Sistema Integrado de Transporte (SIT)  
**Quiero** consultar la ubicación en tiempo real de los buses y su tiempo estimado de llegada (ETA) a mi paradero  
**Para** planificar mi viaje y reducir el tiempo de espera en la estación.

---

### Criterios de Aceptación

#### Criterio 1: Actualización exitosa de ETA con posición GPS válida
* **Dado** que un bus con GPS activo envía su nueva posición (`latitud`, `longitud`, `velocidad`) al sistema,  
* **Cuando** el pasajero consulta la ruta desde la aplicación PWA,  
* **Entonces** el sistema recalculará el tiempo estimado de llegada (ETA) al paradero seleccionado en menos de 15 segundos y mostrará la ubicación actualizada del bus en el mapa.

#### Criterio 2: Manejo de pérdida de señal o señal obsoleta
* **Dado** que un bus deja de transmitir su posición GPS por más de 60 segundos,  
* **Cuando** el pasajero consulte el ETA de esa unidad o paradero,  
* **Entonces** el sistema marcará el viaje en estado `DESVIADO` o `DETENIDO`, mostrando una advertencia de "Información no actualizada / Señal GPS débil" sin interrumpir la consulta de otras unidades.