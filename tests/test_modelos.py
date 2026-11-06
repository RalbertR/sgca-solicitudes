from sgca.modelos import TRANSICIONES, EstadoSolicitud, TipoCertificado, puede_pasar


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
