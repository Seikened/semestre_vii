"""k-NN exacto por coseno con votación: lo usan la evaluación de precarga y la inferencia."""

from collections import Counter, defaultdict

import numpy as np

from ..esquemas.embedding import Embedding
from ..esquemas.galeria import Galeria
from ..esquemas.pan import ClasePan
from ..esquemas.reconocimiento import Reconocimiento, Vecino


def k_vecinos(similitudes: np.ndarray, clases: np.ndarray, k: int) -> tuple[Vecino, ...]:
    """Los k vectores más parecidos, del más cercano al más lejano."""
    candidatos = np.argpartition(-similitudes, k - 1)[:k]
    ordenados = candidatos[np.argsort(-similitudes[candidatos], kind="stable")]
    return tuple(
        Vecino(
            clase=ClasePan(clases[i]),
            similitud=float(np.clip(similitudes[i], -1, 1)),
            indice=int(i),
        )
        for i in ordenados
    )


def votar(vecinos: tuple[Vecino, ...]) -> ClasePan:
    """Mayoría simple; en empate gana la clase cuyos vecinos suman más similitud."""
    votos = Counter(vecino.clase for vecino in vecinos)
    suma = defaultdict(float)
    for vecino in vecinos:
        suma[vecino.clase] += vecino.similitud
    return max(votos, key=lambda clase: (votos[clase], suma[clase]))


def reconocer(galeria: Galeria, consulta: Embedding, umbral: float) -> Reconocimiento:
    similitudes = galeria.vectores @ consulta.vector
    vecinos = k_vecinos(similitudes, galeria.clases, galeria.manifiesto.k)
    # El pan más parecido de cada clase: muestra hacia dónde se carga la consulta.
    por_clase = {
        clase: float(np.clip(similitudes[galeria.clases == clase].max(), -1, 1))
        for clase in galeria.manifiesto.clases
    }
    if vecinos[0].similitud < umbral:
        # Ni el pan más parecido de la galería se acerca: no se adivina una clase.
        clase = None
    else:
        clase = votar(vecinos)
    return Reconocimiento(clase=clase, vecinos=vecinos, consulta=consulta, por_clase=por_clase)
