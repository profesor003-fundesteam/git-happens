"""
Menú de consola que conecta todos los módulos.

Las opciones que dependen de otros integrantes usan el decorador
@pendiente_de: si su función todavía lanza NotImplementedError,
el menú muestra un aviso en lugar de cerrarse.
"""
from functools import wraps

from src.config import (
    TIPO_INGRESO, TIPO_GASTO, MODOS, CATEGORIAS_GASTO, CATEGORIAS_INGRESO,
)
from src.modelos import Transaccion, PagoProgramado, formato_moneda
from src.gestor import GestorFinanzas
from src import datos


# Decorador (closure): protege las opciones que aún no están listas
def pendiente_de(integrante):
    def decorador(funcion):
        @wraps(funcion)
        def envoltura(*args, **kwargs):
            try:
                return funcion(*args, **kwargs)
            except NotImplementedError as e:
                print(f"\n  [En construcción] {e}")
                print(f"  Esta opción está en desarrollo ({integrante}).")
        return envoltura
    return decorador


# Ayudantes para pedir datos por teclado
def pedir(mensaje, validador, por_defecto=None):
    """Repite la pregunta hasta que el validador acepte la respuesta."""
    while True:
        texto = input(mensaje).strip()
        if texto == "" and por_defecto is not None:
            return por_defecto
        try:
            return validador(texto)
        except datos.ErrorValidacion as e:
            print(f"  ✗ {e}")


def elegir(titulo, opciones):
    """Muestra opciones numeradas y devuelve la elegida."""
    print(f"\n  {titulo}")
    for i, opcion in enumerate(opciones, start=1):
        print(f"   {i}. {opcion}")

    def validar(texto):
        if texto.isdigit() and 1 <= int(texto) <= len(opciones):
            return opciones[int(texto) - 1]
        raise datos.ErrorValidacion(f"Escribe un número del 1 al {len(opciones)}")

    return pedir("  > ", validar)


def mostrar_transacciones(lista, limite=15):
    print(f"\n  {'Fecha':<10}  {'Monto':>12}  {'Categoría':<15} {'Modo':<13} Descripción")
    print("  " + "-" * 75)
    for t in lista[:limite]:
        print("  " + str(t))
    if len(lista) > limite:
        print(f"  ... y {len(lista) - limite} más")


def ultimo_mes(gestor):
    meses = gestor.usuario.meses_disponibles()
    return meses[-1] if meses else None


# Opciones del menú
def opcion_registrar(gestor):
    tipo = elegir("¿Qué quieres registrar?", [TIPO_GASTO, TIPO_INGRESO])
    categorias = CATEGORIAS_GASTO if tipo == TIPO_GASTO else CATEGORIAS_INGRESO
    categoria = elegir("Categoría:", list(categorias))
    modo = elegir("Forma de pago:", list(MODOS))
    monto = pedir("  Monto en USD: ", datos.validar_monto)
    descripcion = input("  Descripción (opcional): ").strip()
    fecha = pedir("  Fecha (AAAA-MM-DD, Enter = hoy): ", datos.validar_fecha)

    t = Transaccion(fecha, modo, categoria, monto, tipo, descripcion, origen="Usuario")
    gestor.registrar(t)
    print(f"\n  ✓ Guardado: {t!r}")


def opcion_ver_ultimos(gestor):
    recientes = sorted(gestor.transacciones, key=lambda t: t.fecha, reverse=True)
    mostrar_transacciones(recientes)


def opcion_deshacer(gestor):
    mensaje = gestor.deshacer()
    print(f"\n  ✓ {mensaje}" if mensaje else "\n  No hay nada que deshacer en esta sesión.")


@pendiente_de("Integrante 2")
def opcion_ordenar(gestor):
    from src import ordenamiento
    ordenamiento.quick_sort([], clave=lambda t: t)      # prueba rápida: ¿ya está implementado?
    campo = elegir("Ordenar por:", ["monto", "fecha", "categoria"])
    algoritmo = elegir("Algoritmo:", ["quick_sort", "merge_sort", "burbuja"])
    desc = elegir("Orden:", ["Mayor a menor", "Menor a mayor"]) == "Mayor a menor"
    lista = gestor.transacciones
    if algoritmo == "burbuja" and len(lista) > 2000:
        print("  (burbuja es lenta: se usarán solo las 2,000 transacciones más recientes)")
        lista = lista[:2000]
    ordenar = getattr(ordenamiento, algoritmo)
    resultado = ordenar(lista, clave=lambda t: getattr(t, campo), desc=desc)
    mostrar_transacciones(resultado)


@pendiente_de("Integrante 4")
def opcion_resumen(gestor):
    from src import analisis, graficas
    df = gestor.dataframe()
    resumen = analisis.resumen_mensual(df)
    print("\n  Resumen de los últimos 6 meses:")
    print(resumen.tail(6).to_string(index=False))
    print("\n  Gasto por categoría (último mes):")
    print(analisis.gasto_por_categoria(df, ultimo_mes(gestor)).to_string(index=False))
    rutas = [graficas.grafica_categorias(df, ultimo_mes(gestor)),
             graficas.grafica_ingresos_vs_gastos(df),
             graficas.grafica_ahorro_mensual(df)]
    print("\n  Gráficas guardadas en:")
    for r in rutas:
        print(f"   - {r}")


