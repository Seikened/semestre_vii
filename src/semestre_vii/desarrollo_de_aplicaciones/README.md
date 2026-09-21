# Desarrollo de Aplicaciones

Materia del semestre VII centrada en un único producto de software: **Pronóstico y reabastecimiento de gasolineras**.

No se usa una secuencia `proyecto_1`, `proyecto_2`, etc. La materia evoluciona alrededor del mismo sistema y su documentación viva se mantiene junto con el código.

## Producto

```text
src/semestre_vii/desarrollo_de_aplicaciones/
└── reabastecimiento_gasolineras/
    ├── README.md
    ├── docs/
    ├── backend/
    └── frontend/
```

El producto combina operación de pedidos, autenticación y cuentas, una experiencia para sucursales, una experiencia administrativa y un motor predictivo. **El forecasting es una capacidad del sistema, no la identidad completa del producto.**

Las rutas compartidas de la materia son:

```python
from semestre_vii.desarrollo_de_aplicaciones import DATA_DIR, MODELS_DIR
```
