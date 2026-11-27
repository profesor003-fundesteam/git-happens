"""
Constantes y rutas compartidas por todo el proyecto.
"""
from pathlib import Path

# Rutas
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_RAW = BASE_DIR / "data" / "raw"
DATA_PROCESSED = BASE_DIR / "data" / "processed"
OUTPUTS = BASE_DIR / "outputs"
GRAFICAS_DIR = OUTPUTS / "graficas"
REPORTES_DIR = OUTPUTS / "reportes"

EXCEL_ORIGINAL = DATA_RAW / "datos_con_ingresos.xlsx"
ARCHIVO_TRANSACCIONES = DATA_PROCESSED / "transacciones.csv"
ARCHIVO_DESEOS = DATA_PROCESSED / "lista_deseos.csv"
ARCHIVO_METAS = DATA_PROCESSED / "metas_ahorro.csv"
ARCHIVO_PAGOS = DATA_PROCESSED / "pagos_programados.csv"

# TODOS usan estas columnas en este orden
COLUMNAS = ["fecha", "modo", "categoria", "monto", "tipo", "descripcion", "origen"]

TIPO_INGRESO = "Ingresos"
TIPO_GASTO = "Gastos"
TIPOS = (TIPO_INGRESO, TIPO_GASTO)

MODOS = ("Efectivo", "Tarjeta", "Transferencia")

CATEGORIAS_GASTO = (
    "Comida", "Transporte", "Hogar", "Medicinas", "Familia",
    "Subscripciones", "Regalos", "Universidad", "Vida Social",
)
CATEGORIAS_INGRESO = ("Salario", "Familia", "Trabajo extra", "Reembolsos", "Ventas")

FORMATO_FECHA = "%Y-%m-%d %H:%M:%S"   # cómo se guarda la fecha en el CSV
MONEDA = "$"
