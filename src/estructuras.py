"""
Estructuras de datos propias.

  - Pila (LIFO): guarda las últimas acciones para poder DESHACER.
  - Cola (FIFO): guarda los pagos programados en orden de llegada.
"""


class Pila:
    """Último en entrar, primero en salir. Implementada con una lista de Python."""

    def __init__(self):
        self._items = []

    def apilar(self, elemento):
        self._items.append(elemento)

    def desapilar(self):
        if self.esta_vacia():
            raise IndexError("La pila está vacía")
        return self._items.pop()

    def ver_tope(self):
        if self.esta_vacia():
            raise IndexError("La pila está vacía")
        return self._items[-1]

    def esta_vacia(self):
        return len(self._items) == 0

    def __len__(self):
        return len(self._items)


class _Nodo:
    """Nodo de la lista enlazada que usa la Cola."""

    def __init__(self, dato):
        self.dato = dato
        self.siguiente = None


class Cola:
    """
    Primero en entrar, primero en salir.
    Implementada con nodos enlazados para que encolar y desencolar sean O(1)
    (con una lista, list.pop(0) es O(n)).
    """

    def __init__(self):
        self._frente = None
        self._final = None
        self._tamano = 0

    def encolar(self, elemento):
        nuevo = _Nodo(elemento)
        if self._final is None:          # cola vacía
            self._frente = self._final = nuevo
        else:
            self._final.siguiente = nuevo
            self._final = nuevo
        self._tamano += 1

    def desencolar(self):
        if self.esta_vacia():
            raise IndexError("La cola está vacía")
        dato = self._frente.dato
        self._frente = self._frente.siguiente
        if self._frente is None:
            self._final = None
        self._tamano -= 1
        return dato

    def ver_frente(self):
        if self.esta_vacia():
            raise IndexError("La cola está vacía")
        return self._frente.dato

    def esta_vacia(self):
        return self._tamano == 0

    def a_lista(self):
        """Devuelve los elementos en orden, sin sacarlos de la cola."""
        elementos, actual = [], self._frente
        while actual:
            elementos.append(actual.dato)
            actual = actual.siguiente
        return elementos

    def __len__(self):
        return self._tamano
