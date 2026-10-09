from enum import IntEnum

from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


class Penalizacion(IntEnum):
    baja = 1
    media = 10
    alta = 100


alpha = Penalizacion.media

pipeline = Pipeline([("scaler", StandardScaler()), ("ridge", Ridge(alpha=alpha))])
