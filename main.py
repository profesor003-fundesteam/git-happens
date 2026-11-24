"""
Punto de arranque.
Ejecutar desde la carpeta del proyecto:   python main.py
"""
import sys

from src.config import ARCHIVO_TRANSACCIONES


def main():
    if not ARCHIVO_TRANSACCIONES.exists():
        print("No se encontró data/processed/transacciones.csv")
        print("Primero ejecuta:  python scripts/preparar_datos.py")
        sys.exit(1)
    from src.menu import ejecutar
    ejecutar()


if __name__ == "__main__":
    main()
