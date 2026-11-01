import json
import os
from datetime import datetime


class SistemaSolicitudes:

    def __init__(self):
        self.archivo = "datos.json"

    def menu(self):
        while True:
            print()
            print("=== SGCA - Solicitudes de certificados ===")
            print("1. Registrar solicitud")
            print("2. Cambiar estado")
            print("0. Salir")
            op = input("Opción: ")
            if op == "1":
                legajo = input("Legajo: ").strip()
                tipo = input("Tipo (alumno_regular/analitico_parcial): ").strip().lower()
                prioridad = input("Prioridad (baja/media/alta): ").strip().lower()
                motivo = input("Motivo: ").strip()
                r = self.registrar_solicitud(legajo, tipo, prioridad, motivo)
                if isinstance(r, str) and r.startswith("ERROR"):
                    print(r)
                elif r["estado"] == "rechazada":
                    print("Solicitud " + str(r["id"]) + " registrada. Estado: rechazada. Área: Tesorería. "
                          "Motivo: el estudiante tiene deuda administrativa.")
                else:
                    print("Solicitud " + str(r["id"]) + " registrada. Estado: pendiente. Área: Departamento de Alumnos.")
            elif op == "2":
                self.procesar()
            elif op == "0":
                print("Hasta luego.")
                break
            else:
                print("Opción inválida.")

    def registrar_solicitud(self, legajo, tipo, prioridad, motivo):
        try:
            leg = int(legajo)
        except ValueError:
            return "ERROR: el legajo debe ser numérico"
        f = open(self.archivo, encoding="utf-8")
        d = json.load(f)
        f.close()
        est = None
        for e in d["estudiantes"]:
            if e["legajo"] == leg:
                est = e
        if est is None:
            return "ERROR: no existe un estudiante con legajo " + str(leg)
        if tipo != "alumno_regular" and tipo != "analitico_parcial":
            return "ERROR: tipo de certificado inválido: " + tipo
        if prioridad != "baja" and prioridad != "media" and prioridad != "alta":
            return "ERROR: prioridad inválida: " + prioridad
        aux = 0
        for s in d["solicitudes"]:
            if s["id"] > aux:
                aux = s["id"]
        if est["deuda"]:
            estado = "rechazada"
            area = "Tesorería"
        else:
            estado = "pendiente"
            area = "Departamento de Alumnos"
        s = {
            "id": aux + 1,
            "legajo": leg,
            "tipo": tipo,
            "prioridad": prioridad,
            "estado": estado,
            "area": area,
            "responsable": None,
            "motivo": motivo,
            "fecha": datetime.now().strftime("%Y-%m-%d"),
        }
        d["solicitudes"].append(s)
        f = open(self.archivo, "w", encoding="utf-8")
        json.dump(d, f, ensure_ascii=False, indent=2)
        f.write("\n")
        f.close()
        return s

    def procesar(self):
        id_txt = input("ID de solicitud: ").strip()
        estado = input("Nuevo estado (pendiente/en_proceso/emitida/rechazada): ").strip().lower()
        try:
            id = int(id_txt)
        except ValueError:
            print("ERROR: el ID debe ser numérico")
            return
        r = self.cambiar_estado(id, estado)
        if r.startswith("ERROR"):
            print(r)

    def cambiar_estado(self, id, estado):
        f = open(self.archivo, encoding="utf-8")
        d = json.load(f)
        f.close()
        s = None
        for x in d["solicitudes"]:
            if x["id"] == id:
                s = x
        if s is None:
            return "ERROR: no existe la solicitud " + str(id)
        if estado not in ["pendiente", "en_proceso", "emitida", "rechazada"]:
            return "ERROR: estado inválido: " + estado
        if s["estado"] == "pendiente":
            if estado != "en_proceso" and estado != "rechazada":
                return "ERROR: no se puede pasar de pendiente a " + estado
        elif s["estado"] == "en_proceso":
            if estado != "emitida" and estado != "rechazada":
                return "ERROR: no se puede pasar de en_proceso a " + estado
        else:
            return "ERROR: no se puede pasar de " + s["estado"] + " a " + estado
        if estado == "emitida" and s["responsable"] is None:
            return "ERROR: la solicitud " + str(id) + " no tiene responsable asignado"
        anterior = s["estado"]
        s["estado"] = estado
        f = open(self.archivo, "w", encoding="utf-8")
        json.dump(d, f, ensure_ascii=False, indent=2)
        f.write("\n")
        f.close()
        print("Solicitud " + str(id) + ": " + anterior + " -> " + estado + ".")
        if estado == "emitida":
            est = None
            for e in d["estudiantes"]:
                if e["legajo"] == s["legajo"]:
                    est = e
            fecha = datetime.now().strftime("%Y-%m-%d")
            if s["tipo"] == "alumno_regular":
                texto = "SGCA - Sistema de Gestión de Certificados Académicos\n"
                texto += "CERTIFICADO DE ALUMNO REGULAR\n\n"
                texto += ("Se certifica que " + est["nombre"] + " " + est["apellido"] + ", legajo "
                          + str(est["legajo"]) + ", es alumno/a regular de la carrera " + est["carrera"] + ".\n\n")
                texto += "Solicitud N° " + str(s["id"]) + " - Fecha de emisión: " + fecha + "\n"
            elif s["tipo"] == "analitico_parcial":
                texto = "SGCA - Sistema de Gestión de Certificados Académicos\n"
                texto += "CERTIFICADO ANALÍTICO PARCIAL\n\n"
                texto += "Estudiante: " + est["nombre"] + " " + est["apellido"] + " - Legajo " + str(est["legajo"]) + "\n"
                texto += "Carrera: " + est["carrera"] + "\n"
                suma = 0
                cant = 0
                lineas = ""
                for m in est["materias"]:
                    if m["nota"] >= 4 and m["nota"] <= 10 and not m["extracurricular"]:
                        suma += m["nota"]
                        cant += 1
                        lineas += "- " + m["nombre"] + ": " + str(m["nota"]) + "\n"
                if cant == 0:
                    texto += "Materias aprobadas: ninguna\n"
                    texto += "Promedio: -\n\n"
                else:
                    texto += "Materias aprobadas:\n" + lineas
                    texto += "Promedio: " + format(suma / cant, ".2f") + "\n\n"
                texto += "Solicitud N° " + str(s["id"]) + " - Fecha de emisión: " + fecha + "\n"
            os.makedirs("certificados", exist_ok=True)
            f = open("certificados/certificado_" + str(s["id"]) + ".txt", "w", encoding="utf-8")
            f.write(texto)
            f.close()
            print("Certificado generado: certificados/certificado_" + str(s["id"]) + ".txt")
            if s["tipo"] == "alumno_regular":
                nombre_tipo = "alumno regular"
            else:
                nombre_tipo = "analítico parcial"
            print("Correo enviado a " + est["email"] + ": su certificado de " + nombre_tipo + " está disponible.")
        return ""
