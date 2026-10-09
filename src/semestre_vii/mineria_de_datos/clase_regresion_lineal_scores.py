import numpy as np
from sklearn.linear_model import LinearRegression

# Ejemplo: años de experiencia vs salario
X = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]).reshape(-1, 1)
y = np.array([15000, 18000, 22000, 25000, 30000, 33000, 38000, 45000, 52000, 55000])

# Creamos el modelo y lo entrenamos
model = LinearRegression()
model.fit(X, y)

# Vemos la intercepción y el coeficiente o peso
print(f"Coeficiente (peso): {model.coef_[0]:.4f}")
print(f"Intercepción: {model.intercept_:.4f}")

# Predecimos el salario para 15 años de experiencia
prediccion = model.predict([[15]])
print(f"Salario a los 15 años de experiencia: ${prediccion[0]:.2f}")
print(f"R2 = {model.score(X, y):.4f}")
