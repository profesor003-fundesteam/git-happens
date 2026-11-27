from src.modelos import Deseo, MetaAhorro

def mochila(deseos, presupuesto):
    # Si no hay deseos o no hay dinero, devolvemos vacío de inmediato
    if not deseos or presupuesto <= 0:
        return [], 0, round(max(0.0, float(presupuesto)), 2)

    # Convertimos dólares a centavos enteros para poder usarlos como índices en la tabla
    presupuesto_centavos = int(round(presupuesto * 100))
    precios_centavos = [int(round(deseo.precio * 100)) for deseo in deseos]
    cantidad_deseos = len(deseos)

    # Creamos la tabla llena de ceros:
    # - Filas: representan los deseos (desde 0 hasta cantidad_deseos)
    # - Columnas: representan el dinero disponible en centavos (desde 0 hasta presupuesto_centavos)
    tabla_prioridades = [
        [0] * (presupuesto_centavos + 1)
        for _ in range(cantidad_deseos + 1)
    ]

    # Llenamos la tabla evaluando cada deseo con cada posible monto de dinero
    for num_deseo in range(1, cantidad_deseos + 1):
        precio_actual = precios_centavos[num_deseo - 1]
        prioridad_actual = deseos[num_deseo - 1].prioridad

        for centavos in range(presupuesto_centavos + 1):
            # Si el artículo cuesta más que el dinero disponible en esta columna, no se puede comprar
            if precio_actual > centavos:
                tabla_prioridades[num_deseo][centavos] = tabla_prioridades[num_deseo - 1][centavos]
            else:
                # Comparamos qué nos da más prioridad: no comprarlo vs comprarlo
                prioridad_sin_comprar = tabla_prioridades[num_deseo - 1][centavos]
                prioridad_comprando = (
                    tabla_prioridades[num_deseo - 1][centavos - precio_actual]
                    + prioridad_actual
                )
                tabla_prioridades[num_deseo][centavos] = max(
                    prioridad_sin_comprar, prioridad_comprando
                )

    # Reconstruimos qué deseos se eligieron recorriendo la tabla hacia atrás
    deseos_elegidos = []
    num_deseo = cantidad_deseos
    centavos_restantes = presupuesto_centavos

    while num_deseo > 0:
        # Si el valor cambió respecto a la fila de arriba, significa que sí compramos este deseo
        if tabla_prioridades[num_deseo][centavos_restantes] != tabla_prioridades[num_deseo - 1][centavos_restantes]:
            deseos_elegidos.append(deseos[num_deseo - 1])
            centavos_restantes -= precios_centavos[num_deseo - 1]
        num_deseo -= 1

    # Invertimos la lista para que queden en el mismo orden del archivo original
    deseos_elegidos.reverse()

    # Calculamos los resultados finales
    prioridad_total = tabla_prioridades[cantidad_deseos][presupuesto_centavos]
    total_gastado = sum(deseo.precio for deseo in deseos_elegidos)
    sobrante = round(presupuesto - total_gastado, 2)

    return deseos_elegidos, prioridad_total, sobrante

def plan_ahorro_voraz(sobrante, metas):
    # Si no hay metas registradas, devolvemos un diccionario vacío
    if not metas:
        return {}

    # Ordenamos las metas de mayor a menor prioridad para llenar primero las más importantes
    metas_ordenadas = sorted(metas, key=lambda meta: meta.prioridad, reverse=True)

    plan_asignacion = {}
    dinero_disponible = max(0.0, float(sobrante))

    # Recorremos cada meta y le asignamos lo que alcance del dinero disponible
    for meta in metas_ordenadas:
        # Si alcanza, cubrimos todo el monto objetivo; si no, le damos lo que quede (o 0)
        monto_asignado = min(dinero_disponible, meta.monto_objetivo)
        plan_asignacion[meta.nombre] = round(monto_asignado, 2)

        # Restamos lo que acabamos de asignar para las siguientes metas
        dinero_disponible = round(dinero_disponible - monto_asignado, 2)

    return plan_asignacion

