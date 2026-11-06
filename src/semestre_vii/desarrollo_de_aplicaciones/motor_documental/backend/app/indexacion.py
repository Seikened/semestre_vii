from dataclasses import dataclass
from uuid import UUID

import numpy as np

from app.modelos import DocumentoExtraido, FragmentoExtraido


@dataclass(frozen=True)
class DocumentoIndexado:
    id: UUID
    coleccion_id: UUID
    titulo: str
    extraido: DocumentoExtraido
    fragmentos: list[FragmentoExtraido]
    vectores: np.ndarray
