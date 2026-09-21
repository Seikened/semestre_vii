# 03 · Datos

## Unidad de observación

La representación técnica inicial usa una observación por:

```text
semana × estación × producto
```

Con aproximadamente 120 estaciones y tres productos principales existirían del orden de 360 series relacionadas.

## Esquema mínimo

La tabla canónica utilizará formato largo:

| Campo | Papel |
| --- | --- |
| `week` | semana de la observación |
| `station_id` | identificador estable de la estación |
| `product` | categoría de combustible |
| `liters` | variable objetivo de demanda o venta |

La semántica exacta de `liters` debe verificarse con la fuente: venta, despacho, consumo o alguna medida equivalente no deben mezclarse por suposición.

## Entradas candidatas

La planeación histórica menciona:

- ventas semanales por sucursal y producto;
- precios históricos;
- inventario disponible;
- capacidad de almacenamiento;
- entregas realizadas;
- entregas en tránsito;
- tiempos de entrega;
- faltantes;
- calendario;
- promociones;
- clima o movilidad si existe una fuente útil.

Estos elementos son **candidatos**, no requisitos confirmados. Cada variable debe justificar existencia, calidad, disponibilidad al momento de predecir y utilidad medible.

## Datos conocidos en el futuro

Una variable que sólo se conoce después del instante real de predicción no puede utilizarse como entrada futura durante evaluación.

Ejemplos válidos pueden incluir calendario o promociones programadas. Precio, clima u otras covariables sólo pueden usarse a futuro si realmente son conocidas o si se modelan explícitamente como escenarios.

Usar información futura no disponible produciría **data leakage**.

## Organización local

```text
data/desarrollo_de_aplicaciones/reabastecimiento_gasolineras/
├── raw/
├── external/
├── processed/
├── features/
├── backtests/
├── predictions/
└── artifacts/
```

- `raw/`: exportaciones originales; nunca se sobrescriben.
- `external/`: fuentes externas opcionales.
- `processed/`: tabla canónica validada.
- `features/`: derivados materializados sólo cuando aporten claridad o costo.
- `backtests/`: forecasts emitidos sobre cortes históricos.
- `predictions/`: forecasts reales del producto.
- `artifacts/`: métricas y metadatos reproducibles.

El código accede a esta raíz mediante `PROJECT_DATA_DIR`; no se usan rutas absolutas.

## Calidad temporal

Antes de modelar deben investigarse:

- semanas faltantes;
- duplicados por estación, producto y semana;
- cambios de identificador;
- cierres temporales;
- aperturas o bajas;
- valores negativos o físicamente imposibles;
- ceros reales frente a faltantes;
- cambios de unidad;
- cambios estructurales del negocio.

Una semana sin ventas no equivale automáticamente a dato faltante.

## Datos originales y derivados

Toda transformación debe conservar procedencia suficiente para entender:

1. de qué fuente salió;
2. qué limpieza se aplicó;
3. qué configuración produjo el resultado;
4. qué versión del pipeline lo generó.

Los datasets operativos permanecen fuera de Git. Los derivados deben ser reconstruibles a partir de las fuentes disponibles y el código correspondiente.

## Contrato hacia el producto

El motor predictivo debe quedar detrás de una frontera estable. La aplicación no debe depender de la estructura interna del modelo.

Como mínimo, un forecast consumible necesitará identificar:

- serie o combinación estación/producto;
- fecha de corte;
- horizonte;
- predicción puntual;
- intervalo, cuantiles o señal de incertidumbre cuando exista;
- versión del modelo o artefacto;
- timestamp o versión de datos suficiente para trazabilidad.
