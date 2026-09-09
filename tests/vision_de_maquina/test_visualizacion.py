import matplotlib.pyplot as plt
import torch

from semestre_vii.vision_de_maquina.vision_node import VisionNode


def test_graficas_basicas_conservan_la_api_fluent() -> None:
    tensor = torch.linspace(0, 1, 48).reshape(3, 4, 4)
    node = VisionNode(tensor, titulo="Muestra")

    assert node.mostrar(block=False) is node
    assert node.histograma(block=False) is node
    assert len(plt.gcf().axes) == 4
    assert node.graficar_acumulado(block=False) is node
    assert node.mostrar_reporte(block=False) is node
    assert len(plt.gcf().axes) == 5
    comparada = node.negativo()
    diferencias = node.mostrar_diferencias(comparada, magnifier=2, block=False)
    esperado = (node.tensor - comparada.tensor).abs().mul(2).clamp(0, 1)
    assert torch.equal(diferencias.tensor, esperado)
    assert diferencias.titulo == "Diferencias: Muestra vs Muestra"
    plt.close("all")
