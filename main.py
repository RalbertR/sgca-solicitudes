from datetime import date
from pathlib import Path

from sgca.repositorio import RepositorioJson
from sistema_solicitudes import SistemaSolicitudes

if __name__ == "__main__":
    SistemaSolicitudes(RepositorioJson(Path("datos.json")), date.today, Path("certificados")).menu()
