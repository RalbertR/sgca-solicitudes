import json
from typing import Protocol

from sgca.modelos import (
    EstadoSolicitud,
    Estudiante,
    Materia,
    Prioridad,
    Responsable,
    Solicitud,
    TipoCertificado,
)


class RepositorioSolicitudes(Protocol):

    def buscar_estudiante(self, legajo: int) -> Estudiante | None: ...

    def buscar_responsable(self, nombre: str) -> Responsable | None: ...

    def buscar_solicitud(self, id_solicitud: int) -> Solicitud | None: ...

    def listar_solicitudes(self) -> list[Solicitud]: ...

    def guardar_solicitud(self, solicitud: Solicitud) -> None: ...

    def proximo_id(self) -> int: ...


class RepositorioJson:

    def __init__(self, ruta):
        self.ruta = ruta

    def buscar_estudiante(self, legajo):
        for registro in self._leer()["estudiantes"]:
            if registro["legajo"] == legajo:
                return _estudiante_desde(registro)
        return None

    def buscar_responsable(self, nombre):
        for registro in self._leer()["responsables"]:
            if registro["nombre"] == nombre:
                return Responsable(**registro)
        return None

    def buscar_solicitud(self, id_solicitud):
        for solicitud in self.listar_solicitudes():
            if solicitud.id == id_solicitud:
                return solicitud
        return None

    def listar_solicitudes(self):
        return [_solicitud_desde(registro) for registro in self._leer()["solicitudes"]]

    def guardar_solicitud(self, solicitud):
        datos = self._leer()
        registros = datos["solicitudes"]
        nuevo = _registro_de(solicitud)
        for indice, registro in enumerate(registros):
            if registro["id"] == solicitud.id:
                registros[indice] = nuevo
                break
        else:
            registros.append(nuevo)
        self._escribir(datos)

    def proximo_id(self):
        return max((registro["id"] for registro in self._leer()["solicitudes"]), default=0) + 1

    def _leer(self):
        with open(self.ruta, encoding="utf-8") as archivo:
            return json.load(archivo)

    def _escribir(self, datos):
        with open(self.ruta, "w", encoding="utf-8") as archivo:
            json.dump(datos, archivo, ensure_ascii=False, indent=2)
            archivo.write("\n")


def _estudiante_desde(registro):
    materias = [Materia(**materia) for materia in registro["materias"]]
    return Estudiante(**{**registro, "materias": materias})


def _solicitud_desde(registro):
    return Solicitud(
        id=registro["id"],
        legajo=registro["legajo"],
        tipo=TipoCertificado(registro["tipo"]),
        prioridad=Prioridad(registro["prioridad"]),
        estado=EstadoSolicitud(registro["estado"]),
        area=registro["area"],
        responsable=registro["responsable"],
        motivo=registro["motivo"],
        fecha=registro["fecha"],
    )


def _registro_de(solicitud):
    return {
        "id": solicitud.id,
        "legajo": solicitud.legajo,
        "tipo": solicitud.tipo.value,
        "prioridad": solicitud.prioridad.value,
        "estado": solicitud.estado.value,
        "area": solicitud.area,
        "responsable": solicitud.responsable,
        "motivo": solicitud.motivo,
        "fecha": solicitud.fecha,
    }
