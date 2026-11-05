import os
from dataclasses import dataclass, field
from pathlib import Path

from psycopg.conninfo import make_conninfo


@dataclass(frozen=True)
class Configuracion:
    conexion: str
    api_key: str
    luna_api_key: str | None = field(repr=False)
    originales: Path
    corpus: Path

    @classmethod
    def cargar(cls):
        clave = Path(os.environ["API_KEY_FILE"]).read_text().strip()
        password = Path(os.environ["DB_PASSWORD_FILE"]).read_text().strip()
        if len(clave) < 32 or len(password) < 32:
            raise ValueError("Las credenciales locales deben contener al menos 32 caracteres.")
        conexion = make_conninfo(
            host=os.getenv("DB_HOST", "db"), dbname="documental", user="motor",
            password=password, connect_timeout=5,
        )
        ruta_luna = Path(os.getenv("LUNA_API_KEY_FILE", "/run/secrets/luna_api_key"))
        clave_luna = ruta_luna.read_text().strip() if ruta_luna.is_file() else ""
        return cls(
            conexion=conexion, api_key=clave, luna_api_key=clave_luna or None,
            originales=Path(os.getenv("ORIGINALES_DIR", "/datos/originales")),
            corpus=Path(os.getenv("CORPUS_DIR", "/proyecto/demo/contratos")),
        )
