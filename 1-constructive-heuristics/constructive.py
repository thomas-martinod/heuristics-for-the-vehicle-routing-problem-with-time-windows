import os
import math
import numpy as np
from visualization import plot_routes  # Importamos la función de visualización

K_max = 30  # Máximo número de vehículos permitidos

class Node:
    def __init__(self, index, x, y, q, inf, sup, t_serv):
        self.index = index
        self.x = x
        self.y = y
        self.q = q  # Demanda
        self.inf = inf  # Inicio de ventana de tiempo
        self.sup = sup  # Fin de ventana de tiempo
        self.t_serv = t_serv  # Tiempo de servicio

def read_files(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

        first_line = lines[0].strip().split()
        n = int(first_line[0])
        Q = int(first_line[1])

        node_set = []

        for line in lines[1:]:
            parts = list(map(int, line.strip().split()))
            node = Node(parts[0], parts[1], parts[2], parts[3], parts[4], parts[5], parts[6])
            node_set.append(node)
    return n, Q, node_set

def dist(n1, n2):
    """Calcula la distancia euclidiana entre dos nodos."""
    return math.sqrt((n1.x - n2.x)**2 + (n1.y - n2.y)**2)

def organize_customer_list(nodes):
    """Organiza la lista de clientes en base a las ventanas de tiempo y el tiempo de servicio."""
    customers = [node for node in nodes if node.index != 0]
    customers.sort(key=lambda x: (x.inf, x.sup, -x.t_serv))
    return customers

def is_capacity_feasible(used_capacity, new_demand, Q):
    """Verifica si un vehículo tiene suficiente capacidad para aceptar el nuevo nodo."""
    return used_capacity + new_demand <= Q

def is_timewise_feasible(activity_ending_time, time_between_nodes, inf_new_node, sup_new_node, service_time_new):
    """Verifica si es factible llegar al nodo dentro de su ventana de tiempo."""
    starting_new_time = max(activity_ending_time + time_between_nodes, inf_new_node)
    return starting_new_time + service_time_new <= sup_new_node

def create_time_matrix(nodes):
    """Crea una matriz de tiempos entre todos los nodos."""
    n = len(nodes)
    times = np.zeros((n, n))  # Inicializamos una matriz de n x n
    for i in range(n):
        for j in range(n):
            times[i][j] = dist(nodes[i], nodes[j])  # Aquí estamos asumiendo que el tiempo es proporcional a la distancia
    return times



def create_routes(n, Q, nodes, times):
    """Crea rutas factibles para los vehículos respetando las restricciones de capacidad y tiempo."""
    aux = True
    total_demand = sum(node.q for node in nodes if node.index != 0)
    K_ini = math.ceil(total_demand / Q)

    for K in range(K_ini, K_max + 1):
        routes = [{'route': [nodes[0]], 'used_capacity': 0, 'last_arrival_time': 0, 'activity_ending_time': 0} for _ in range(K)]
        customer_list = organize_customer_list(nodes)

        for node in customer_list:
            available_routes = []

            # Revisar rutas factibles por capacidad y tiempo
            for route in routes:
                if is_capacity_feasible(route['used_capacity'], node.q, Q) and \
                   is_timewise_feasible(route['activity_ending_time'], times[route['route'][-1].index][node.index], 
                                        node.inf, node.sup, node.t_serv):
                    available_routes.append(route)

            # Si no hay rutas factibles, no es posible con K vehículos, incrementar K
            if not available_routes:
                aux = False
                break

            # Seleccionar la ruta con menor distancia al nodo
            best_route = min(available_routes, key=lambda r: dist(r['route'][-1], node))

            # Actualizar la ruta seleccionada
            travel_time = times[best_route['route'][-1].index][node.index]  # Usamos la matriz de tiempos
            arrival_time = max(best_route['activity_ending_time'] + travel_time, node.inf)
            best_route['route'].append(node)
            best_route['used_capacity'] += node.q  # Actualizamos la capacidad usada
            best_route['last_arrival_time'] = arrival_time  # Actualizamos el último tiempo de llegada
            best_route['activity_ending_time'] = arrival_time + node.t_serv  # Actualizamos el tiempo de servicio final

        # Si logramos encontrar rutas factibles para todos los nodos con K vehículos, retornamos las rutas
        if aux:
            return routes

    # Si llegamos a este punto, no es factible encontrar rutas con ningún K
    print("No se pudo encontrar una solución factible.")
    return None


def print_routes(routes):
    """Imprime las rutas generadas."""
    if routes is None:
        print("No hay rutas disponibles.")
    else:
        for i, route_data in enumerate(routes):
            route = route_data['route']
            route_str = ' -> '.join([str(node.index) for node in route])
            print(f"Ruta {i+1}: {route_str}")
        print()

def main(instance_path):
    """Función principal que ejecuta la lógica del VRPTW."""
    n, Q, nodes = read_files(instance_path)

    # Crear la matriz de tiempos
    times = create_time_matrix(nodes)

    # Generar las rutas
    routes = create_routes(n, Q, nodes, times)
    print_routes(routes)

    # Llamar a la función para graficar las rutas
    if routes is not None:
        plot_routes(routes)

# Cambia esta ruta a la ubicación de tu archivo
instance_path = "VRPTW Instances/VRPTW1.txt"
main(instance_path)
