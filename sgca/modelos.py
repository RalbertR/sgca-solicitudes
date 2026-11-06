from enum import StrEnum

AREA_ALUMNOS = "Departamento de Alumnos"
AREA_TESORERIA = "Tesoreria"
NOTA_MINIMA_APROBACION = 4
NOTA_MAXIMA = 10


class EstadoSolicitud(StrEnum):
    PENDIENTE = "pendiente"
    EN_PROCESO = "en_proceso"
    EMITIDA = "emitida"
    RECHAZADA = "rechazada"


class TipoCertificado(StrEnum):
    ALUMNO_REGULAR = "alumno_regular"
    ANALITICO_PARCIAL = "analitico_parcial"

    @property
    def descripcion(self):
        if self is TipoCertificado.ALUMNO_REGULAR:
            return "alumno regular"
        return "analitico parcial"


class Prioridad(StrEnum):
    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"


TRANSICIONES = {
    EstadoSolicitud.PENDIENTE: frozenset({EstadoSolicitud.EN_PROCESO, EstadoSolicitud.RECHAZADA}),
    EstadoSolicitud.EN_PROCESO: frozenset({EstadoSolicitud.EMITIDA, EstadoSolicitud.RECHAZADA}),
    EstadoSolicitud.EMITIDA: frozenset(),
    EstadoSolicitud.RECHAZADA: frozenset(),
}


def puede_pasar(actual, nuevo):
    return nuevo in TRANSICIONES[actual]
