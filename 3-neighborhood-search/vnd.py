import time
from distance_finder import calculate_total_distance, calculate_route_distance
from feasibility import is_feasible


def swap_between_routes(routes, times, capacity):
    import random
    new_routes = [route.copy() for route in routes]

    if len(new_routes) < 2:
        return new_routes  # No hay suficientes rutas para intercambiar

    route_indices = list(range(len(new_routes)))
    random.shuffle(route_indices)

    for i in route_indices:
        for j in route_indices:
            if i >= j:
                continue  # Evitar duplicados y misma ruta

            route1 = new_routes[i]
            route2 = new_routes[j]

            # Excluir los depósitos
            customers1 = route1[1:-1]
            customers2 = route2[1:-1]

            for idx1, cust1 in enumerate(customers1):
                for idx2, cust2 in enumerate(customers2):
                    # Crear copias de las rutas
                    temp_route1 = route1.copy()
                    temp_route2 = route2.copy()

                    # Intercambiar los clientes
                    temp_route1[idx1 + 1] = cust2  # +1 por el depósito al inicio
                    temp_route2[idx2 + 1] = cust1

                    # Verificar factibilidad de ambas rutas utilizando is_feasible
                    if (is_feasible(temp_route1, capacity, times) and
                        is_feasible(temp_route2, capacity, times)):
                        # Reemplazar las rutas originales
                        new_routes[i] = temp_route1
                        new_routes[j] = temp_route2
                        return new_routes  # Retornar después de la primera mejora
    return new_routes  # Si no se encontraron mejoras


def or_opt_within_route_single(route, times, capacity):
    best_route = route.copy()
    best_distance = calculate_route_distance(best_route, times)
    n = len(route)
    improved = False

    for segment_size in range(1, 4):
        for i in range(1, n - segment_size - 1):
            segment = route[i:i+segment_size]
            rest_route = route[:i] + route[i+segment_size:]

            for j in range(1, len(rest_route)):
                new_route = rest_route[:j] + segment + rest_route[j:]
                if is_feasible(new_route, capacity, times):
                    new_distance = calculate_route_distance(new_route, times)
                    if new_distance + 1e-6 < best_distance:
                        best_route = new_route
                        best_distance = new_distance
                        improved = True
                        return best_route, best_distance, improved  # Salir inmediatamente
    return best_route, best_distance, improved


def relocate_between_routes(routes, times, capacity):
    import random
    new_routes = [route.copy() for route in routes]

    if len(new_routes) < 2:
        return new_routes  # No hay suficientes rutas para reubicar

    route_indices = list(range(len(new_routes)))
    random.shuffle(route_indices)

    for i in route_indices:
        for j in route_indices:
            if i == j:
                continue  # No reubicar en la misma ruta

            route_from = new_routes[i]
            route_to = new_routes[j]

            # Excluir los depósitos
            customers_from = route_from[1:-1]

            for idx_cust, cust in enumerate(customers_from):
                # Crear copias de las rutas
                temp_route_from = route_from.copy()
                temp_route_to = route_to.copy()

                # Remover el cliente de la ruta origen
                del temp_route_from[idx_cust + 1]  # +1 por el depósito al inicio

                # Intentar insertar el cliente en todas las posiciones de la ruta destino
                for k in range(1, len(temp_route_to)):  # Evitar posición 0 (depósito)
                    temp_route_to_insert = temp_route_to[:k] + [cust] + temp_route_to[k:]

                    # Verificar factibilidad de ambas rutas utilizando is_feasible
                    if (is_feasible(temp_route_from, capacity, times) and
                        is_feasible(temp_route_to_insert, capacity, times)):
                        # Reemplazar las rutas originales
                        new_routes[i] = temp_route_from
                        new_routes[j] = temp_route_to_insert
                        return new_routes  # Retornar después de la primera mejora
    return new_routes  # Si no se encontraron mejoras

def two_opt_within_route(routes, times, capacity):
    new_routes = [route.copy() for route in routes]

    for idx, route in enumerate(new_routes):
        best_distance = calculate_route_distance(route, times)
        best_route = route.copy()
        improved = False

        for i in range(1, len(route) - 2):
            for j in range(i + 1, len(route) - 1):
                new_route = route[:i] + route[i:j+1][::-1] + route[j+1:]

                # Verificar factibilidad utilizando is_feasible
                if is_feasible(new_route, capacity, times):
                    new_distance = calculate_route_distance(new_route, times)
                    if new_distance + 1e-6 < best_distance:
                        best_distance = new_distance
                        best_route = new_route
                        improved = True

        if improved:
            new_routes[idx] = best_route
            return new_routes  # Retornar después de la primera mejora

    return new_routes  # Si no se encontraron mejoras

