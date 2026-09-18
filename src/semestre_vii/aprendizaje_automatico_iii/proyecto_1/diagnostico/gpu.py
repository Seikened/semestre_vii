"""Comprueba si PyTorch puede usar la GPU antes de entrenar."""

import shutil
import subprocess

import torch


def info_nvidia() -> bool:
    if shutil.which("nvidia-smi") is None:
        print("nvidia-smi: no encontrado")
        return False

    resultado = subprocess.run(
        [
            "nvidia-smi",
            "--query-gpu=name,memory.total,driver_version",
            "--format=csv,noheader",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    if resultado.returncode != 0:
        print("nvidia-smi: instalado, pero no pudo consultar la GPU")
        return False

    print(f"NVIDIA: {resultado.stdout.strip()}")
    return True


def main() -> None:
    print("\n=== GPU CHECK ===\n")
    driver_nvidia = info_nvidia()

    print(f"PyTorch: {torch.__version__}")
    print(f"CUDA de PyTorch: {torch.version.cuda or 'no incluida'}")
    print(f"ROCm de PyTorch: {getattr(torch.version, 'hip', None) or 'no incluido'}")
    print(f"GPU disponible para PyTorch: {torch.cuda.is_available()}")

    if not torch.cuda.is_available():
        print("\n❌ PyTorch NO está usando la GPU.")
        if driver_nvidia:
            print("La NVIDIA sí está visible en Linux, así que probablemente instalaste PyTorch sin CUDA.")
            print("No corras train_model.py todavía; pásame esta salida y corregimos PyTorch/uv.")
        else:
            print("Linux/PyTorch no están viendo una GPU compatible.")
            print("Pásame esta salida y revisamos primero el driver o el tipo de GPU.")
        return

    indice = torch.cuda.current_device()
    propiedades = torch.cuda.get_device_properties(indice)
    memoria_gb = propiedades.total_memory / 1024**3

    print(f"\n✅ GPU detectada: {torch.cuda.get_device_name(indice)}")
    print(f"Dispositivo: cuda:{indice}")
    print(f"VRAM: {memoria_gb:.1f} GB")

    prueba = torch.ones((1024, 1024), device=f"cuda:{indice}")
    resultado = (prueba @ prueba).mean()
    torch.cuda.synchronize(indice)
    print(f"Prueba de cálculo: OK ({resultado.item():.1f})")
    print("\n✅ Todo bien. Ya puedes ejecutar train_model.py y debería usar la GPU.")


if __name__ == "__main__":
    main()
