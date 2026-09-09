from pathlib import Path

import pytest
import torch
from PIL import Image

from semestre_vii.vision_de_maquina import DATA_DIR
from semestre_vii.vision_de_maquina.vision_node import VisionNode


def test_data_dir_contiene_las_imagenes_de_la_materia() -> None:
    assert (DATA_DIR / "golf.BMP").is_file()


def test_desde_archivo_carga_rgb_normalizado(tmp_path: Path) -> None:
    ruta = tmp_path / "entrada.png"
    with Image.new("RGB", (2, 1)) as imagen:
        imagen.putdata([(0, 127, 255), (255, 0, 64)])
        imagen.save(ruta)

    node = VisionNode.desde_archivo(ruta, dtype=torch.float64)

    assert node.shape == (3, 1, 2)
    assert node.dtype is torch.float64
    assert node.device.type == "cpu"
    assert node.titulo == "entrada.png"
    assert node.tensor.min() >= 0.0
    assert node.tensor.max() <= 1.0
    esperado = torch.tensor([0.0, 127 / 255, 1.0], dtype=torch.float64)
    assert torch.allclose(node.tensor[:, 0, 0], esperado)


def test_guardar_crea_directorios_y_un_archivo_rgb(tmp_path: Path) -> None:
    ruta = tmp_path / "resultados" / "salida.png"
    tensor = torch.tensor(
        [
            [[1.0, 0.0]],
            [[0.0, 1.0]],
            [[0.0, 0.0]],
        ]
    )

    resultado = VisionNode(tensor).guardar(ruta)

    assert resultado.tensor is tensor
    with Image.open(ruta) as imagen:
        assert imagen.mode == "RGB"
        assert imagen.size == (2, 1)
        assert list(imagen.get_flattened_data()) == [(255, 0, 0), (0, 255, 0)]


def test_guardar_conserva_la_escala_de_grises(tmp_path: Path) -> None:
    ruta = tmp_path / "gris.png"
    tensor = torch.tensor([[[0.0, 0.5, 1.0]]])

    VisionNode(tensor).guardar(ruta)

    with Image.open(ruta) as imagen:
        assert imagen.mode == "L"
        assert list(imagen.get_flattened_data()) == [0, 127, 255]


def test_desde_archivo_propaga_un_archivo_invalido(tmp_path: Path) -> None:
    ruta = tmp_path / "invalida.png"
    ruta.write_text("esto no es una imagen")

    with pytest.raises(OSError):
        VisionNode.desde_archivo(ruta)
