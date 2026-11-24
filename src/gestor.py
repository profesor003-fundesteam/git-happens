"""
Une al Usuario con la Pila y la Cola.

El menú habla con el gestor; el gestor se encarga de guardar,
deshacer y procesar pagos. Así el menú queda simple.
"""
from datetime import datetime

from src.estructuras import Pila, Cola
from src.modelos import Usuario
from src import datos


class GestorFinanzas:

    def __init__(self, nombre_usuario="Estudiante", ruta=datos.ARCHIVO_TRANSACCIONES,
                 ruta_pagos=datos.ARCHIVO_PAGOS, autoguardar=True):
        self.ruta = ruta
        self.ruta_pagos = ruta_pagos
        self.autoguardar = autoguardar
        self.usuario = Usuario(nombre_usuario, datos.cargar_transacciones(ruta) if ruta.exists() else [])
        self.historial = Pila()          # acciones para deshacer
        self.pagos = Cola()              # pagos programados en orden de fecha
        for pago in datos.cargar_pagos_programados(ruta_pagos):
            self.pagos.encolar(pago)

    # --- Registrar y deshacer ---------------------------------
    def registrar(self, transaccion):
        self.usuario.agregar(transaccion)
        self.historial.apilar(("agregar", transaccion))
        self._guardar()

    def eliminar(self, transaccion):
        self.usuario.eliminar(transaccion)
        self.historial.apilar(("eliminar", transaccion))
        self._guardar()

    def deshacer(self):
        """Revierte la última acción. Devuelve un texto con lo que se deshizo, o None."""
        if self.historial.esta_vacia():
            return None
        accion, transaccion = self.historial.desapilar()
        if accion == "agregar":
            self.usuario.eliminar(transaccion)
            mensaje = f"Se eliminó: {transaccion!r}"
        else:
            self.usuario.agregar(transaccion)
            mensaje = f"Se restauró: {transaccion!r}"
        self._guardar()
        return mensaje

    # --- Pagos programados ------------------------------------
    def programar_pago(self, pago):
        """Agrega un pago y mantiene la cola ordenada por fecha."""
        pendientes = sorted(self.pagos.a_lista() + [pago], key=lambda p: p.fecha)
        self.pagos = Cola()
        for p in pendientes:
            self.pagos.encolar(p)
        datos.guardar_pagos_programados(pendientes, self.ruta_pagos)

    def procesar_pagos(self, hasta=None):
        """Convierte en gastos todos los pagos cuya fecha ya llegó. Devuelve la lista procesada."""
        hasta = hasta or datetime.now()
        procesados = []
        while not self.pagos.esta_vacia() and self.pagos.ver_frente().fecha <= hasta:
            pago = self.pagos.desencolar()
            self.registrar(pago.a_transaccion())
            procesados.append(pago)
        if procesados:
            datos.guardar_pagos_programados(self.pagos.a_lista(), self.ruta_pagos)
        return procesados

    # --- Atajos para los demás módulos ------------------------
    @property
    def transacciones(self):
        return self.usuario.transacciones

    def dataframe(self):
        return datos.a_dataframe(self.usuario.transacciones)

    def _guardar(self):
        if self.autoguardar:
            datos.guardar_transacciones(self.usuario.transacciones, self.ruta)
