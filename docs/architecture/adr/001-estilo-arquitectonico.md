# ADR-001: Adoptar un monolito modular como estilo arquitectónico

- Estado: Aceptado
- Fecha: 2026-10-04
- Decisores: Mathias Dario Davila Flores, Deivick Paul Eddi Chavez Cuno

## Contexto

RutaSIT Arequipa debe recibir las posiciones enviadas por los dispositivos GPS de los buses (RF-01), permitir al pasajero consultar la ubicación de los buses en el mapa (RF-02) y calcular el tiempo estimado de llegada a los paraderos (RF-03). Para cumplir estos requisitos, el sistema debe procesar las posiciones de 300 buses enviadas cada 10 segundos y actualizar el ETA en un máximo de 15 segundos (QA-01).

Además, el MVP debe estar en producción en 1 mes (R-01), será desarrollado por un equipo de 2 integrantes con conocimientos en Python, Java, MySQL y Git/GitHub (R-02), y dispone de un presupuesto bajo (R-03).

La arquitectura debe equilibrar el rendimiento requerido con la simplicidad de desarrollo y operación. También debe mantener una separación clara de responsabilidades entre ubicaciones, rutas y buses, cálculo de ETA, alertas y consultas, sin introducir una complejidad de infraestructura difícil de asumir durante el desarrollo del MVP.

## Alternativas consideradas

1. **Monolito modular:** una única aplicación desplegable organizada en módulos internos con responsabilidades claramente separadas.

2. **Arquitectura orientada a eventos:** procesamiento desacoplado de las actualizaciones GPS mediante eventos y componentes consumidores.

3. **Microservicios:** división del sistema en servicios independientes que pueden desplegarse y escalarse por separado.

## Decisión

Usaremos un **monolito modular** como estilo arquitectónico para el MVP de RutaSIT Arequipa. La aplicación se desplegará como una sola unidad y estará dividida internamente en módulos para ubicaciones, rutas y buses, cálculo de ETA, alertas y consultas.

La decisión se basa en la matriz de evaluación arquitectónica, donde el monolito modular obtuvo **4.25/5**, frente a **4.00/5** de la arquitectura orientada a eventos y **3.45/5** de microservicios.

## Consecuencias

- Positivas:
  - Reduce la complejidad de desarrollo, despliegue y operación para un equipo de 2 integrantes.
  - Facilita alcanzar el MVP dentro del plazo de 1 mes y con un presupuesto limitado.
  - Mantiene responsabilidades separadas mediante módulos internos.
  - Permite evolucionar posteriormente determinados módulos si las mediciones reales de carga justifican su desacoplamiento.

- Negativas:
  - Los módulos no pueden desplegarse y escalarse de forma independiente.
  - Un fallo grave en la aplicación puede afectar a varias funcionalidades del sistema.
  - Si la carga crece considerablemente, podría ser necesario desacoplar algunos módulos o incorporar mecanismos asíncronos.