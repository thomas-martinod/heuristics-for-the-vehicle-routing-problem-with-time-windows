import os
import time
import numpy as np
from openpyxl import Workbook
from distance_finder import travel_times_matrix, calculate_total_distance
from feasibility import is_feasible
from file_reader import read_txt_file
from file_writer import save_to_excel
from visualization import save_routes_plot_in_folder


# Parámetros del ACO
aco_params = {
    'num_ants': 50,       # Número de hormigas
    'num_iterations': 100, # Iteraciones
    'alpha': 1.5,          # Influencia de la feromona
    'beta': 2.0,           # Influencia de la distancia
    'rho': 0.7,            # Factor de evaporación de feromona
    'Q': 10.0              # Cantidad de feromona depositada
}


def initialize_pheromones(num_nodes, times):
    """
    Inicializa las feromonas según la matriz de tiempos.
    """
    pheromones = np.ones((num_nodes, num_nodes)) / (times + 1e-6)  # Feromonas inversamente proporcionales a la distancia
    return pheromones


def update_pheromones(pheromones, all_routes, Q, rho):
    """
    Actualiza las feromonas con evaporación y deposición.
    """
    pheromones *= (1 - rho)  # Evaporación
    for routes, distance in all_routes:
        for route in routes:
            for i in range(len(route) - 1):
                pheromones[route[i].index][route[i + 1].index] += Q / distance  # Incremento de feromonas


def aco_vrptw(nodes, capacity, times, num_ants, num_iterations, alpha, beta, rho, Q):
    """
    ACO para el problema VRPTW.
    """
    num_nodes = len(nodes)
    pheromones = initialize_pheromones(num_nodes, times)
    best_routes = None
    best_distance = float('inf')

    for iteration in range(num_iterations):
        all_routes = []
        for ant in range(num_ants):
            depot = nodes[0]
            customers = set(range(1, num_nodes))  # Índices de clientes
            routes = []

            while customers:
                route = [depot]
                current_load = 0

                while True:
                    # Clientes factibles para la hormiga
                    feasible_customers = [cust for cust in customers if is_feasible(route, nodes[cust], capacity, times)]
                    if not feasible_customers:
                        break

                    # Cálculo de probabilidades basado en feromonas y visibilidad
                    probabilities = []
                    for cust in feasible_customers:
                        pheromone = pheromones[route[-1].index][cust]
                        travel_time = times[route[-1].index][cust]
                        visibility = 1 / (travel_time if travel_time > 0 else 1e-6)
                        probabilities.append((pheromone ** alpha) * (visibility ** beta))

                    total_prob = sum(probabilities)
                    probabilities = np.array(probabilities) / total_prob if total_prob > 0 else np.ones(len(feasible_customers)) / len(feasible_customers)
                    
                    # Seleccionar el próximo cliente basado en probabilidades
                    next_customer_index = np.random.choice(feasible_customers, p=probabilities)
                    next_customer = nodes[next_customer_index]

                    if current_load + next_customer.q <= capacity:
                        route.append(next_customer)
                        current_load += next_customer.q
                        customers.remove(next_customer_index)
                    else:
                        break

                route.append(depot)  # El vehículo regresa al depósito
                routes.append(route)

            total_distance = sum(calculate_total_distance([route], times) for route in routes)
            all_routes.append((routes, total_distance))

            # Actualizar la mejor solución si es mejor que la actual
            if total_distance < best_distance:
                best_distance = total_distance
                best_routes = routes

        # Actualizar feromonas
        update_pheromones(pheromones, all_routes, Q, rho)

    return best_routes, best_distance


def vrptw_solver(directory_path, output_filename):
    """
    Solución ACO para VRPTW y guardado de resultados.
    """
    wb = Workbook()
    wb.remove(wb.active)

    execution_times = []  # Lista para guardar tiempos de ejecución

    for i in range(1, 19):  # Procesar archivos VRPTW1 a VRPTW18
        filename = f'{directory_path}/VRPTW{i}.txt'
        file_start_time = time.time()  # Tiempo de inicio

        # Leer nodos y calcular la matriz de tiempos
        n, Q, nodes = read_txt_file(filename)
        times = travel_times_matrix(nodes)

        # Aplicar ACO
        routes, best_distance = aco_vrptw(nodes, Q, times, **aco_params)
        computation_time = (time.time() - file_start_time) * 1000  # Tiempo en milisegundos
        execution_times.append(computation_time)

        # Mostrar detalles de la solución
        print(f"Solution for {filename}: Total Distance = {best_distance}, Execution Time = {computation_time:.0f} ms")

        # Guardar resultados en Excel
        sheet_name = f'VRPTW{i}'
        save_to_excel(wb, sheet_name, routes, best_distance, computation_time, times)

        # Guardar la figura de la solución
        save_routes_plot_in_folder(routes, f"{sheet_name}.png", folder='1-constructive-heuristics/figures/ACO')

    # Guardar el archivo Excel
    wb.save(output_filename)

    total_elapsed_time = sum(execution_times)  # Tiempo total en milisegundos
    print(f"\nTotal execution time: {total_elapsed_time:.0f} ms")


# Ejecutar la solución ACO
output_filename = '1-constructive-heuristics/results/VRPTW_ACO.xlsx'
vrptw_solver('VRPTW Instances', output_filename)
