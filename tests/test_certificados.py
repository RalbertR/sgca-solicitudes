from sgca.certificados import GENERADORES, generar_certificado
from sgca.modelos import (
    AREA_ALUMNOS,
    EstadoSolicitud,
    Estudiante,
    Materia,
    Prioridad,
    Solicitud,
    TipoCertificado,
)


def _estudiante(materias):
    return Estudiante(1004, "Joaquín", "Paz", "joaquin@example.edu.ar", "TUP", False, materias)


def _solicitud(tipo):
    return Solicitud(7, 1004, tipo, Prioridad.BAJA, EstadoSolicitud.EMITIDA, AREA_ALUMNOS, "Graciela Molina", "x",
                     "2026-10-20")


def test_hay_generador_para_cada_tipo():
    assert set(GENERADORES) == set(TipoCertificado)


def test_alumno_regular_texto():
    texto = generar_certificado(_solicitud(TipoCertificado.ALUMNO_REGULAR), _estudiante([]), "2026-11-01")
    assert texto == (
        "SGCA - Sistema de Gestión de Certificados Académicos\n"
        "CERTIFICADO DE ALUMNO REGULAR\n"
        "\n"
        "Se certifica que Joaquín Paz, legajo 1004, es alumno/a regular de la carrera TUP.\n"
        "\n"
        "Solicitud N° 7 - Fecha de emisión: 2026-11-01\n"
    )


def test_analitico_sin_aprobadas():
    estudiante = _estudiante([Materia("Matemática", 3, False), Materia("Coro Universitario", 9, True)])
    texto = generar_certificado(_solicitud(TipoCertificado.ANALITICO_PARCIAL), estudiante, "2026-11-01")
    assert "Materias aprobadas: ninguna\nPromedio: -\n" in texto
    assert "Coro Universitario" not in texto
