import os
import time
import math
import numpy as np
from scipy.sparse.csgraph import minimum_spanning_tree
from openpyxl import Workbook
from distance_finder import travel_times_matrix, calculate_total_distance
from feasibility import is_feasible
from file_reader import read_txt_file
from file_writer import save_to_excel
from visualization import save_routes_plot_in_folder


c_distance = 0.5
c_inf = 0.4
c_sup = 0.1

directory_path = 'VRPTW Instances'
output_filename = '1-constructive-heuristics/results/VRPTW_tm_constructive.xlsx'


def lower_bound_routes(customers, vehicle_capacity):
    """
    Calculate the lower bound on the number of routes based on total demand and vehicle capacity.
    :param customers: List of customer nodes, each with a demand attribute.
    :param vehicle_capacity: Maximum capacity of a single vehicle.
    :return: Lower bound on the number of routes (vehicles).
    """
    total_demand = sum(customer.q for customer in customers)
    return math.ceil(total_demand / vehicle_capacity)


def lower_bound_mst(depot, customers, distance_matrix):
    """
    Calculate the lower bound on the total distance using the Minimum Spanning Tree (MST).
    :param depot: The depot node (starting point for all routes).
    :param customers: List of customer nodes.
    :param distance_matrix: Precomputed matrix of distances between nodes.
    :return: Lower bound on the total distance using MST.
    """
    # Combine the depot and customer nodes to form a full graph
    nodes = [depot] + customers
    n = len(nodes)

    # Create a full distance matrix for all nodes
    full_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            full_matrix[i, j] = distance_matrix[nodes[i].index][nodes[j].index]

    # Compute the minimum spanning tree (MST) of the full graph
    mst = minimum_spanning_tree(full_matrix).toarray()

    # Sum of the edges in the MST gives the lower bound distance
    mst_distance = mst.sum()

    return mst_distance


def constructive_route_selection(nodes, capacity, times):
    depot = nodes[0]
    customers = nodes[1:]
    routes = []

    while customers:
        route = [depot]
        current_load = 0

        while True:
            feasible_customers = [cust for cust in customers if is_feasible(route, cust, capacity, times)]
            if not feasible_customers:
                break

            # Select the customer based on the weighted criteria
            next_customer = min(feasible_customers, key=lambda x:
                c_distance * (times[route[-1].index][x.index]) +  # Distance
                c_inf * x.inf +  # Time window lower bound
                c_sup * x.sup)  # Time window upper bound

            if current_load + next_customer.q <= capacity:
                route.append(next_customer)
                current_load += next_customer.q
                customers.remove(next_customer)
            else:
                break

        route.append(depot)  # Return to depot
        routes.append(route)

    return routes


def vrptw_solver(directory_path, output_filename):
    wb = Workbook()
    wb.remove(wb.active)

    execution_times = []  # Lista para guardar tiempos de ejecución de cada archivo

    for i in range(1, 19):  # Looping over the files from VRPTW1 to VRPTW18
        filename = f'{directory_path}/VRPTW{i}.txt'
        file_start_time = time.time()  # Start time for each file

        n, Q, nodes = read_txt_file(filename)  # Leer los nodos del archivo
        times = travel_times_matrix(nodes)  # Calcular los tiempos de viaje

        depot = nodes[0]
        customers = nodes[1:]

        # Calcular las cotas inferiores
        lb_routes = lower_bound_routes(customers, Q)
        lb_distance = lower_bound_mst(depot, customers, times)  # Usar MST para la cota inferior

        # Generar las rutas usando el método constructivo
        routes = constructive_route_selection(nodes, Q, times)
        best_distance = calculate_total_distance(routes, times)  # Calcular la distancia total
        computation_time = (time.time() - file_start_time) * 1000  # Tiempo en milisegundos
        execution_times.append(computation_time)  # Guardar el tiempo en milisegundos

        # Calcular el GAP para número de rutas y distancia total
        actual_routes = len(routes)
        gap_routes = max(((actual_routes - lb_routes) / lb_routes) * 100 if lb_routes > 0 else 0, 0)
        gap_distance = max(((best_distance - lb_distance) / lb_distance) * 100 if lb_distance > 0 else 0, 0)

        # Mostrar detalles de la solución
        print(f"Solution for {filename}:")
        print(f"  - Total Distance = {best_distance}")
        print(f"  - Lower Bound Distance (MST) = {lb_distance:.2f}")
        print(f"  - GAP Distance = {gap_distance:.2f}%")
        print(f"  - Actual Routes = {actual_routes}")
        print(f"  - Lower Bound Routes = {lb_routes}")
        print(f"  - GAP Routes = {gap_routes:.2f}%")
        print(f"  - Execution Time = {computation_time:.0f} ms\n")

        sheet_name = f'VRPTW{i}'
        save_to_excel(wb, sheet_name, routes, best_distance, computation_time, times)

        save_routes_plot_in_folder(routes, f"{sheet_name}.png", folder='1-constructive-heuristics/figures/constructive')

    # Guardar el archivo Excel
    wb.save(output_filename)

    total_elapsed_time = sum(execution_times)  # Tiempo total en milisegundos
    print(f"\nTotal execution time: {total_elapsed_time:.0f} ms")


# Ejecutar la función
vrptw_solver(directory_path, output_filename)