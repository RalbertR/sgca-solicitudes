from sgca.modelos import TRANSICIONES, EstadoSolicitud, Estudiante, Materia, TipoCertificado, puede_pasar


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
