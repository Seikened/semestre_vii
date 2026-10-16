from sklearn.datasets import fetch_california_housing
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    root_mean_squared_error,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PolynomialFeatures, StandardScaler


def scores(modelo, X, y):
    y_pred = modelo.predict(X)
    r2 = r2_score(y, y_pred)
    mse = mean_squared_error(y, y_pred)
    rmse = root_mean_squared_error(y, y_pred)
    mae = mean_absolute_error(y, y_pred)
    return f"R²: {r2:.4f} | MSE: {mse:.4f} | RMSE: {rmse:.4f} | MAE: {mae:.4f}"


def ridge_pipeline(alpha):
    return Pipeline([("scaler", StandardScaler()), ("ridge", Ridge(alpha=alpha))])


def poly_pipeline(degree):
    poly = PolynomialFeatures(degree=degree, include_bias=False)
    return Pipeline([("poly", poly), ("lineal", LinearRegression())])


housing = fetch_california_housing()
X, y = housing.data, housing.target
feature_names = housing.feature_names
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print(f"Features: {feature_names}")
print(f"Dataset shape: {X.shape}")

# Regresión lineal
model = LinearRegression()
model.fit(X_train, y_train)

print("\nCoeficientes:")
for caracteristica, coeficiente in zip(feature_names, model.coef_):
    print(f"  {caracteristica:12s}: {coeficiente:+.6f}")
print(f"  {'Intercepto':12s}: {model.intercept_:+.6f}")

print("\nRegresión lineal")
print("Train:", scores(model, X_train, y_train))
print("Test: ", scores(model, X_test, y_test))

# Ridge
pipeline = ridge_pipeline(alpha=10)
pipeline.fit(X_train, y_train)

print("\nRidge (alpha=10)")
print("Train:", scores(pipeline, X_train, y_train))
print("Test: ", scores(pipeline, X_test, y_test))

# Polinómicos de grados 2 y 3
for degree in (2, 3):
    poly_pipe = poly_pipeline(degree)
    poly_pipe.fit(X_train, y_train)
    cantidad = poly_pipe.named_steps["poly"].n_output_features_

    print(f"\nPolinómico grado {degree}: {X.shape[1]} entradas → {cantidad} características")
    print("Train:", scores(poly_pipe, X_train, y_train))
    print("Test: ", scores(poly_pipe, X_test, y_test))

print("\nRMSE y MAE usan unidades de 100 000 USD; MSE las usa al cuadrado.")
