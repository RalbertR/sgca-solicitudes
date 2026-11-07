from collections.abc import Callable

from sgca.modelos import Estudiante, Solicitud, TipoCertificado

ENCABEZADO = "SGCA - Sistema de Gestión de Certificados Académicos\n"

GeneradorCertificado = Callable[[Solicitud, Estudiante], str]


def certificado_alumno_regular(solicitud, estudiante):
    return (
        "CERTIFICADO DE ALUMNO REGULAR\n\n"
        f"Se certifica que {estudiante.nombre} {estudiante.apellido}, legajo {estudiante.legajo}, "
        f"es alumno/a regular de la carrera {estudiante.carrera}.\n\n"
    )


def certificado_analitico_parcial(solicitud, estudiante):
    return (
        "CERTIFICADO ANALÍTICO PARCIAL\n\n"
        f"Estudiante: {estudiante.nombre} {estudiante.apellido} - Legajo {estudiante.legajo}\n"
        f"Carrera: {estudiante.carrera}\n"
        f"{_bloque_de_materias(estudiante)}"
    )


GENERADORES: dict[TipoCertificado, GeneradorCertificado] = {
    TipoCertificado.ALUMNO_REGULAR: certificado_alumno_regular,
    TipoCertificado.ANALITICO_PARCIAL: certificado_analitico_parcial,
}


def generar_certificado(solicitud, estudiante, fecha):
    cuerpo = GENERADORES[solicitud.tipo](solicitud, estudiante)
    return f"{ENCABEZADO}{cuerpo}Solicitud N° {solicitud.id} - Fecha de emisión: {fecha}\n"


def _bloque_de_materias(estudiante):
    aprobadas = estudiante.materias_aprobadas()
    if not aprobadas:
        return "Materias aprobadas: ninguna\nPromedio: -\n\n"
    lineas = "".join(f"- {materia.nombre}: {materia.nota}\n" for materia in aprobadas)
    return f"Materias aprobadas:\n{lineas}Promedio: {estudiante.promedio_analitico():.2f}\n\n"
