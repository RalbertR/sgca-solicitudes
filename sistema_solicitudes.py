import json
import os
from datetime import datetime

from sgca.modelos import (
    AREA_ALUMNOS,
    AREA_TESORERIA,
    NOTA_MAXIMA,
    NOTA_MINIMA_APROBACION,
    EstadoSolicitud,
    Prioridad,
    TipoCertificado,
    puede_pasar,
)


class SistemaSolicitudes:

    def __init__(self):
        self.archivo = "datos.json"

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
            if opcion == "1":
                legajo = input("Legajo: ").strip()
                tipo = input("Tipo (alumno_regular/analitico_parcial): ").strip().lower()
                prioridad = input("Prioridad (baja/media/alta): ").strip().lower()
                motivo = input("Motivo: ").strip()
                resultado = self.registrar_solicitud(legajo, tipo, prioridad, motivo)
                if isinstance(resultado, str) and resultado.startswith("ERROR"):
                    print(resultado)
                elif resultado["estado"] == EstadoSolicitud.RECHAZADA:
                    print("Solicitud " + str(resultado["id"]) + " registrada. Estado: " + EstadoSolicitud.RECHAZADA
                          + ". Área: " + AREA_TESORERIA + ". Motivo: el estudiante tiene deuda administrativa.")
                else:
                    print("Solicitud " + str(resultado["id"]) + " registrada. Estado: " + EstadoSolicitud.PENDIENTE
                          + ". Área: " + AREA_ALUMNOS + ".")
            elif opcion == "2":
                self.pedir_cambio_de_estado()
            elif opcion == "3":
                id_texto = input("ID de solicitud: ").strip()
                nombre = input("Responsable: ").strip()
                try:
                    id_solicitud = int(id_texto)
                except ValueError:
                    print("ERROR: el ID debe ser numérico")
                    continue
                print(self.asignar_responsable(id_solicitud, nombre))
            elif opcion == "4":
                estado = input("Estado (vacío = todos): ").strip().lower()
                tipo = input("Tipo (vacío = todos): ").strip().lower()
                prioridad = input("Prioridad (vacío = todas): ").strip().lower()
                legajo = input("Legajo (vacío = todos): ").strip()
                self.filtrar_solicitudes(estado, tipo, prioridad, legajo)
            elif opcion == "5":
                self.reporte()
            elif opcion == "0":
                print("Hasta luego.")
                break
            else:
                print("Opción inválida.")

    def registrar_solicitud(self, legajo, tipo, prioridad, motivo):
        try:
            numero_legajo = int(legajo)
        except ValueError:
            return "ERROR: el legajo debe ser numérico"
        f = open(self.archivo, encoding="utf-8")
        datos = json.load(f)
        f.close()
        estudiante = self._buscar_estudiante(datos, numero_legajo)
        if estudiante is None:
            return "ERROR: no existe un estudiante con legajo " + str(numero_legajo)
        error = self._validar_tipo_y_prioridad(tipo, prioridad)
        if error is not None:
            return error
        estado, area = self._estado_y_area_inicial(estudiante)
        solicitud = {
            "id": self._proximo_id(datos),
            "legajo": numero_legajo,
            "tipo": tipo,
            "prioridad": prioridad,
            "estado": estado,
            "area": area,
            "responsable": None,
            "motivo": motivo,
            "fecha": datetime.now().strftime("%Y-%m-%d"),
        }
        datos["solicitudes"].append(solicitud)
        f = open(self.archivo, "w", encoding="utf-8")
        json.dump(datos, f, ensure_ascii=False, indent=2)
        f.write("\n")
        f.close()
        return solicitud

    def _buscar_estudiante(self, datos, legajo):
        for estudiante in datos["estudiantes"]:
            if estudiante["legajo"] == legajo:
                return estudiante
        return None

    def _buscar_solicitud(self, datos, id_solicitud):
        for solicitud in datos["solicitudes"]:
            if solicitud["id"] == id_solicitud:
                return solicitud
        return None

    def _validar_tipo_y_prioridad(self, tipo, prioridad):
        if tipo not in list(TipoCertificado):
            return "ERROR: tipo de certificado inválido: " + tipo
        if prioridad not in list(Prioridad):
            return "ERROR: prioridad inválida: " + prioridad
        return None

    def _estado_y_area_inicial(self, estudiante):
        if estudiante["deuda"]:
            return EstadoSolicitud.RECHAZADA, AREA_TESORERIA
        return EstadoSolicitud.PENDIENTE, AREA_ALUMNOS

    def _proximo_id(self, datos):
        ultimo_id = 0
        for solicitud in datos["solicitudes"]:
            if solicitud["id"] > ultimo_id:
                ultimo_id = solicitud["id"]
        return ultimo_id + 1

    def pedir_cambio_de_estado(self):
        id_texto = input("ID de solicitud: ").strip()
        estado = input("Nuevo estado (pendiente/en_proceso/emitida/rechazada): ").strip().lower()
        try:
            id_solicitud = int(id_texto)
        except ValueError:
            print("ERROR: el ID debe ser numérico")
            return
        resultado = self.cambiar_estado(id_solicitud, estado)
        if resultado.startswith("ERROR"):
            print(resultado)

    def cambiar_estado(self, id_solicitud, nuevo_estado):
        f = open(self.archivo, encoding="utf-8")
        datos = json.load(f)
        f.close()
        solicitud = self._buscar_solicitud(datos, id_solicitud)
        if solicitud is None:
            return "ERROR: no existe la solicitud " + str(id_solicitud)
        error = self._validar_transicion(solicitud, nuevo_estado)
        if error is not None:
            return error
        anterior = solicitud["estado"]
        solicitud["estado"] = nuevo_estado
        f = open(self.archivo, "w", encoding="utf-8")
        json.dump(datos, f, ensure_ascii=False, indent=2)
        f.write("\n")
        f.close()
        print("Solicitud " + str(id_solicitud) + ": " + anterior + " -> " + nuevo_estado + ".")
        if nuevo_estado == EstadoSolicitud.EMITIDA:
            self._emitir(datos, solicitud)
        return ""

    def _validar_transicion(self, solicitud, nuevo_estado):
        actual = solicitud["estado"]
        if nuevo_estado not in list(EstadoSolicitud):
            return "ERROR: estado inválido: " + nuevo_estado
        if not puede_pasar(EstadoSolicitud(actual), EstadoSolicitud(nuevo_estado)):
            return "ERROR: no se puede pasar de " + actual + " a " + nuevo_estado
        if nuevo_estado == EstadoSolicitud.EMITIDA and solicitud["responsable"] is None:
            return "ERROR: la solicitud " + str(solicitud["id"]) + " no tiene responsable asignado"
        return None

    def _emitir(self, datos, solicitud):
        estudiante = self._buscar_estudiante(datos, solicitud["legajo"])
        fecha = datetime.now().strftime("%Y-%m-%d")
        texto = self._generar_texto_certificado(solicitud, estudiante, fecha)
        ruta = self._guardar_certificado(solicitud["id"], texto)
        print("Certificado generado: " + ruta)
        self._avisar_por_correo(estudiante, solicitud["tipo"])

    def _generar_texto_certificado(self, solicitud, estudiante, fecha):
        texto = "SGCA - Sistema de Gestión de Certificados Académicos\n"
        if solicitud["tipo"] == TipoCertificado.ALUMNO_REGULAR:
            texto += "CERTIFICADO DE ALUMNO REGULAR\n\n"
            texto += ("Se certifica que " + estudiante["nombre"] + " " + estudiante["apellido"] + ", legajo "
                      + str(estudiante["legajo"]) + ", es alumno/a regular de la carrera "
                      + estudiante["carrera"] + ".\n\n")
        elif solicitud["tipo"] == TipoCertificado.ANALITICO_PARCIAL:
            texto += "CERTIFICADO ANALÍTICO PARCIAL\n\n"
            texto += ("Estudiante: " + estudiante["nombre"] + " " + estudiante["apellido"] + " - Legajo "
                      + str(estudiante["legajo"]) + "\n")
            texto += "Carrera: " + estudiante["carrera"] + "\n"
            texto += self._bloque_de_materias(estudiante["materias"])
        texto += "Solicitud N° " + str(solicitud["id"]) + " - Fecha de emisión: " + fecha + "\n"
        return texto

    def _bloque_de_materias(self, materias):
        aprobadas = self._materias_aprobadas(materias)
        if len(aprobadas) == 0:
            return "Materias aprobadas: ninguna\nPromedio: -\n\n"
        lineas = "Materias aprobadas:\n"
        for materia in aprobadas:
            lineas += "- " + materia["nombre"] + ": " + str(materia["nota"]) + "\n"
        return lineas + "Promedio: " + format(self._calcular_promedio(materias), ".2f") + "\n\n"

    def _materias_aprobadas(self, materias):
        aprobadas = []
        for materia in materias:
            nota_valida = NOTA_MINIMA_APROBACION <= materia["nota"] <= NOTA_MAXIMA
            if nota_valida and not materia["extracurricular"]:
                aprobadas.append(materia)
        return aprobadas

    def _calcular_promedio(self, materias):
        aprobadas = self._materias_aprobadas(materias)
        if len(aprobadas) == 0:
            return None
        return sum(materia["nota"] for materia in aprobadas) / len(aprobadas)

    def _guardar_certificado(self, id_solicitud, texto):
        os.makedirs("certificados", exist_ok=True)
        ruta = "certificados/certificado_" + str(id_solicitud) + ".txt"
        f = open(ruta, "w", encoding="utf-8")
        f.write(texto)
        f.close()
        return ruta

    def _avisar_por_correo(self, estudiante, tipo):
        descripcion = TipoCertificado(tipo).descripcion
        print("Correo enviado a " + estudiante["email"] + ": su certificado de " + descripcion + " está disponible.")

    def asignar_responsable(self, id_solicitud, nombre):
        f = open(self.archivo, encoding="utf-8")
        datos = json.load(f)
        f.close()
        solicitud = self._buscar_solicitud(datos, id_solicitud)
        if solicitud is None:
            return "ERROR: no existe la solicitud " + str(id_solicitud)
        responsable = None
        for candidato in datos["responsables"]:
            if candidato["nombre"] == nombre:
                responsable = candidato
        if responsable is None:
            return "ERROR: no existe el responsable " + nombre
        if responsable["area"] != solicitud["area"]:
            return "ERROR: " + nombre + " no pertenece al área " + solicitud["area"]
        solicitud["responsable"] = nombre
        f = open(self.archivo, "w", encoding="utf-8")
        json.dump(datos, f, ensure_ascii=False, indent=2)
        f.write("\n")
        f.close()
        return "Solicitud " + str(id_solicitud) + " asignada a " + nombre + " (" + responsable["area"] + ")."

    def filtrar_solicitudes(self, estado, tipo, prioridad, legajo):
        f = open(self.archivo, encoding="utf-8")
        datos = json.load(f)
        f.close()
        encontradas = []
        for solicitud in datos["solicitudes"]:
            if estado != "" and solicitud["estado"] != estado:
                continue
            if tipo != "" and solicitud["tipo"] != tipo:
                continue
            if prioridad != "" and solicitud["prioridad"] != prioridad:
                continue
            if legajo != "" and str(solicitud["legajo"]) != legajo:
                continue
            encontradas.append(solicitud)
        if len(encontradas) == 0:
            print("No se encontraron solicitudes.")
            return
        encontradas.sort(key=lambda solicitud: solicitud["id"])
        for solicitud in encontradas:
            estudiante = self._buscar_estudiante(datos, solicitud["legajo"])
            responsable = solicitud["responsable"]
            if responsable is None:
                responsable = "-"
            print("#" + str(solicitud["id"]) + " | " + str(solicitud["legajo"]) + " " + estudiante["apellido"]
                  + ", " + estudiante["nombre"] + " | " + solicitud["tipo"] + " | " + solicitud["prioridad"]
                  + " | " + solicitud["estado"] + " | " + responsable)
        print("Total: " + str(len(encontradas)))

    def reporte(self):
        f = open(self.archivo, encoding="utf-8")
        datos = json.load(f)
        f.close()
        por_estado = {estado.value: 0 for estado in EstadoSolicitud}
        por_tipo = {tipo.value: 0 for tipo in TipoCertificado}
        por_prioridad = {prioridad.value: 0 for prioridad in Prioridad}
        for solicitud in datos["solicitudes"]:
            por_estado[solicitud["estado"]] += 1
            por_tipo[solicitud["tipo"]] += 1
            por_prioridad[solicitud["prioridad"]] += 1
        print("Reporte de solicitudes")
        print("Total: " + str(len(datos["solicitudes"])))
        print("Por estado: " + self._formatear_conteo(por_estado))
        print("Por tipo: " + self._formatear_conteo(por_tipo))
        print("Por prioridad: " + self._formatear_conteo(por_prioridad))

    def _formatear_conteo(self, conteo):
        return ", ".join(clave + "=" + str(cantidad) for clave, cantidad in conteo.items())