def two_opt_within_route_single(route, times, capacity):
    best_route = route.copy()
    best_distance = calculate_route_distance(best_route, times)
    n = len(route)
    improved = False

    for i in range(1, n - 2):
        for j in range(i + 1, n - 1):
            new_route = route[:i] + route[i:j+1][::-1] + route[j+1:]
            if is_feasible(new_route, capacity, times):
                new_distance = calculate_route_distance(new_route, times)
                if new_distance + 1e-6 < best_distance:
                    best_route = new_route
                    best_distance = new_distance
                    improved = True
    return best_route, best_distance, improved

def two_opt_across_routes(routes, times, capacity):
    best_routes = [route.copy() for route in routes]
    best_distance = calculate_total_distance(best_routes, times)
    improved = False

    for i in range(len(routes)):
        for j in range(i + 1, len(routes)):
            route1 = routes[i]
            route2 = routes[j]

            for idx1 in range(1, len(route1) - 1):
                for idx2 in range(1, len(route2) - 1):
                    new_route1 = route1[:idx1] + route2[idx2:]
                    new_route2 = route2[:idx2] + route1[idx1:]

                    if (is_feasible(new_route1, capacity, times) and
                        is_feasible(new_route2, capacity, times)):
                        temp_routes = routes.copy()
                        temp_routes[i] = new_route1
                        temp_routes[j] = new_route2
                        temp_distance = calculate_total_distance(temp_routes, times)
                        if temp_distance + 1e-6 < best_distance:
                            best_routes = temp_routes
                            best_distance = temp_distance
                            improved = True
    return best_routes, best_distance, improved


def swap_between_routes_best(routes, times, capacity):
    best_routes = [route.copy() for route in routes]
    best_distance = calculate_total_distance(best_routes, times)
    improved = False

    for i in range(len(routes)):
        for j in range(i + 1, len(routes)):
            route1 = routes[i]
            route2 = routes[j]

            customers1 = route1[1:-1]
            customers2 = route2[1:-1]

            for idx1, cust1 in enumerate(customers1):
                for idx2, cust2 in enumerate(customers2):
                    temp_route1 = route1.copy()
                    temp_route2 = route2.copy()

                    temp_route1[idx1 + 1] = cust2
                    temp_route2[idx2 + 1] = cust1

                    if (is_feasible(temp_route1, capacity, times) and
                        is_feasible(temp_route2, capacity, times)):
                        temp_routes = routes.copy()
                        temp_routes[i] = temp_route1
                        temp_routes[j] = temp_route2
                        temp_distance = calculate_total_distance(temp_routes, times)
                        if temp_distance + 1e-6 < best_distance:
                            best_routes = temp_routes
                            best_distance = temp_distance
                            improved = True
    return best_routes, best_distance, improved

def relocate_between_routes_best(routes, times, capacity):
    """
    Función mejorada para reubicar clientes entre rutas de manera más agresiva.
    Intenta mover secuencias de clientes de una ruta a otra.
    """
    best_routes = [route.copy() for route in routes]
    best_distance = calculate_total_distance(best_routes, times)
    improved = False

    for i in range(len(routes)):
        for j in range(len(routes)):
            if i == j:
                continue

            route_from = routes[i]
            route_to = routes[j]

            customers_from = route_from[1:-1]

            # Intentar mover secuencias de diferentes tamaños
            for seq_length in range(1, len(customers_from) + 1):
                for idx_cust in range(len(customers_from) - seq_length + 1):
                    segment = customers_from[idx_cust:idx_cust + seq_length]

                    temp_route_from = route_from[:idx_cust + 1] + route_from[idx_cust + seq_length + 1:]
                    if not is_feasible(temp_route_from, capacity, times):
                        continue

                    for k in range(1, len(route_to)):
                        temp_route_to = route_to[:k] + segment + route_to[k:]
                        if is_feasible(temp_route_to, capacity, times):
                            temp_routes = routes.copy()
                            temp_routes[i] = temp_route_from
                            temp_routes[j] = temp_route_to
                            temp_distance = calculate_total_distance(temp_routes, times)
                            if temp_distance + 1e-6 < best_distance:
                                best_routes = temp_routes
                                best_distance = temp_distance
                                improved = True
    return best_routes, best_distance, improved


