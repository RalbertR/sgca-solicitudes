from sgca.modelos import (
    TRANSICIONES,
    EstadoSolicitud,
    Estudiante,
    FiltroSolicitudes,
    Materia,
    Prioridad,
    Solicitud,
    TipoCertificado,
    puede_pasar,
)


def test_transiciones_permitidas():
    assert puede_pasar(EstadoSolicitud.PENDIENTE, EstadoSolicitud.EN_PROCESO)
    assert puede_pasar(EstadoSolicitud.PENDIENTE, EstadoSolicitud.RECHAZADA)
    assert puede_pasar(EstadoSolicitud.EN_PROCESO, EstadoSolicitud.EMITIDA)
    assert puede_pasar(EstadoSolicitud.EN_PROCESO, EstadoSolicitud.RECHAZADA)
    assert not puede_pasar(EstadoSolicitud.PENDIENTE, EstadoSolicitud.EMITIDA)
    assert not puede_pasar(EstadoSolicitud.PENDIENTE, EstadoSolicitud.PENDIENTE)


def test_estados_finales_sin_salida():
    assert TRANSICIONES[EstadoSolicitud.EMITIDA] == frozenset()
    assert TRANSICIONES[EstadoSolicitud.RECHAZADA] == frozenset()


def test_descripcion_del_tipo():
    assert TipoCertificado.ALUMNO_REGULAR.descripcion == "alumno regular"
    assert TipoCertificado.ANALITICO_PARCIAL.descripcion == "analítico parcial"


def _lucia():
    return Estudiante(
        legajo=1001,
        nombre="Lucía",
        apellido="Ferreyra",
        email="lucia.ferreyra@alumnos.example.edu.ar",
        carrera="Tecnicatura Universitaria en Programación",
        deuda=False,
        materias=[
            Materia("Programación I", 8, False),
            Materia("Matemática", 6, False),
            Materia("Inglés I", 9, False),
            Materia("Taller de Fotografía", 10, True),
            Materia("Bases de Datos I", 2, False),
        ],
    )


def test_materias_aprobadas_excluye_extracurriculares_y_desaprobadas():
    nombres = [materia.nombre for materia in _lucia().materias_aprobadas()]
    assert nombres == ["Programación I", "Matemática", "Inglés I"]


def test_materia_aprobada_en_los_limites_de_la_escala():
    assert Materia("Física", 4, False).esta_aprobada()
    assert Materia("Física", 10, False).esta_aprobada()
    assert not Materia("Física", 3, False).esta_aprobada()
    assert not Materia("Física", 11, False).esta_aprobada()


def test_promedio_analitico():
    assert round(_lucia().promedio_analitico(), 2) == 7.67


def test_promedio_sin_materias_aprobadas():
    joaquin = Estudiante(1004, "Joaquín", "Paz", "x", "y", False, [Materia("Matemática", 3, False)])
    assert joaquin.promedio_analitico() is None


def _solicitud(id_solicitud, legajo, tipo, prioridad, estado):
    return Solicitud(id_solicitud, legajo, tipo, prioridad, estado, "Departamento de Alumnos", None, "x", "2026-10-20")


SOLICITUDES = [
    _solicitud(1, 1001, TipoCertificado.ALUMNO_REGULAR, Prioridad.MEDIA, EstadoSolicitud.PENDIENTE),
    _solicitud(2, 1003, TipoCertificado.ANALITICO_PARCIAL, Prioridad.ALTA, EstadoSolicitud.EN_PROCESO),
    _solicitud(3, 1001, TipoCertificado.ANALITICO_PARCIAL, Prioridad.BAJA, EstadoSolicitud.PENDIENTE),
]


def test_filtro_vacio_coincide_con_todo():
    filtro = FiltroSolicitudes()
    assert all(filtro.coincide(solicitud) for solicitud in SOLICITUDES)


def test_filtro_combina_estado_y_tipo():
    filtro = FiltroSolicitudes(estado="pendiente", tipo="analitico_parcial")
    assert [solicitud.id for solicitud in SOLICITUDES if filtro.coincide(solicitud)] == [3]


def test_filtro_por_legajo_compara_como_texto():
    filtro = FiltroSolicitudes(legajo="1001")
    assert [solicitud.id for solicitud in SOLICITUDES if filtro.coincide(solicitud)] == [1, 3]
    assert not FiltroSolicitudes(legajo="abc").coincide(SOLICITUDES[0])
