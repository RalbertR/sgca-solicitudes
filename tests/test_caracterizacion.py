import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
FIXTURE = RAIZ / "tests" / "datos_prueba.json"
ESPERADOS = RAIZ / "tests" / "esperados"


@dataclass
class Resultado:
    salida: str
    datos: dict
    certificados: dict


def normalizar(texto):
    return texto.replace(date.today().isoformat(), "<HOY>")


def ejecutar(tmp_path, *entradas):
    shutil.copy(FIXTURE, tmp_path / "datos.json")
    entorno = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    proceso = subprocess.run(
        [sys.executable, str(RAIZ / "main.py")],
        cwd=tmp_path,
        input="\n".join([*entradas, "0"]) + "\n",
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=entorno,
        timeout=10,
    )
    assert proceso.returncode == 0, proceso.stderr
    datos = json.loads((tmp_path / "datos.json").read_text(encoding="utf-8"))
    carpeta = tmp_path / "certificados"
    certificados = {}
    if carpeta.exists():
        for archivo in sorted(carpeta.glob("*.txt")):
            certificados[archivo.name] = normalizar(archivo.read_text(encoding="utf-8"))
    return Resultado(normalizar(proceso.stdout), datos, certificados)


def solicitud(datos, id_solicitud):
    return next(s for s in datos["solicitudes"] if s["id"] == id_solicitud)


def test_registra_solicitud_sin_deuda(tmp_path):
    r = ejecutar(tmp_path, "1", "1003", "alumno_regular", "media", "Constancia")
    assert "Solicitud 4 registrada. Estado: pendiente. Área: Departamento de Alumnos." in r.salida
    nueva = solicitud(r.datos, 4)
    assert nueva == {
        "id": 4,
        "legajo": 1003,
        "tipo": "alumno_regular",
        "prioridad": "media",
        "estado": "pendiente",
        "area": "Departamento de Alumnos",
        "responsable": None,
        "motivo": "Constancia",
        "fecha": date.today().isoformat(),
    }
    assert list(nueva) == ["id", "legajo", "tipo", "prioridad", "estado", "area", "responsable", "motivo", "fecha"]


def test_registra_con_deuda_queda_rechazada_en_tesoreria(tmp_path):
    r = ejecutar(tmp_path, "1", "1002", "analitico_parcial", "alta", "x")
    assert (
        "Solicitud 4 registrada. Estado: rechazada. Área: Tesorería. "
        "Motivo: el estudiante tiene deuda administrativa."
    ) in r.salida
    nueva = solicitud(r.datos, 4)
    assert nueva["estado"] == "rechazada"
    assert nueva["area"] == "Tesorería"


def test_registro_legajo_inexistente(tmp_path):
    r = ejecutar(tmp_path, "1", "9999", "alumno_regular", "baja", "x")
    assert "ERROR: no existe un estudiante con legajo 9999" in r.salida
    assert len(r.datos["solicitudes"]) == 3


def test_registro_legajo_no_numerico(tmp_path):
    r = ejecutar(tmp_path, "1", "abc", "alumno_regular", "baja", "x")
    assert "ERROR: el legajo debe ser numérico" in r.salida
    assert "Traceback" not in r.salida
    assert len(r.datos["solicitudes"]) == 3


def test_registro_tipo_y_prioridad_invalidos(tmp_path):
    r = ejecutar(
        tmp_path,
        "1", "1001", "titulo", "baja", "x",
        "1", "1001", "alumno_regular", "urgente", "x",
    )
    assert "ERROR: tipo de certificado inválido: titulo" in r.salida
    assert "ERROR: prioridad inválida: urgente" in r.salida
    assert len(r.datos["solicitudes"]) == 3


def test_registro_normaliza_tipo_y_prioridad(tmp_path):
    r = ejecutar(tmp_path, "1", "1003", " Alumno_Regular ", " Alta ", "x")
    nueva = solicitud(r.datos, 4)
    assert nueva["tipo"] == "alumno_regular"
    assert nueva["prioridad"] == "alta"


def test_asigna_responsable(tmp_path):
    r = ejecutar(tmp_path, "3", "1", "Graciela Molina")
    assert "Solicitud 1 asignada a Graciela Molina (Departamento de Alumnos)." in r.salida
    assert solicitud(r.datos, 1)["responsable"] == "Graciela Molina"


def test_asigna_responsable_de_otra_area(tmp_path):
    r = ejecutar(tmp_path, "3", "1", "Silvia Ortega")
    assert "ERROR: Silvia Ortega no pertenece al área Departamento de Alumnos" in r.salida
    assert solicitud(r.datos, 1)["responsable"] is None


def test_asigna_responsable_inexistente(tmp_path):
    r = ejecutar(tmp_path, "3", "1", "Nadie")
    assert "ERROR: no existe el responsable Nadie" in r.salida


def test_cambia_estado(tmp_path):
    r = ejecutar(tmp_path, "2", "1", "en_proceso")
    assert "Solicitud 1: pendiente -> en_proceso." in r.salida
    assert solicitud(r.datos, 1)["estado"] == "en_proceso"


def test_transicion_invalida(tmp_path):
    r = ejecutar(tmp_path, "2", "1", "emitida")
    assert "ERROR: no se puede pasar de pendiente a emitida" in r.salida
    assert solicitud(r.datos, 1)["estado"] == "pendiente"


def test_estado_final_no_cambia(tmp_path):
    r = ejecutar(tmp_path, "2", "3", "en_proceso")
    assert "ERROR: no se puede pasar de rechazada a en_proceso" in r.salida
    assert solicitud(r.datos, 3)["estado"] == "rechazada"


