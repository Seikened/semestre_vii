# Desarrollo de Aplicaciones

Materia del semestre VII centrada en el **motor documental inmobiliario**.

La documentación viva se mantiene junto con el código. El proyecto de gasolineras fue descartado por Fernando y se conserva como antecedente.

## Producto

```text
src/semestre_vii/desarrollo_de_aplicaciones/
└── motor_documental/
    ├── README.md
    ├── docs/
    ├── backend/
    └── frontend/
```

El producto extrae, vectoriza y recupera contratos completamente ficticios. La recuperación funciona sin un LLM. La interfaz Nuxt UI también incorpora un chat opcional de GPT-6 Luna conectado al motor local. Cloudflare R2 y WhatsApp oficial se incorporarán después.

El servicio tiene su propio entorno uv en `motor_documental/backend/`, para conservar las dependencias y la versión Python de las demás materias. Consultar el [README del producto](motor_documental/README.md), su [proceso de desarrollo](motor_documental/DEVELOPMENT.md) y la [rúbrica del segundo parcial](motor_documental/docs/09_matriz_rubrica.md).

Las rutas compartidas de la materia son:

```python
from semestre_vii.desarrollo_de_aplicaciones import DATA_DIR, MODELS_DIR
```
