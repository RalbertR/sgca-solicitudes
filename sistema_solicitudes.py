from sgca.errores import ErrorSolicitud
from sgca.modelos import (
    AREA_ALUMNOS,
    AREA_TESORERIA,
    EstadoSolicitud,
    FiltroSolicitudes,
    NuevaSolicitud,
    Prioridad,
    Solicitud,
    TipoCertificado,
    puede_pasar,
)


class SistemaSolicitudes:

    def __init__(self, repositorio, reloj, directorio_certificados):
        self.repositorio = repositorio
        self.reloj = reloj
        self.directorio_certificados = directorio_certificados

    def menu(self):
        while True:
            print()
            print("=== SGCA - Solicitudes de certificados ===")
            print("1. Registrar solicitud")
            print("2. Cambiar estado")
            print("3. Asignar responsable")
            print("4. Buscar solicitudes")
            print("5. Reporte")
            print("0. Salir")
            opcion = input("Opción: ")
            if opcion == "0":
                print("Hasta luego.")
                break
            try:
                self._ejecutar_opcion(opcion)
            except ErrorSolicitud as error:
                print("ERROR: " + str(error))

    def _ejecutar_opcion(self, opcion):
        if opcion == "1":
            self.pedir_registro()
        elif opcion == "2":
            self.pedir_cambio_de_estado()
        elif opcion == "3":
            self.pedir_asignacion()
        elif opcion == "4":
            self.pedir_busqueda()
        elif opcion == "5":
            self.reporte()
        else:
            print("Opción inválida.")

    def pedir_registro(self):
        legajo = input("Legajo: ").strip()
        tipo = input("Tipo (alumno_regular/analitico_parcial): ").strip().lower()
        prioridad = input("Prioridad (baja/media/alta): ").strip().lower()
        motivo = input("Motivo: ").strip()
        nueva = NuevaSolicitud(_a_numero(legajo, "el legajo debe ser numérico"), tipo, prioridad, motivo)
        solicitud = self.registrar_solicitud(nueva)
        if solicitud.estado == EstadoSolicitud.RECHAZADA:
            print("Solicitud " + str(solicitud.id) + " registrada. Estado: " + solicitud.estado
                  + ". Área: " + solicitud.area + ". Motivo: el estudiante tiene deuda administrativa.")
        else:
            print("Solicitud " + str(solicitud.id) + " registrada. Estado: " + solicitud.estado
                  + ". Área: " + solicitud.area + ".")

    def registrar_solicitud(self, nueva):
        estudiante = self.repositorio.buscar_estudiante(nueva.legajo)
        if estudiante is None:
            raise ErrorSolicitud("no existe un estudiante con legajo " + str(nueva.legajo))
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

    def _validar_tipo_y_prioridad(self, tipo, prioridad):
        if tipo not in list(TipoCertificado):
            raise ErrorSolicitud("tipo de certificado inválido: " + tipo)
        if prioridad not in list(Prioridad):
            raise ErrorSolicitud("prioridad inválida: " + prioridad)

    def _estado_y_area_inicial(self, estudiante):
        if estudiante.deuda:
            return EstadoSolicitud.RECHAZADA, AREA_TESORERIA
        return EstadoSolicitud.PENDIENTE, AREA_ALUMNOS

    def pedir_cambio_de_estado(self):
        id_texto = input("ID de solicitud: ").strip()
        estado = input("Nuevo estado (pendiente/en_proceso/emitida/rechazada): ").strip().lower()
        self.cambiar_estado(_a_numero(id_texto, "el ID debe ser numérico"), estado)

    def cambiar_estado(self, id_solicitud, nuevo_estado):
        solicitud = self._buscar_solicitud(id_solicitud)
        self._validar_transicion(solicitud, nuevo_estado)
        anterior = solicitud.estado
        solicitud.estado = EstadoSolicitud(nuevo_estado)
        self.repositorio.guardar_solicitud(solicitud)
        print("Solicitud " + str(id_solicitud) + ": " + anterior + " -> " + solicitud.estado + ".")
        if solicitud.estado == EstadoSolicitud.EMITIDA:
            self._emitir(solicitud)

    def _buscar_solicitud(self, id_solicitud):
        solicitud = self.repositorio.buscar_solicitud(id_solicitud)
        if solicitud is None:
            raise ErrorSolicitud("no existe la solicitud " + str(id_solicitud))
        return solicitud

    def _validar_transicion(self, solicitud, nuevo_estado):
        if nuevo_estado not in list(EstadoSolicitud):
            raise ErrorSolicitud("estado inválido: " + nuevo_estado)
        if not puede_pasar(solicitud.estado, EstadoSolicitud(nuevo_estado)):
            raise ErrorSolicitud("no se puede pasar de " + solicitud.estado + " a " + nuevo_estado)
        if nuevo_estado == EstadoSolicitud.EMITIDA and solicitud.responsable is None:
            raise ErrorSolicitud("la solicitud " + str(solicitud.id) + " no tiene responsable asignado")

    def _emitir(self, solicitud):
        estudiante = self.repositorio.buscar_estudiante(solicitud.legajo)
        texto = self._generar_texto_certificado(solicitud, estudiante, self.reloj().isoformat())
        ruta = self._guardar_certificado(solicitud.id, texto)
        print("Certificado generado: " + ruta)
        self._avisar_por_correo(estudiante, solicitud.tipo)

    def _generar_texto_certificado(self, solicitud, estudiante, fecha):
        texto = "SGCA - Sistema de Gestión de Certificados Académicos\n"
        if solicitud.tipo == TipoCertificado.ALUMNO_REGULAR:
            texto += "CERTIFICADO DE ALUMNO REGULAR\n\n"
            texto += ("Se certifica que " + estudiante.nombre + " " + estudiante.apellido + ", legajo "
                      + str(estudiante.legajo) + ", es alumno/a regular de la carrera "
                      + estudiante.carrera + ".\n\n")
        elif solicitud.tipo == TipoCertificado.ANALITICO_PARCIAL:
            texto += "CERTIFICADO ANALÍTICO PARCIAL\n\n"
            texto += ("Estudiante: " + estudiante.nombre + " " + estudiante.apellido + " - Legajo "
                      + str(estudiante.legajo) + "\n")
            texto += "Carrera: " + estudiante.carrera + "\n"
            texto += self._bloque_de_materias(estudiante)
        texto += "Solicitud N° " + str(solicitud.id) + " - Fecha de emisión: " + fecha + "\n"
        return texto

    def _bloque_de_materias(self, estudiante):
        aprobadas = estudiante.materias_aprobadas()
        if not aprobadas:
            return "Materias aprobadas: ninguna\nPromedio: -\n\n"
        lineas = "Materias aprobadas:\n"
        for materia in aprobadas:
            lineas += "- " + materia.nombre + ": " + str(materia.nota) + "\n"
        return lineas + "Promedio: " + format(estudiante.promedio_analitico(), ".2f") + "\n\n"

    def _guardar_certificado(self, id_solicitud, texto):
        self.directorio_certificados.mkdir(parents=True, exist_ok=True)
        ruta = self.directorio_certificados / ("certificado_" + str(id_solicitud) + ".txt")
        ruta.write_text(texto, encoding="utf-8")
        return ruta.as_posix()

    def _avisar_por_correo(self, estudiante, tipo):
        print("Correo enviado a " + estudiante.email + ": su certificado de " + tipo.descripcion + " está disponible.")

    def pedir_asignacion(self):
        id_texto = input("ID de solicitud: ").strip()
        nombre = input("Responsable: ").strip()
        solicitud = self.asignar_responsable(_a_numero(id_texto, "el ID debe ser numérico"), nombre)
        print("Solicitud " + str(solicitud.id) + " asignada a " + solicitud.responsable + " (" + solicitud.area + ").")

    def asignar_responsable(self, id_solicitud, nombre):
        solicitud = self._buscar_solicitud(id_solicitud)
        responsable = self.repositorio.buscar_responsable(nombre)
        if responsable is None:
            raise ErrorSolicitud("no existe el responsable " + nombre)
        if responsable.area != solicitud.area:
            raise ErrorSolicitud(nombre + " no pertenece al área " + solicitud.area)
        solicitud.responsable = responsable.nombre
        self.repositorio.guardar_solicitud(solicitud)
        return solicitud

    def pedir_busqueda(self):
        filtro = FiltroSolicitudes(
            estado=input("Estado (vacío = todos): ").strip().lower(),
            tipo=input("Tipo (vacío = todos): ").strip().lower(),
            prioridad=input("Prioridad (vacío = todas): ").strip().lower(),
            legajo=input("Legajo (vacío = todos): ").strip(),
        )
        self.filtrar_solicitudes(filtro)

    def filtrar_solicitudes(self, filtro):
        encontradas = [solicitud for solicitud in self.repositorio.listar_solicitudes() if filtro.coincide(solicitud)]
        if not encontradas:
            print("No se encontraron solicitudes.")
            return
        encontradas.sort(key=lambda solicitud: solicitud.id)
        for solicitud in encontradas:
            estudiante = self.repositorio.buscar_estudiante(solicitud.legajo)
            responsable = solicitud.responsable or "-"
            print("#" + str(solicitud.id) + " | " + str(solicitud.legajo) + " " + estudiante.apellido
                  + ", " + estudiante.nombre + " | " + solicitud.tipo + " | " + solicitud.prioridad
                  + " | " + solicitud.estado + " | " + responsable)
        print("Total: " + str(len(encontradas)))

    def reporte(self):
        solicitudes = self.repositorio.listar_solicitudes()
        por_estado = {estado.value: 0 for estado in EstadoSolicitud}
        por_tipo = {tipo.value: 0 for tipo in TipoCertificado}
        por_prioridad = {prioridad.value: 0 for prioridad in Prioridad}
        for solicitud in solicitudes:
            por_estado[solicitud.estado.value] += 1
            por_tipo[solicitud.tipo.value] += 1
            por_prioridad[solicitud.prioridad.value] += 1
        print("Reporte de solicitudes")
        print("Total: " + str(len(solicitudes)))
        print("Por estado: " + self._formatear_conteo(por_estado))
        print("Por tipo: " + self._formatear_conteo(por_tipo))
        print("Por prioridad: " + self._formatear_conteo(por_prioridad))

    def _formatear_conteo(self, conteo):
        return ", ".join(clave + "=" + str(cantidad) for clave, cantidad in conteo.items())


def _a_numero(texto, mensaje_de_error):
    try:
        return int(texto)
    except ValueError:
        raise ErrorSolicitud(mensaje_de_error) from None
