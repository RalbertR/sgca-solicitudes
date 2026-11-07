from datetime import date
from pathlib import Path

from sgca.cli import main
from sgca.repositorio import RepositorioJson
from sgca.servicio import ServicioSolicitudes

if __name__ == "__main__":
    main(ServicioSolicitudes(RepositorioJson(Path("datos.json")), date.today, Path("certificados")))
