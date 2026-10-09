from matplotlib.figure import Figure

from semestre_vii.vision_de_maquina.vision_node import Grafica

from .experimento import ResultadoRuido


def uniforme(resultado: ResultadoRuido, fila: int = 100) -> Figure:
    sigma_entrada = (resultado.ruidosa - resultado.limpia).tensor.std(correction=0).item() * 255
    sigma_salida = (resultado.filtrada - resultado.limpia).tensor.std(correction=0).item() * 255
    return (
        Grafica("Ruido gaussiano sobre una imagen uniforme", columnas=3)
        .imagen(resultado.limpia, "Limpia: todos los píxeles = 127", rango="unidad")
        .imagen(resultado.ruidosa, f"Ruido normal: σ medida = {sigma_entrada:.2f}", rango="unidad")
        .imagen(resultado.filtrada, f"GLPF: σ residual = {sigma_salida:.2f}", rango="unidad")
        .histogramas(
            (resultado.ruidosa, "Con ruido"), (resultado.filtrada, "GLPF"),
            titulo="Distribución antes y después",
        )
        .senales(
            (resultado.limpia * 255, "Limpia"),
            (resultado.ruidosa * 255, "Con ruido"),
            (resultado.filtrada * 255, "GLPF"),
            fila=fila, titulo=f"Corte horizontal, fila {fila}", ylabel="Tono de gris",
        )
        .espectro(resultado.espectro, "Fourier después del pasabajas")
        .mostrar(block=False)
    )


def imagen_real(resultado: ResultadoRuido, corte: float) -> Figure:
    descartada = (resultado.ruidosa - resultado.filtrada + 127 / 255).clip()
    limpia_suavizada = resultado.limpia.fft().pasabajas_gaussiano(corte).inversa()
    perdida_limpia = (resultado.limpia - limpia_suavizada + 127 / 255).clip()
    return (
        Grafica(f"{resultado.limpia.titulo}: ruido, desenfoque y umbral", columnas=3)
        .imagen(resultado.limpia, "Referencia limpia", rango="unidad")
        .imagen(resultado.ruidosa, "Entrada con ruido", rango="unidad")
        .imagen(resultado.filtrada, f"Pasabajas gaussiano: corte = {corte:g}", rango="unidad")
        .imagen(resultado.con_umbral, f"Comparación espacial: umbral = {resultado.umbral:g}", rango="unidad")
        .imagen(descartada, "Entrada - GLPF + 127", rango="unidad")
        .imagen(perdida_limpia, "Limpia - GLPF(limpia) + 127", rango="unidad")
        .mostrar(block=False)
    )


def diagnostico(resultado: ResultadoRuido, fila: int = 100, *, block: bool = True) -> Figure:
    diferencia = resultado.ruidosa - resultado.filtrada
    superior = resultado.limpia * 0 + resultado.umbral
    inferior = resultado.limpia * 0 - resultado.umbral
    return (
        Grafica("Qué atenúa Fourier y qué conserva la comparación espacial", columnas=3)
        .espectro(resultado.ruidosa.fft(), "Fourier de la entrada con ruido")
        .espectro(resultado.espectro, "Fourier multiplicada por H")
        .mascara(resultado.espectro, "H: pasabajas gaussiano")
        .senales(
            (resultado.limpia * 255, "Limpia"),
            (resultado.ruidosa * 255, "Con ruido"),
            (resultado.filtrada * 255, "GLPF"),
            (resultado.con_umbral * 255, "Con umbral"),
            fila=fila, titulo=f"Fila {fila}: antes y después", ylabel="Tono de gris",
        )
        .senales(
            (diferencia * 255, "Entrada - GLPF"),
            (superior, "+umbral"), (inferior, "-umbral"),
            fila=fila, titulo="Diferencia que decide la selección", cero=True,
            ylabel="Diferencia en tonos de gris",
        )
        .senales(
            ((resultado.filtrada - resultado.limpia) * 255, "Error de GLPF"),
            ((resultado.con_umbral - resultado.limpia) * 255, "Error con umbral"),
            fila=fila, titulo="Error frente a la referencia limpia", cero=True,
            ylabel="Error en tonos de gris",
        )
        .mostrar(block=block)
    )
