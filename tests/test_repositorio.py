import shutil
from dataclasses import replace
from pathlib import Path

from sgca.modelos import EstadoSolicitud, Prioridad, Solicitud, TipoCertificado
from sgca.repositorio import RepositorioJson

FIXTURE = Path(__file__).parent / "datos_prueba.json"


def _repositorio(tmp_path):
    ruta = tmp_path / "datos.json"
    shutil.copy(FIXTURE, ruta)
    return RepositorioJson(ruta)


def test_buscar_estudiante_y_responsable(tmp_path):
    repositorio = _repositorio(tmp_path)
    assert repositorio.buscar_estudiante(1003).apellido == "Ríos"
    assert repositorio.buscar_estudiante(9999) is None
    assert repositorio.buscar_responsable("Silvia Ortega").area == "Tesorería"
    assert repositorio.buscar_responsable("Nadie") is None


def test_proximo_id(tmp_path):
    assert _repositorio(tmp_path).proximo_id() == 4


def test_guardar_y_buscar_solicitud(tmp_path):
    repositorio = _repositorio(tmp_path)
    nueva = Solicitud(
        4, 1004, TipoCertificado.ALUMNO_REGULAR, Prioridad.BAJA, EstadoSolicitud.PENDIENTE,
        "Departamento de Alumnos", None, "Constancia", "2026-11-01",
    )
    repositorio.guardar_solicitud(nueva)
    assert RepositorioJson(tmp_path / "datos.json").buscar_solicitud(4) == nueva
    repositorio.guardar_solicitud(replace(nueva, estado=EstadoSolicitud.EN_PROCESO))
    assert len(repositorio.listar_solicitudes()) == 4
    assert repositorio.buscar_solicitud(4).estado == EstadoSolicitud.EN_PROCESO


def test_formato_json_se_conserva(tmp_path):
    repositorio = _repositorio(tmp_path)
    repositorio.guardar_solicitud(repositorio.buscar_solicitud(1))
    assert (tmp_path / "datos.json").read_text(encoding="utf-8") == FIXTURE.read_text(encoding="utf-8")
