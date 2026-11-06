import numpy as np
from sentence_transformers import SentenceTransformer

MODELO = "intfloat/multilingual-e5-small"
REVISION = "614241f622f53c4eeff9890bdc4f31cfecc418b3"
DIMENSION = 384


class Vectorizador:
    def __init__(self):
        self.modelo = SentenceTransformer(MODELO, revision=REVISION, device="cpu")

    def documentos(self, textos: list[str]) -> np.ndarray:
        pasajes = [f"passage: {texto}" for texto in textos]
        return self.modelo.encode(pasajes, normalize_embeddings=True, show_progress_bar=False)

    def consulta(self, texto: str) -> np.ndarray:
        return self.modelo.encode(f"query: {texto}", normalize_embeddings=True)
