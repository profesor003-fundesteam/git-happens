"""
Clases principales del proyecto.
"""
from datetime import datetime

from src.config import TIPO_GASTO, TIPO_INGRESO, FORMATO_FECHA, MONEDA


# Cierre (closure): crea una función que "recuerda" el símbolo
def crear_formateador_moneda(simbolo=MONEDA, decimales=2):
    """Devuelve una función que formatea montos. Ej: formato(1500) -> '$1,500.00'."""
    def formatear(monto):
        signo = "-" if monto < 0 else ""
        return f"{signo}{simbolo}{abs(monto):,.{decimales}f}"
    return formatear


formato_moneda = crear_formateador_moneda()


# ---------------------------------------------------------------
class Transaccion:
    """Un movimiento de dinero: ingreso o gasto."""

    def __init__(self, fecha, modo, categoria, monto, tipo, descripcion="", origen="Usuario"):
        self.fecha = fecha                    # datetime
        self.modo = modo                      # Efectivo / Tarjeta / Transferencia
        self.categoria = categoria
        self.monto = round(float(monto), 2)   # siempre positivo, en USD
        self.tipo = tipo                      # "Ingresos" o "Gastos"
        self.descripcion = descripcion
        self.origen = origen                  # Original / Simulado / Usuario

    @property
    def es_gasto(self):
        return self.tipo == TIPO_GASTO

    @property
    def es_ingreso(self):
        return self.tipo == TIPO_INGRESO

    @property
    def monto_con_signo(self):
        """Positivo si entra dinero, negativo si sale. Útil para calcular saldos."""
        return self.monto if self.es_ingreso else -self.monto

    def to_dict(self):
        """Convierte la transacción a diccionario (para CSV o pandas)."""
        return {
            "fecha": self.fecha.strftime(FORMATO_FECHA),
            "modo": self.modo,
            "categoria": self.categoria,
            "monto": self.monto,
            "tipo": self.tipo,
            "descripcion": self.descripcion,
            "origen": self.origen,
        }

    @classmethod
    def from_dict(cls, d):
        """Crea una transacción a partir de una fila del CSV."""
        return cls(
            fecha=datetime.fromisoformat(str(d["fecha"])),
            modo=d["modo"],
            categoria=d["categoria"],
            monto=float(d["monto"]),
            tipo=d["tipo"],
            descripcion=d.get("descripcion", "") or "",
            origen=d.get("origen", "Usuario") or "Usuario",
        )

    def __repr__(self):
        return (f"Transaccion({self.fecha:%Y-%m-%d}, {self.tipo}, {self.categoria}, "
                f"{formato_moneda(self.monto)})")

    def __str__(self):
        monto = ("+" if self.es_ingreso else "-") + formato_moneda(self.monto)
        return (f"{self.fecha:%Y-%m-%d}  {monto:>12}  "
                f"{self.categoria:<15} {self.modo:<13} {self.descripcion}")


# ---------------------------------------------------------------
class Usuario:
    """Dueño de las transacciones. Calcula totales y saldo."""

    def __init__(self, nombre, transacciones=None):
        self.nombre = nombre
        self.transacciones = list(transacciones) if transacciones else []

    def agregar(self, transaccion):
        self.transacciones.append(transaccion)

    def eliminar(self, transaccion):
        self.transacciones.remove(transaccion)

    def total_ingresos(self, mes=None):
        return round(sum(t.monto for t in self._filtrar(mes) if t.es_ingreso), 2)

    def total_gastos(self, mes=None):
        return round(sum(t.monto for t in self._filtrar(mes) if t.es_gasto), 2)

    def saldo(self, mes=None):
        return round(self.total_ingresos(mes) - self.total_gastos(mes), 2)

    def transacciones_del_mes(self, mes):
        """mes en formato 'AAAA-MM', por ejemplo '2018-08'."""
        return self._filtrar(mes)

    def meses_disponibles(self):
        return sorted({t.fecha.strftime("%Y-%m") for t in self.transacciones})

    def _filtrar(self, mes):
        if mes is None:
            return self.transacciones
        return [t for t in self.transacciones if t.fecha.strftime("%Y-%m") == mes]

    def __len__(self):
        return len(self.transacciones)


# ---------------------------------------------------------------
class Deseo:
    """Algo que el usuario quiere comprar. Lo usa el Integrante 3 (mochila)."""

    def __init__(self, nombre, precio, prioridad):
        self.nombre = nombre
        self.precio = round(float(precio), 2)
        self.prioridad = int(prioridad)       # 1 (poco) a 10 (mucho)

    def __repr__(self):
        return f"Deseo({self.nombre}, {formato_moneda(self.precio)}, prioridad={self.prioridad})"


class MetaAhorro:
    """Meta de ahorro. La usa el Integrante 3 (algoritmo voraz)."""

    def __init__(self, nombre, monto_objetivo, prioridad):
        self.nombre = nombre
        self.monto_objetivo = round(float(monto_objetivo), 2)
        self.prioridad = int(prioridad)

    def __repr__(self):
        return f"MetaAhorro({self.nombre}, {formato_moneda(self.monto_objetivo)}, prioridad={self.prioridad})"


class PagoProgramado:
    """Gasto recurrente que se procesa cuando llega su fecha (va en la Cola)."""

    def __init__(self, fecha, categoria, monto, descripcion, modo="Tarjeta"):
        self.fecha = fecha
        self.categoria = categoria
        self.monto = round(float(monto), 2)
        self.descripcion = descripcion
        self.modo = modo

    def a_transaccion(self):
        return Transaccion(self.fecha, self.modo, self.categoria, self.monto,
                           TIPO_GASTO, self.descripcion, origen="Programado")

    def __repr__(self):
        return f"PagoProgramado({self.fecha:%Y-%m-%d}, {self.descripcion}, {formato_moneda(self.monto)})"
