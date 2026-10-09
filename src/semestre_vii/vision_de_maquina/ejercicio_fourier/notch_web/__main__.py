import argparse
import webbrowser

from .servidor import crear_servidor


def main() -> None:
    parser = argparse.ArgumentParser(description="Laboratorio local de filtros notch del saco")
    parser.add_argument("--port", type=int, default=8768)
    parser.add_argument("--no-browser", action="store_true")
    argumentos = parser.parse_args()
    with crear_servidor(argumentos.port) as servidor:
        url = f"http://127.0.0.1:{servidor.server_port}"
        print(f"Laboratorio notch: {url}", flush=True)
        if not argumentos.no_browser:
            webbrowser.open(url)
        try:
            servidor.serve_forever()
        except KeyboardInterrupt:
            print("Laboratorio cerrado.")


if __name__ == "__main__":
    main()
