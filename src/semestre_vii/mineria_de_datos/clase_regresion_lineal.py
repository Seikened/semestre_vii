import matplotlib.pyplot as plt
import numpy as np

X = np.array([1, 2, 3, 4, 5])
y = np.array([1.5, 1.7, 3.2, 3.8, 5.1])


X = np.append(X, [6, 7, 8, 9, 10])
y = np.append(y, [5.9, 6.8, 7.5, 8.2, 9.1])


X_AUM = np.column_stack((np.ones(X.size), X))
w = np.linalg.inv(X_AUM.T @ X_AUM) @ X_AUM.T @ y

print(w)

y_hat = X_AUM @ w

print(y_hat)

fig, ax = plt.subplots(figsize=(6, 4), layout="constrained")
ax.scatter(X, y, color="#374151", s=45, zorder=3, label="Datos")
ax.plot(X, y_hat, color="#0D9488", linewidth=2, label=f"ŷ = {w[0]:.2f} + {w[1]:.2f}x")
ax.set(xlabel="X", ylabel="y")
ax.set_title("Regresión lineal", loc="left", pad=16)
ax.spines[["top", "right"]].set_visible(False)
ax.spines[["left", "bottom"]].set_color("#D1D5DB")
ax.tick_params(colors="#6B7280", length=0)
ax.margins(x=0.08, y=0.12)
ax.legend(frameon=False)
plt.show()
