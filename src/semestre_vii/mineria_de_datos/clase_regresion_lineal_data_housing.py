from sklearn.datasets import fetch_california_housing
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, root_mean_squared_error
from sklearn.model_selection import train_test_split

housing = fetch_california_housing()
X, y = housing.data, housing.target
feature_names = housing.feature_names

print(f"Features: {feature_names}")
print(f"Forma del dataset: {X.shape}")

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = LinearRegression()
model.fit(X_train, y_train)

print("\nCoeficientes:")
for caracteristica, coeficiente in zip(feature_names, model.coef_):
    print(f"  {caracteristica:12s}: {coeficiente:+.6f}")
print(f"  {'Intercepto':12s}: {model.intercept_:+.6f}")

print("\nMétricas de evaluación:")
print(f"{'Conjunto':15s} {'R²':>10s} {'MSE':>10s} {'RMSE':>10s} {'MAE':>10s}")
for nombre, X_eval, y_eval in (
    ("Entrenamiento", X_train, y_train),
    ("Prueba", X_test, y_test),
):
    y_pred = model.predict(X_eval)
    r2 = model.score(X_eval, y_eval)
    mse = mean_squared_error(y_eval, y_pred)
    rmse = root_mean_squared_error(y_eval, y_pred)
    mae = mean_absolute_error(y_eval, y_pred)
    print(f"{nombre:15s} {r2:10.4f} {mse:10.4f} {rmse:10.4f} {mae:10.4f}")

print("\nR²: coeficiente de determinación; mayor es mejor, con un máximo de 1.")
print("MSE: error cuadrático medio; penaliza más los errores grandes.")
print("RMSE: raíz del MSE; expresa el error en las mismas unidades que el objetivo.")
print("MAE: promedio del error absoluto, en las mismas unidades que el objetivo.")
print("En MSE, RMSE y MAE, menor es mejor; 0 significa predicciones perfectas.")
print("El objetivo está en unidades de 100 000 USD; MSE usa esas unidades al cuadrado.")