def test_estado_invalido(tmp_path):
    r = ejecutar(tmp_path, "2", "1", "archivada")
    assert "ERROR: estado inválido: archivada" in r.salida


def test_emitir_sin_responsable(tmp_path):
    r = ejecutar(tmp_path, "2", "1", "en_proceso", "2", "1", "emitida")
    assert "ERROR: la solicitud 1 no tiene responsable asignado" in r.salida
    assert solicitud(r.datos, 1)["estado"] == "en_proceso"
    assert r.certificados == {}


def test_id_inexistente_y_no_numerico(tmp_path):
    r = ejecutar(tmp_path, "2", "99", "en_proceso", "3", "x", "Graciela Molina")
    assert "ERROR: no existe la solicitud 99" in r.salida
    assert "ERROR: el ID debe ser numérico" in r.salida
    assert "Traceback" not in r.salida


def test_emite_alumno_regular(tmp_path):
    r = ejecutar(
        tmp_path,
        "3", "1", "Graciela Molina",
        "2", "1", "en_proceso",
        "2", "1", "emitida",
    )
    assert "Solicitud 1: en_proceso -> emitida." in r.salida
    assert "Certificado generado: certificados/certificado_1.txt" in r.salida
    assert (
        "Correo enviado a lucia.ferreyra@alumnos.example.edu.ar: "
        "su certificado de alumno regular está disponible."
    ) in r.salida
    assert r.certificados["certificado_1.txt"] == (
        "SGCA - Sistema de Gestión de Certificados Académicos\n"
        "CERTIFICADO DE ALUMNO REGULAR\n"
        "\n"
        "Se certifica que Lucía Ferreyra, legajo 1001, es alumno/a regular de la carrera "
        "Tecnicatura Universitaria en Programación.\n"
        "\n"
        "Solicitud N° 1 - Fecha de emisión: <HOY>\n"
    )


def test_emite_analitico_excluye_extracurriculares_y_desaprobadas(tmp_path):
    r = ejecutar(
        tmp_path,
        "1", "1001", "analitico_parcial", "alta", "Pase de universidad",
        "3", "4", "Graciela Molina",
        "2", "4", "en_proceso",
        "2", "4", "emitida",
    )
    assert (
        "Correo enviado a lucia.ferreyra@alumnos.example.edu.ar: "
        "su certificado de analítico parcial está disponible."
    ) in r.salida
    assert r.certificados["certificado_4.txt"] == (
        "SGCA - Sistema de Gestión de Certificados Académicos\n"
        "CERTIFICADO ANALÍTICO PARCIAL\n"
        "\n"
        "Estudiante: Lucía Ferreyra - Legajo 1001\n"
        "Carrera: Tecnicatura Universitaria en Programación\n"
        "Materias aprobadas:\n"
        "- Programación I: 8\n"
        "- Matemática: 6\n"
        "- Inglés I: 9\n"
        "Promedio: 7.67\n"
        "\n"
        "Solicitud N° 4 - Fecha de emisión: <HOY>\n"
    )


def test_emite_analitico_sin_aprobadas(tmp_path):
    r = ejecutar(
        tmp_path,
        "1", "1004", "analitico_parcial", "media", "x",
        "3", "4", "Martín Quiroga",
        "2", "4", "en_proceso",
        "2", "4", "emitida",
    )
    certificado = r.certificados["certificado_4.txt"]
    assert "Materias aprobadas: ninguna\nPromedio: -\n" in certificado
    assert "Coro Universitario" not in certificado


def test_busca_por_estado_y_tipo(tmp_path):
    r = ejecutar(tmp_path, "4", "pendiente", "alumno_regular", "", "")
    assert "#1 | 1001 Ferreyra, Lucía | alumno_regular | media | pendiente | -" in r.salida
    assert "Total: 1" in r.salida
    assert "#2 |" not in r.salida


def test_busca_por_legajo(tmp_path):
    r = ejecutar(tmp_path, "4", "", "", "", "1003")
    assert "#2 | 1003 Ríos, Valentina | analitico_parcial | alta | en_proceso | Martín Quiroga" in r.salida
    assert "Total: 1" in r.salida


def test_busca_sin_resultados(tmp_path):
    r = ejecutar(tmp_path, "4", "emitida", "", "", "")
    assert "No se encontraron solicitudes." in r.salida
    assert "Total:" not in r.salida


def test_reporte(tmp_path):
    r = ejecutar(tmp_path, "5")
    assert (
        "Reporte de solicitudes\n"
        "Total: 3\n"
        "Por estado: pendiente=1, en_proceso=1, emitida=0, rechazada=1\n"
        "Por tipo: alumno_regular=2, analitico_parcial=1\n"
        "Por prioridad: baja=1, media=1, alta=1\n"
    ) in r.salida


def test_opcion_invalida(tmp_path):
    r = ejecutar(tmp_path, "9")
    assert "Opción inválida." in r.salida
    assert r.salida.rstrip().endswith("Hasta luego.")


def test_recorrido_completo(tmp_path):
    r = ejecutar(
        tmp_path,
        "1", "1001", "analitico_parcial", "alta", "Beca",
        "1", "1002", "alumno_regular", "media", "Obra social",
        "1", "abc", "alumno_regular", "baja", "x",
        "3", "4", "Graciela Molina",
        "3", "4", "Silvia Ortega",
        "2", "4", "en_proceso",
        "2", "4", "emitida",
        "2", "5", "en_proceso",
        "2", "x", "emitida",
        "4", "", "", "", "1001",
        "5",
        "7",
    )
    esperado = (ESPERADOS / "recorrido_completo.txt").read_text(encoding="utf-8")
    assert r.salida == esperado
