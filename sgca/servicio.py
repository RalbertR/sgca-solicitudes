from dataclasses import dataclass

from sgca.certificados import generar_certificado
from sgca.errores import ErrorSolicitud
from sgca.modelos import (
    AREA_ALUMNOS,
    AREA_TESORERIA,
    EstadoSolicitud,
    Prioridad,
    Solicitud,
    TipoCertificado,
    puede_pasar,
)


@dataclass
class CambioDeEstado:
    solicitud: Solicitud
    anterior: EstadoSolicitud
    ruta_certificado: str | None = None
    email_notificado: str | None = None


@dataclass
class Reporte:
    total: int
    por_estado: dict[str, int]
    por_tipo: dict[str, int]
    por_prioridad: dict[str, int]


class ServicioSolicitudes:

    def __init__(self, repositorio, reloj, directorio_certificados):
        self.repositorio = repositorio
        self.reloj = reloj
        self.directorio_certificados = directorio_certificados

    def registrar(self, nueva):
        estudiante = self.repositorio.buscar_estudiante(nueva.legajo)
        if estudiante is None:
            raise ErrorSolicitud(f"no existe un estudiante con legajo {nueva.legajo}")
        self._validar_tipo_y_prioridad(nueva.tipo, nueva.prioridad)
        estado, area = self._estado_y_area_inicial(estudiante)
        solicitud = Solicitud(
            id=self.repositorio.proximo_id(),
            legajo=nueva.legajo,
            tipo=TipoCertificado(nueva.tipo),
            prioridad=Prioridad(nueva.prioridad),
            estado=estado,
            area=area,
            responsable=None,
            motivo=nueva.motivo,
            fecha=self.reloj().isoformat(),
        )
        self.repositorio.guardar_solicitud(solicitud)
        return solicitud

    def cambiar_estado(self, id_solicitud, nuevo_estado):
        solicitud = self._buscar_solicitud(id_solicitud)
        self._validar_transicion(solicitud, nuevo_estado)
        cambio = CambioDeEstado(solicitud, solicitud.estado)
        solicitud.estado = EstadoSolicitud(nuevo_estado)
        self.repositorio.guardar_solicitud(solicitud)
        if solicitud.estado == EstadoSolicitud.EMITIDA:
            estudiante = self.repositorio.buscar_estudiante(solicitud.legajo)
            cambio.ruta_certificado = self._emitir_certificado(solicitud, estudiante)
            cambio.email_notificado = estudiante.email
        return cambio

    def asignar_responsable(self, id_solicitud, nombre):
        solicitud = self._buscar_solicitud(id_solicitud)
        responsable = self.repositorio.buscar_responsable(nombre)
        if responsable is None:
            raise ErrorSolicitud(f"no existe el responsable {nombre}")
        if responsable.area != solicitud.area:
            raise ErrorSolicitud(f"{nombre} no pertenece al área {solicitud.area}")
        solicitud.responsable = responsable.nombre
        self.repositorio.guardar_solicitud(solicitud)
        return solicitud

    def buscar(self, filtro):
        encontradas = [solicitud for solicitud in self.repositorio.listar_solicitudes() if filtro.coincide(solicitud)]
        encontradas.sort(key=lambda solicitud: solicitud.id)
        return [(solicitud, self.repositorio.buscar_estudiante(solicitud.legajo)) for solicitud in encontradas]

    def reporte(self):
        solicitudes = self.repositorio.listar_solicitudes()
        return Reporte(
            total=len(solicitudes),
            por_estado=_contar(solicitudes, EstadoSolicitud, lambda solicitud: solicitud.estado),
            por_tipo=_contar(solicitudes, TipoCertificado, lambda solicitud: solicitud.tipo),
            por_prioridad=_contar(solicitudes, Prioridad, lambda solicitud: solicitud.prioridad),
        )

    def _buscar_solicitud(self, id_solicitud):
        solicitud = self.repositorio.buscar_solicitud(id_solicitud)
        if solicitud is None:
            raise ErrorSolicitud(f"no existe la solicitud {id_solicitud}")
        return solicitud

    def _validar_tipo_y_prioridad(self, tipo, prioridad):
        if tipo not in list(TipoCertificado):
            raise ErrorSolicitud(f"tipo de certificado inválido: {tipo}")
        if prioridad not in list(Prioridad):
            raise ErrorSolicitud(f"prioridad inválida: {prioridad}")

    def _estado_y_area_inicial(self, estudiante):
        if estudiante.deuda:
            return EstadoSolicitud.RECHAZADA, AREA_TESORERIA
        return EstadoSolicitud.PENDIENTE, AREA_ALUMNOS

    def _validar_transicion(self, solicitud, nuevo_estado):
        if nuevo_estado not in list(EstadoSolicitud):
            raise ErrorSolicitud(f"estado inválido: {nuevo_estado}")
        if not puede_pasar(solicitud.estado, EstadoSolicitud(nuevo_estado)):
            raise ErrorSolicitud(f"no se puede pasar de {solicitud.estado} a {nuevo_estado}")
        if nuevo_estado == EstadoSolicitud.EMITIDA and solicitud.responsable is None:
            raise ErrorSolicitud(f"la solicitud {solicitud.id} no tiene responsable asignado")

    def _emitir_certificado(self, solicitud, estudiante):
        texto = generar_certificado(solicitud, estudiante, self.reloj().isoformat())
        self.directorio_certificados.mkdir(parents=True, exist_ok=True)
        ruta = self.directorio_certificados / f"certificado_{solicitud.id}.txt"
        ruta.write_text(texto, encoding="utf-8")
        return ruta.as_posix()


def _contar(solicitudes, valores_posibles, valor_de):
    conteo = {valor.value: 0 for valor in valores_posibles}
    for solicitud in solicitudes:
        conteo[valor_de(solicitud).value] += 1
    return conteo
