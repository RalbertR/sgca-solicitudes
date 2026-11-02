# SGCA · Módulo de solicitudes de certificados

Prototipo de consola del módulo de solicitudes del SGCA, el Sistema de Gestión de Certificados Académicos. Un estudiante pide un certificado de alumno regular o un analítico parcial, el sistema revisa si tiene deuda administrativa y la solicitud sigue su recorrido hasta que se emite o se rechaza.

## Cómo se usa

Hace falta Python 3.12 o superior. El sistema no usa librerías externas.

```bash
python main.py
```

Los datos de ejemplo están en `datos.json` y son todos inventados. Los certificados emitidos se guardan en la carpeta `certificados/`.

## Funcionalidades

1. Registrar una solicitud. Si el estudiante tiene deuda queda rechazada y pasa a Tesorería.
2. Cambiar el estado de una solicitud. Al emitirla se genera el certificado y se avisa por correo.
3. Asignar un responsable del área que corresponde.
4. Buscar solicitudes por estado, tipo, prioridad y legajo.
5. Ver un reporte con la cantidad de solicitudes por estado, tipo y prioridad.
