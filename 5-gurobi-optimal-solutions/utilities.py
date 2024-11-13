# utilities.py
from gurobipy import GRB

def print_routes(model, x, locations, K, depot, nodes_dict):
    """
    Imprime las rutas óptimas si se encuentra una solución.
    """
    if model.status == GRB.OPTIMAL:
        routes = extract_routes(model, x, locations, K, depot, nodes_dict)
        for i, ruta in enumerate(routes, start=1):
            route_str = " -> ".join(str(node.index) for node in ruta)
            print(f"Ruta {i}: {route_str}")
    else:
        print("No se encontró solución óptima.")

# utilities.py

def extract_routes(model, x, locations, K, depot, nodes_dict):
    """
    Extrae las rutas a partir del modelo optimizado y devuelve una lista de rutas,
    donde cada ruta es una lista de objetos Node.
    """
    routes = []

    for k in range(1, K + 1):  # Iterar para cada vehículo
        ruta = []
        nodo_actual = depot
        visitados = set([depot])  # Comenzamos con el depósito como visitado

        while True:
            ruta.append(nodes_dict[nodo_actual])  # Agregar el nodo actual como objeto Node
            siguiente_nodo = None

            # Buscar el siguiente nodo en la ruta para el vehículo k
            for j in locations:
                if j != nodo_actual and (nodo_actual, j, k) in x and x[nodo_actual, j, k].X > 0.5:
                    siguiente_nodo = j
                    break

            if siguiente_nodo is None or siguiente_nodo in visitados:
                # Si no hay siguiente nodo o ya fue visitado, finalizar la ruta regresando al depósito
                ruta.append(nodes_dict[depot])  # Terminar la ruta en el depósito
                routes.append(ruta)  # Guardar la ruta completa para el vehículo k
                break

            # Marcar el nodo como visitado y avanzar al siguiente
            visitados.add(siguiente_nodo)
            nodo_actual = siguiente_nodo

    return routes



def extract_routes(model, x, locations, K, depot, nodes_dict):
    """
    Extrae las rutas a partir del modelo optimizado y devuelve una lista de rutas,
    donde cada ruta es una lista de objetos Node.
    """
    routes = []

    for k in range(1, K + 1):  # Iterar para cada vehículo
        ruta = []
        nodo_actual = depot
        visitados = set([depot])  # Comenzamos con el depósito como visitado

        while True:
            ruta.append(nodes_dict[nodo_actual])  # Agregar el nodo actual como objeto Node
            siguiente_nodo = None

            # Buscar el siguiente nodo en la ruta para el vehículo k
            for j in locations:
                if j != nodo_actual and (nodo_actual, j, k) in x and x[nodo_actual, j, k].X > 0.5:
                    siguiente_nodo = j
                    break

            if siguiente_nodo is None or siguiente_nodo in visitados:
                # Si no hay siguiente nodo o ya fue visitado, finalizar la ruta regresando al depósito
                ruta.append(nodes_dict[depot])  # Terminar la ruta en el depósito
                routes.append(ruta)  # Guardar la ruta completa para el vehículo k
                break

            # Marcar el nodo como visitado y avanzar al siguiente
            visitados.add(siguiente_nodo)
            nodo_actual = siguiente_nodo

    return routes