def _presupuesto_sugerido(gestor):
    return max(gestor.usuario.saldo(ultimo_mes(gestor)), 0)


@pendiente_de("Integrante 3")
def opcion_que_comprar(gestor):
    from src import optimizacion
    optimizacion.mochila([], 0)                         # prueba rápida: ¿ya está implementado?
    deseos = datos.cargar_deseos()
    if not deseos:
        print("\n  No hay deseos en data/processed/lista_deseos.csv")
        return
    sugerido = _presupuesto_sugerido(gestor)
    presupuesto = pedir(f"  Presupuesto (Enter = {formato_moneda(sugerido)}): ",
                        datos.validar_monto, por_defecto=sugerido)
    elegidos, prioridad, sobrante = optimizacion.mochila(deseos, presupuesto)
    print(f"\n  Con {formato_moneda(presupuesto)} te conviene comprar:")
    for d in elegidos:
        print(f"   - {d.nombre} ({formato_moneda(d.precio)}, prioridad {d.prioridad})")
    print(f"  Prioridad total: {prioridad} | Te sobran: {formato_moneda(sobrante)}")


@pendiente_de("Integrante 3")
def opcion_plan_ahorro(gestor):
    from src import optimizacion
    optimizacion.plan_ahorro_voraz(0, [])               # prueba rápida: ¿ya está implementado?
    metas = datos.cargar_metas()
    sugerido = _presupuesto_sugerido(gestor)
    sobrante = pedir(f"  Dinero para ahorrar (Enter = {formato_moneda(sugerido)}): ",
                     datos.validar_monto, por_defecto=sugerido)
    plan = optimizacion.plan_ahorro_voraz(sobrante, metas)
    print("\n  Plan de ahorro:")
    for meta, monto in plan.items():
        print(f"   - {meta:<20} {formato_moneda(monto)}")


@pendiente_de("Integrantes 3 y 4")
def opcion_consejo_ia(gestor):
    from src import analisis, asesor_ia
    resumen = analisis.resumen_para_ia(gestor.dataframe(), ultimo_mes(gestor))
    print("\n  Consultando a la IA...")
    print("\n" + asesor_ia.pedir_consejo(resumen))


def opcion_pagos(gestor):
    accion = elegir("Pagos programados:", ["Ver pendientes", "Programar uno nuevo",
                                           "Procesar los que ya vencieron", "Volver"])
    if accion == "Ver pendientes":
        pendientes = gestor.pagos.a_lista()
        if not pendientes:
            print("\n  No hay pagos pendientes.")
        for p in pendientes:
            print(f"   {p.fecha:%Y-%m-%d}  {formato_moneda(p.monto):>10}  {p.categoria:<15} {p.descripcion}")
    elif accion == "Programar uno nuevo":
        categoria = elegir("Categoría:", list(CATEGORIAS_GASTO))
        monto = pedir("  Monto en USD: ", datos.validar_monto)
        descripcion = input("  Descripción: ").strip() or categoria
        fecha = pedir("  Fecha del pago (AAAA-MM-DD): ", datos.validar_fecha)
        gestor.programar_pago(PagoProgramado(fecha, categoria, monto, descripcion))
        print("  ✓ Pago programado")
    elif accion == "Procesar los que ya vencieron":
        procesados = gestor.procesar_pagos()
        print(f"\n  ✓ Se registraron {len(procesados)} pago(s) como gastos.")


OPCIONES = {
    "1": ("Registrar ingreso o gasto", opcion_registrar),
    "2": ("Ver últimos movimientos", opcion_ver_ultimos),
    "3": ("Deshacer último movimiento", opcion_deshacer),
    "4": ("Ver movimientos ordenados", opcion_ordenar),
    "5": ("Resumen y gráficas", opcion_resumen),
    "6": ("¿Qué puedo comprar?", opcion_que_comprar),
    "7": ("Plan de ahorro", opcion_plan_ahorro),
    "8": ("Consejo de la IA", opcion_consejo_ia),
    "9": ("Pagos programados", opcion_pagos),
}


def mostrar_encabezado(gestor):
    u = gestor.usuario
    mes = ultimo_mes(gestor)
    print("\n" + "=" * 50)
    print("  FinanzApp - Tu presupuesto inteligente")
    print("=" * 50)
    print(f"  Movimientos: {len(u)}   |   Saldo total: {formato_moneda(u.saldo())}")
    if mes:
        print(f"  Último mes ({mes}): ingresos {formato_moneda(u.total_ingresos(mes))}"
              f" · gastos {formato_moneda(u.total_gastos(mes))}")
    print("-" * 50)
    for clave, (texto, _) in OPCIONES.items():
        print(f"  {clave}. {texto}")
    print("  0. Salir")


def ejecutar():
    gestor = GestorFinanzas()
    if len(gestor.pagos):
        print(f"\n  Tienes {len(gestor.pagos)} pago(s) programado(s). Revísalos en la opción 9.")
    while True:
        mostrar_encabezado(gestor)
        opcion = input("\n  Elige una opción: ").strip()
        if opcion == "0":
            print("\n  ¡Hasta luego! Tus datos están guardados.\n")
            break
        if opcion in OPCIONES:
            try:
                OPCIONES[opcion][1](gestor)
            except KeyboardInterrupt:
                print("\n  (operación cancelada)")
            input("\n  Presiona Enter para continuar...")
        else:
            print("  Opción no válida.")
