"""
Convierte el Excel original en los CSV que usa la app.

Ejecutar UNA vez (o cuando cambie el Excel):   python scripts/preparar_datos.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))   # para poder importar src

import pandas as pd

from src.config import (EXCEL_ORIGINAL, ARCHIVO_TRANSACCIONES, ARCHIVO_DESEOS,
                        ARCHIVO_METAS, ARCHIVO_PAGOS, COLUMNAS, TIPOS, FORMATO_FECHA)

RENOMBRAR = {
    "Fecha": "fecha", "Mode": "modo", "Categoria": "categoria", "Monto (USD)": "monto",
    "Ingresos/Gastos": "tipo", "Descripcion": "descripcion", "Origen": "origen",
}


def preparar_transacciones():
    df = pd.read_excel(EXCEL_ORIGINAL).rename(columns=RENOMBRAR)
    faltan = set(COLUMNAS) - set(df.columns)
    if faltan:
        raise SystemExit(f"Al Excel le faltan columnas: {faltan}")

    df = df[COLUMNAS].copy()
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
    df["categoria"] = df["categoria"].str.strip()
    df["descripcion"] = df["descripcion"].fillna("")
    antes = len(df)
    df = df.dropna(subset=["fecha", "monto"])
    df = df[(df["monto"] > 0) & (df["tipo"].isin(TIPOS))]
    df = df.sort_values("fecha", ascending=False)
    df["fecha"] = df["fecha"].dt.strftime(FORMATO_FECHA)

    ARCHIVO_TRANSACCIONES.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(ARCHIVO_TRANSACCIONES, index=False, encoding="utf-8")
    print(f"✓ {ARCHIVO_TRANSACCIONES.name}: {len(df)} filas ({antes - len(df)} descartadas)")


def crear_ejemplos():
    """Crea los CSV de ejemplo solo si no existen (para no borrar cambios del equipo)."""
    ejemplos = {
        ARCHIVO_DESEOS: "nombre,precio,prioridad\n"
                        "Audífonos,40,8\nZapatos deportivos,55,6\nLibro de Python,15,9\n"
                        "Mochila nueva,35,5\nCurso en línea,25,7\nSalida al cine,12,4\n",
        ARCHIVO_METAS: "meta,monto_objetivo,prioridad\n"
                       "Fondo de emergencia,200,10\nLaptop,600,8\nViaje de graduación,150,5\n",
        ARCHIVO_PAGOS: "fecha,categoria,monto,descripcion,modo\n"
                       "2018-10-01,Subscripciones,9.99,Streaming,Tarjeta\n"
                       "2018-10-05,Subscripciones,15.00,Plan de celular,Tarjeta\n"
                       "2018-10-10,Hogar,25.00,Internet,Transferencia\n",
    }
    for ruta, contenido in ejemplos.items():
        if ruta.exists():
            print(f"- {ruta.name} ya existe, no se modificó")
        else:
            ruta.write_text(contenido, encoding="utf-8")
            print(f"✓ {ruta.name} creado")


if __name__ == "__main__":
    preparar_transacciones()
    crear_ejemplos()
