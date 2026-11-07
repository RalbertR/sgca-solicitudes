# SGCA · Módulo de solicitudes de certificados

Prototipo de consola del módulo de solicitudes del SGCA, el Sistema de Gestión de Certificados Académicos. Un estudiante pide un certificado de alumno regular o un analítico parcial, el sistema revisa si tiene deuda administrativa y la solicitud sigue su recorrido hasta que se emite o se rechaza.

Es el trabajo integrador de Metodología de Sistemas II. Partimos de una versión que funcionaba pero tenía todo en una sola clase, y la refactorizamos en pull requests revisados entre los dos sin cambiar lo que hace el sistema.

## Requisitos

Hace falta Python 3.12 o superior. El sistema no usa librerías externas. Las pruebas, el linter y las métricas necesitan los paquetes de `requirements-dev.txt`.

## Instalación

```bash
python -m venv .venv
```

En Windows el entorno se activa con `.venv\Scripts\activate` y en Linux o macOS con `source .venv/bin/activate`. Después se instalan los paquetes de desarrollo.

```bash
pip install -r requirements-dev.txt
```

## Uso

```bash
python main.py
```

Los datos de ejemplo están en `datos.json` y son todos inventados. Los certificados emitidos se guardan en la carpeta `certificados/`. El aviso por correo es simulado y solo se muestra en la consola.

## Funcionalidades

1. Registrar una solicitud. Si el estudiante tiene deuda queda rechazada y pasa a Tesorería.
2. Cambiar el estado de una solicitud. Al emitirla se genera el certificado y se avisa por correo.
3. Asignar un responsable del área que corresponde.
4. Buscar solicitudes por estado, tipo, prioridad y legajo.
5. Ver un reporte con la cantidad de solicitudes por estado, tipo y prioridad.

## Tecnologías

- Python con la biblioteca estándar.
- pytest para las pruebas.
- ruff como linter.
- radon para medir complejidad y mantenibilidad.
- GitHub Actions, que corre `ruff check .` y `pytest` en cada push y en cada pull request.

## Pruebas y linter

```bash
pytest
ruff check .
```

`tests/test_caracterizacion.py` tiene 24 pruebas de caja negra que corren `main.py` con un guion de entradas y comparan la consola, el JSON y los certificados. Las escribimos antes de refactorizar y no cambiaron en ningún PR. Las otras 32 son unitarias y prueban cada pieza por separado.

Las métricas salen de `radon cc -s -a main.py sgca` y `radon mi -s main.py sgca`. Las salidas de antes y después están en `docs/evidencias/`.

## Estructura

```text
main.py               arma el servicio y arranca la consola
sgca/cli.py           menú, entrada y salida por consola
sgca/servicio.py      reglas de las solicitudes
sgca/modelos.py       entidades, enums y transiciones de estado
sgca/repositorio.py   interfaz del repositorio y acceso a datos.json
sgca/certificados.py  un generador de texto por tipo de certificado
sgca/errores.py       ErrorSolicitud
tests/                pruebas de caracterización y unitarias
docs/                 diagnóstico, checklist, decisiones y evidencias
```

## Tags

| Tag | Qué marca |
|---|---|
| `estado-inicial` | La versión inicial, con todo en `sistema_solicitudes.py` |
| `etapa-diagnostico` | Pruebas de caracterización, diagnóstico de smells, evidencias iniciales y CI |
| `etapa-refactoring` | El cierre de los seis PR de refactoring |
| `etapa-pruebas` | Evidencias de pruebas y métricas antes y después |
| `etapa-docs` | Este README, las decisiones técnicas y el diagnóstico con el PR que resolvió cada smell |
| `estado-refactorizado` | La versión final |

## Integrantes

Raúl Robino, RalbertR en GitHub, y Mariano Rodríguez Arce, Mariano-RA en GitHub. Cada PR lo revisó el otro integrante con el checklist de `docs/checklist-code-review.md`.

| PR | Autor | Cambio |
|---|---|---|
| #1 | Mariano Rodríguez Arce | Checklist de code review |
| #2 | Raúl Robino | Extract Method en `registrar_solicitud` y `cambiar_estado` |
| #3 | Mariano Rodríguez Arce | Enums para estado, tipo y prioridad, y tabla de transiciones |
| #4 | Raúl Robino | Promedio en `Estudiante` y persistencia en `RepositorioJson` |
| #5 | Mariano Rodríguez Arce | `NuevaSolicitud`, `FiltroSolicitudes` y errores con excepciones |
| #6 | Raúl Robino | Consola en `cli.py` y lógica en `ServicioSolicitudes` |
| #7 | Mariano Rodríguez Arce | Un generador de certificado por tipo |
