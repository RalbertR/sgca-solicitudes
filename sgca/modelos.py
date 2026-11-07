from dataclasses import dataclass
from enum import StrEnum

AREA_ALUMNOS = "Departamento de Alumnos"
AREA_TESORERIA = "Tesorería"
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
        return "analítico parcial"


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


@dataclass
class Materia:
    nombre: str
    nota: int
    extracurricular: bool

    def esta_aprobada(self):
        return not self.extracurricular and NOTA_MINIMA_APROBACION <= self.nota <= NOTA_MAXIMA


@dataclass
class Estudiante:
    legajo: int
    nombre: str
    apellido: str
    email: str
    carrera: str
    deuda: bool
    materias: list[Materia]

    def materias_aprobadas(self):
        return [materia for materia in self.materias if materia.esta_aprobada()]

    def promedio_analitico(self):
        aprobadas = self.materias_aprobadas()
        if not aprobadas:
            return None
        return sum(materia.nota for materia in aprobadas) / len(aprobadas)


@dataclass
class Responsable:
    nombre: str
    area: str


@dataclass
class Solicitud:
    id: int
    legajo: int
    tipo: TipoCertificado
    prioridad: Prioridad
    estado: EstadoSolicitud
    area: str
    responsable: str | None
    motivo: str
    fecha: str


@dataclass(frozen=True)
class NuevaSolicitud:
    legajo: int
    tipo: str
    prioridad: str
    motivo: str


@dataclass(frozen=True)
class FiltroSolicitudes:
    estado: str = ""
    tipo: str = ""
    prioridad: str = ""
    legajo: str = ""

    def coincide(self, solicitud):
        criterios = [
            (self.estado, solicitud.estado),
            (self.tipo, solicitud.tipo),
            (self.prioridad, solicitud.prioridad),
            (self.legajo, str(solicitud.legajo)),
        ]
        return all(buscado == "" or buscado == valor for buscado, valor in criterios)