def vnd_algorithm(routes, times, capacity, time_limit, start_time):
    """
    Algoritmo VND con criterio de parada basado en tiempo.
    """
    best_routes = [route.copy() for route in routes]
    best_distance = calculate_total_distance(best_routes, times)
    neighborhoods = [
        two_opt_within_route_single,
        or_opt_within_route_single,
        swap_between_routes_best,
        relocate_between_routes_best,
        two_opt_across_routes,
        merge_routes
    ]

    neighborhood_index = 0

    while neighborhood_index < len(neighborhoods):
        current_time = time.time()
        elapsed_time = current_time - start_time
        if elapsed_time >= time_limit:
            # Tiempo límite alcanzado, terminar
            break

        neighborhood = neighborhoods[neighborhood_index]
        improved = False

        if neighborhood in [two_opt_within_route_single, or_opt_within_route_single]:
            # Aplicar movimientos dentro de rutas individuales
            for idx, route in enumerate(best_routes):
                new_route, new_distance, route_improved = neighborhood(route, times, capacity)
                if route_improved and new_distance + 1e-6 < calculate_route_distance(best_routes[idx], times):
                    best_routes[idx] = new_route
                    best_distance = calculate_total_distance(best_routes, times)
                    improved = True

                    # Verificar el tiempo después de cada mejora
                    current_time = time.time()
                    elapsed_time = current_time - start_time
                    if elapsed_time >= time_limit:
                        break
            if elapsed_time >= time_limit:
                break
        else:
            if neighborhood == merge_routes:
                new_routes = neighborhood(best_routes, times, capacity)
                new_distance = calculate_total_distance(new_routes, times)
                neighborhood_improved = (len(new_routes) < len(best_routes) or new_distance + 1e-6 < best_distance)
            else:
                new_routes, new_distance, neighborhood_improved = neighborhood(best_routes, times, capacity)

            if neighborhood_improved and (new_distance + 1e-6 < best_distance or len(new_routes) < len(best_routes)):
                best_routes = [route.copy() for route in new_routes]
                best_distance = new_distance
                improved = True

                # Verificar el tiempo después de cada mejora
                current_time = time.time()
                elapsed_time = current_time - start_time
                if elapsed_time >= time_limit:
                    break

        if improved:
            # Continuar con el mismo vecindario
            neighborhood_index = 0
        else:
            # Pasar al siguiente vecindario
            neighborhood_index += 1

    return best_routes


def merge_routes(routes, times, capacity):
    """
    Función mejorada para fusionar rutas de manera más agresiva.
    Intenta fusionar rutas considerando todos los pares posibles y las inversiones de rutas.
    """
    improved = True
    while improved:
        improved = False
        num_routes = len(routes)
        best_distance = calculate_total_distance(routes, times)
        best_routes = routes.copy()

        for i in range(num_routes):
            for j in range(num_routes):
                if i >= j:
                    continue

                route1 = routes[i]
                route2 = routes[j]

                # Intentar fusionar route1 y route2 directamente
                merged_route = route1[:-1] + route2[1:]
                if is_feasible(merged_route, capacity, times):
                    temp_routes = [routes[k] for k in range(num_routes) if k != i and k != j]
                    temp_routes.append(merged_route)
                    temp_distance = calculate_total_distance(temp_routes, times)
                    if temp_distance + 1e-6 < best_distance or len(temp_routes) < len(best_routes):
                        best_routes = temp_routes
                        best_distance = temp_distance
                        improved = True
                        break

                # Intentar fusionar route1 y la inversión de route2
                reversed_route2 = [route2[0]] + route2[1:-1][::-1] + [route2[-1]]
                merged_route = route1[:-1] + reversed_route2[1:]
                if is_feasible(merged_route, capacity, times):
                    temp_routes = [routes[k] for k in range(num_routes) if k != i and k != j]
                    temp_routes.append(merged_route)
                    temp_distance = calculate_total_distance(temp_routes, times)
                    if temp_distance + 1e-6 < best_distance or len(temp_routes) < len(best_routes):
                        best_routes = temp_routes
                        best_distance = temp_distance
                        improved = True
                        break

            if improved:
                routes = best_routes
                break  # Reiniciar búsqueda desde el principio

    return routes
