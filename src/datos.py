"""
Cargar, guardar y validar datos.

Entrada : archivos CSV de data/processed/ y lo que escribe el usuario.
Proceso : validar y convertir cada fila en un objeto.
Salida  : listas de Transaccion / Deseo / MetaAhorro / PagoProgramado / Dataframe
"""
import csv
from datetime import datetime

from src.config import (
    COLUMNAS, TIPOS, TIPO_GASTO, MODOS, CATEGORIAS_GASTO, CATEGORIAS_INGRESO,
    ARCHIVO_TRANSACCIONES, ARCHIVO_DESEOS, ARCHIVO_METAS, ARCHIVO_PAGOS,
)
from src.modelos import Transaccion, Deseo, MetaAhorro, PagoProgramado


class ErrorValidacion(ValueError):
    """Se lanza cuando un dato no cumple las reglas."""


# Validaciones
def validar_monto(texto):
    """'12.50' -> 12.5. Rechaza texto, cero y negativos."""
    try:
        monto = float(str(texto).replace(",", "").replace("$", "").strip())
    except ValueError:
        raise ErrorValidacion(f"'{texto}' no es un número válido")
    if monto <= 0:
        raise ErrorValidacion("El monto debe ser mayor que 0")
    if monto > 100_000:
        raise ErrorValidacion("El monto es demasiado alto, revisa si está bien escrito")
    return round(monto, 2)


def validar_fecha(texto):
    """Acepta 'AAAA-MM-DD' o 'DD/MM/AAAA'. Vacío = ahora."""
    texto = str(texto).strip()
    if texto == "":
        return datetime.now().replace(microsecond=0)
    for formato in ("%Y-%m-%d", "%d/%m/%Y", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(texto, formato)
        except ValueError:
            pass
    raise ErrorValidacion(f"Fecha '{texto}' no válida. Usa AAAA-MM-DD o DD/MM/AAAA")


def validar_tipo(tipo):
    if tipo not in TIPOS:
        raise ErrorValidacion(f"Tipo debe ser uno de {TIPOS}")
    return tipo


def validar_categoria(categoria, tipo):
    permitidas = CATEGORIAS_GASTO if tipo == TIPO_GASTO else CATEGORIAS_INGRESO
    if categoria not in permitidas:
        raise ErrorValidacion(f"Categoría '{categoria}' no válida para {tipo}")
    return categoria


def validar_modo(modo):
    if modo not in MODOS:
        raise ErrorValidacion(f"Modo debe ser uno de {MODOS}")
    return modo


# Transacciones
def cargar_transacciones(ruta=ARCHIVO_TRANSACCIONES):
    """Lee el CSV y devuelve una lista de Transaccion (más reciente primero)."""
    transacciones = []
    with open(ruta, newline="", encoding="utf-8") as f:
        for numero, fila in enumerate(csv.DictReader(f), start=2):
            try:
                transacciones.append(Transaccion.from_dict(fila))
            except (ValueError, KeyError) as e:
                print(f"[aviso] fila {numero} ignorada: {e}")
    transacciones.sort(key=lambda t: t.fecha, reverse=True)
    return transacciones


def guardar_transacciones(transacciones, ruta=ARCHIVO_TRANSACCIONES):
    """Escribe todas las transacciones en el CSV (sobrescribe el archivo)."""
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        escritor = csv.DictWriter(f, fieldnames=COLUMNAS)
        escritor.writeheader()
        for t in sorted(transacciones, key=lambda t: t.fecha, reverse=True):
            escritor.writerow(t.to_dict())


def a_dataframe(transacciones):
    """Convierte la lista en un DataFrame de pandas (para el Integrante 4)."""
    import pandas as pd   # import aquí: así el resto funciona aunque falle pandas
    df = pd.DataFrame([t.to_dict() for t in transacciones], columns=COLUMNAS)
    df["fecha"] = pd.to_datetime(df["fecha"])
    return df


# Deseos, metas y pagos programados
def _leer_csv(ruta):
    if not ruta.exists():
        return []
    with open(ruta, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def cargar_deseos(ruta=ARCHIVO_DESEOS):
    return [Deseo(f["nombre"], f["precio"], f["prioridad"]) for f in _leer_csv(ruta)]


def cargar_metas(ruta=ARCHIVO_METAS):
    return [MetaAhorro(f["meta"], f["monto_objetivo"], f["prioridad"]) for f in _leer_csv(ruta)]


def cargar_pagos_programados(ruta=ARCHIVO_PAGOS):
    pagos = [
        PagoProgramado(validar_fecha(f["fecha"]), f["categoria"], f["monto"],
                       f["descripcion"], f.get("modo", "Tarjeta"))
        for f in _leer_csv(ruta)
    ]
    return sorted(pagos, key=lambda p: p.fecha)


def guardar_pagos_programados(pagos, ruta=ARCHIVO_PAGOS):
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        escritor = csv.writer(f)
        escritor.writerow(["fecha", "categoria", "monto", "descripcion", "modo"])
        for p in pagos:
            escritor.writerow([p.fecha.strftime("%Y-%m-%d"), p.categoria, p.monto, p.descripcion, p.modo])
