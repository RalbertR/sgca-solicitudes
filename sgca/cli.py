from sgca.errores import ErrorSolicitud
from sgca.modelos import EstadoSolicitud, FiltroSolicitudes, NuevaSolicitud

MENU = """
=== SGCA - Solicitudes de certificados ===
1. Registrar solicitud
2. Cambiar estado
3. Asignar responsable
4. Buscar solicitudes
5. Reporte
0. Salir"""


def main(servicio):
    while True:
        print(MENU)
        opcion = input("Opción: ")
        if opcion == "0":
            print("Hasta luego.")
            return
        accion = OPCIONES.get(opcion)
        if accion is None:
            print("Opción inválida.")
            continue
        try:
            accion(servicio)
        except ErrorSolicitud as error:
            print(f"ERROR: {error}")


def registrar(servicio):
    legajo = _pedir("Legajo: ")
    tipo = _pedir_valor("Tipo (alumno_regular/analitico_parcial): ")
    prioridad = _pedir_valor("Prioridad (baja/media/alta): ")
    motivo = _pedir("Motivo: ")
    nueva = NuevaSolicitud(_a_numero(legajo, "el legajo debe ser numérico"), tipo, prioridad, motivo)
    solicitud = servicio.registrar(nueva)
    mensaje = f"Solicitud {solicitud.id} registrada. Estado: {solicitud.estado}. Área: {solicitud.area}."
    if solicitud.estado == EstadoSolicitud.RECHAZADA:
        mensaje += " Motivo: el estudiante tiene deuda administrativa."
    print(mensaje)


def cambiar_estado(servicio):
    id_texto = _pedir("ID de solicitud: ")
    estado = _pedir_valor("Nuevo estado (pendiente/en_proceso/emitida/rechazada): ")
    cambio = servicio.cambiar_estado(_a_numero(id_texto, "el ID debe ser numérico"), estado)
    print(f"Solicitud {cambio.solicitud.id}: {cambio.anterior} -> {cambio.solicitud.estado}.")
    if cambio.ruta_certificado is not None:
        print(f"Certificado generado: {cambio.ruta_certificado}")
        print(f"Correo enviado a {cambio.email_notificado}: "
              f"su certificado de {cambio.solicitud.tipo.descripcion} está disponible.")


def asignar_responsable(servicio):
    id_texto = _pedir("ID de solicitud: ")
    nombre = _pedir("Responsable: ")
    solicitud = servicio.asignar_responsable(_a_numero(id_texto, "el ID debe ser numérico"), nombre)
    print(f"Solicitud {solicitud.id} asignada a {solicitud.responsable} ({solicitud.area}).")


def buscar(servicio):
    filtro = FiltroSolicitudes(
        estado=_pedir_valor("Estado (vacío = todos): "),
        tipo=_pedir_valor("Tipo (vacío = todos): "),
        prioridad=_pedir_valor("Prioridad (vacío = todas): "),
        legajo=_pedir("Legajo (vacío = todos): "),
    )
    resultado = servicio.buscar(filtro)
    if not resultado:
        print("No se encontraron solicitudes.")
        return
    for solicitud, estudiante in resultado:
        print(f"#{solicitud.id} | {solicitud.legajo} {estudiante.apellido}, {estudiante.nombre} | {solicitud.tipo} | "
              f"{solicitud.prioridad} | {solicitud.estado} | {solicitud.responsable or '-'}")
    print(f"Total: {len(resultado)}")


def mostrar_reporte(servicio):
    reporte = servicio.reporte()
    print("Reporte de solicitudes")
    print(f"Total: {reporte.total}")
    print(f"Por estado: {_formatear_conteo(reporte.por_estado)}")
    print(f"Por tipo: {_formatear_conteo(reporte.por_tipo)}")
    print(f"Por prioridad: {_formatear_conteo(reporte.por_prioridad)}")


OPCIONES = {
    "1": registrar,
    "2": cambiar_estado,
    "3": asignar_responsable,
    "4": buscar,
    "5": mostrar_reporte,
}


def _pedir(texto):
    return input(texto).strip()


def _pedir_valor(texto):
    return _pedir(texto).lower()


def _a_numero(texto, mensaje_de_error):
    try:
        return int(texto)
    except ValueError:
        raise ErrorSolicitud(mensaje_de_error) from None


def _formatear_conteo(conteo):
    return ", ".join(f"{clave}={cantidad}" for clave, cantidad in conteo.items())
