from datetime import date
from pathlib import Path

import pytest

from sgca.errores import ErrorSolicitud
from sgca.modelos import (
    AREA_ALUMNOS,
    AREA_TESORERIA,
    EstadoSolicitud,
    Estudiante,
    FiltroSolicitudes,
    Materia,
    NuevaSolicitud,
    Prioridad,
    Responsable,
    Solicitud,
    TipoCertificado,
)
from sgca.servicio import ServicioSolicitudes

HOY = date(2026, 11, 1)


class RepositorioEnMemoria:

    def __init__(self, estudiantes, responsables, solicitudes):
        self.estudiantes = {estudiante.legajo: estudiante for estudiante in estudiantes}
        self.responsables = {responsable.nombre: responsable for responsable in responsables}
        self.solicitudes = {solicitud.id: solicitud for solicitud in solicitudes}

    def buscar_estudiante(self, legajo):
        return self.estudiantes.get(legajo)

    def buscar_responsable(self, nombre):
        return self.responsables.get(nombre)

    def buscar_solicitud(self, id_solicitud):
        return self.solicitudes.get(id_solicitud)

    def listar_solicitudes(self):
        return list(self.solicitudes.values())

    def guardar_solicitud(self, solicitud):
        self.solicitudes[solicitud.id] = solicitud

    def proximo_id(self):
        return max(self.solicitudes, default=0) + 1


def _servicio(tmp_path):
    repositorio = RepositorioEnMemoria(
        estudiantes=[
            Estudiante(1001, "Lucía", "Ferreyra", "lucia@example.edu.ar", "TUP", False, [Materia("Programación I", 8, False)]),
            Estudiante(1002, "Tomás", "Benítez", "tomas@example.edu.ar", "TUP", True, []),
        ],
        responsables=[Responsable("Graciela Molina", AREA_ALUMNOS), Responsable("Silvia Ortega", AREA_TESORERIA)],
        solicitudes=[
            Solicitud(1, 1001, TipoCertificado.ALUMNO_REGULAR, Prioridad.MEDIA, EstadoSolicitud.PENDIENTE,
                      AREA_ALUMNOS, None, "x", "2026-10-20"),
            Solicitud(2, 1001, TipoCertificado.ANALITICO_PARCIAL, Prioridad.ALTA, EstadoSolicitud.EN_PROCESO,
                      AREA_ALUMNOS, "Graciela Molina", "x", "2026-10-22"),
        ],
    )
    return ServicioSolicitudes(repositorio, lambda: HOY, tmp_path / "certificados")


def test_registrar_con_deuda_va_a_tesoreria(tmp_path):
    solicitud = _servicio(tmp_path).registrar(NuevaSolicitud(1002, "alumno_regular", "baja", "x"))
    assert solicitud.id == 3
    assert solicitud.estado == EstadoSolicitud.RECHAZADA
    assert solicitud.area == AREA_TESORERIA
    assert solicitud.fecha == "2026-11-01"


def test_registrar_tipo_invalido_lanza_error(tmp_path):
    with pytest.raises(ErrorSolicitud, match="tipo de certificado inválido: titulo"):
        _servicio(tmp_path).registrar(NuevaSolicitud(1001, "titulo", "baja", "x"))


def test_registrar_sin_deuda_queda_pendiente_en_alumnos(tmp_path):
    solicitud = _servicio(tmp_path).registrar(NuevaSolicitud(1001, "analitico_parcial", "alta", "Beca"))
    assert solicitud.estado == EstadoSolicitud.PENDIENTE
    assert solicitud.area == AREA_ALUMNOS
    assert solicitud.responsable is None


def test_registrar_legajo_inexistente_lanza_error(tmp_path):
    with pytest.raises(ErrorSolicitud, match="no existe un estudiante con legajo 9999"):
        _servicio(tmp_path).registrar(NuevaSolicitud(9999, "alumno_regular", "baja", "x"))


def test_emitir_sin_responsable_lanza_error(tmp_path):
    servicio = _servicio(tmp_path)
    servicio.cambiar_estado(1, "en_proceso")
    with pytest.raises(ErrorSolicitud, match="la solicitud 1 no tiene responsable asignado"):
        servicio.cambiar_estado(1, "emitida")


def test_emitir_escribe_certificado(tmp_path):
    cambio = _servicio(tmp_path).cambiar_estado(2, "emitida")
    assert cambio.anterior == EstadoSolicitud.EN_PROCESO
    assert cambio.solicitud.estado == EstadoSolicitud.EMITIDA
    assert cambio.ruta_certificado == (tmp_path / "certificados" / "certificado_2.txt").as_posix()
    assert cambio.email_notificado == "lucia@example.edu.ar"
    texto = Path(cambio.ruta_certificado).read_text(encoding="utf-8")
    assert "Promedio: 8.00" in texto
    assert texto.endswith("Fecha de emisión: 2026-11-01\n")


def test_cambio_sin_emision_no_genera_certificado(tmp_path):
    cambio = _servicio(tmp_path).cambiar_estado(1, "en_proceso")
    assert cambio.ruta_certificado is None
    assert cambio.email_notificado is None


def test_transicion_no_permitida_lanza_error(tmp_path):
    servicio = _servicio(tmp_path)
    with pytest.raises(ErrorSolicitud, match="no se puede pasar de pendiente a emitida"):
        servicio.cambiar_estado(1, "emitida")
    assert servicio.repositorio.buscar_solicitud(1).estado == EstadoSolicitud.PENDIENTE


def test_estado_invalido_lanza_error(tmp_path):
    with pytest.raises(ErrorSolicitud, match="estado inválido: anulada"):
        _servicio(tmp_path).cambiar_estado(1, "anulada")


def test_asignar_responsable_del_area(tmp_path):
    servicio = _servicio(tmp_path)
    solicitud = servicio.asignar_responsable(1, "Graciela Molina")
    assert solicitud.responsable == "Graciela Molina"
    assert servicio.repositorio.buscar_solicitud(1).responsable == "Graciela Molina"


def test_asignar_responsable_inexistente_lanza_error(tmp_path):
    with pytest.raises(ErrorSolicitud, match="no existe el responsable Nadie"):
        _servicio(tmp_path).asignar_responsable(1, "Nadie")


def test_asignar_responsable_de_otra_area_lanza_error(tmp_path):
    with pytest.raises(ErrorSolicitud, match="Silvia Ortega no pertenece al área Departamento de Alumnos"):
        _servicio(tmp_path).asignar_responsable(1, "Silvia Ortega")


def test_buscar_devuelve_solicitud_y_estudiante(tmp_path):
    resultado = _servicio(tmp_path).buscar(FiltroSolicitudes(legajo="1001"))
    assert [(solicitud.id, estudiante.apellido) for solicitud, estudiante in resultado] == [(1, "Ferreyra"), (2, "Ferreyra")]


def test_reporte_cuenta_por_estado_tipo_y_prioridad(tmp_path):
    reporte = _servicio(tmp_path).reporte()
    assert reporte.total == 2
    assert reporte.por_estado == {"pendiente": 1, "en_proceso": 1, "emitida": 0, "rechazada": 0}
    assert reporte.por_tipo == {"alumno_regular": 1, "analitico_parcial": 1}
    assert reporte.por_prioridad == {"baja": 0, "media": 1, "alta": 1}
