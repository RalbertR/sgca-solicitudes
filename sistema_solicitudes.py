import json
from datetime import datetime


class SistemaSolicitudes:

    def __init__(self):
        self.archivo = "datos.json"

    def menu(self):
        while True:
            print()
            print("=== SGCA - Solicitudes de certificados ===")
            print("1. Registrar solicitud")
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
