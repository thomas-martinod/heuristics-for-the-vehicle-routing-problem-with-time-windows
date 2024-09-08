import os
import time
import matplotlib.pyplot as plt
from openpyxl import Workbook
from distance_finder import travel_times_matrix, calculate_total_distance
from feasibility import is_feasible
from file_reader import read_txt_file  # New import
from file_writer import save_to_excel  # New import


c_distance = 0.5
c_inf = 0.25
c_sup = 0.25


def calculate_min_max_values(nodes, times):
    # Obtener los valores mínimos y máximos de las distancias (times)
    min_time = min(min(row) for row in times)
    max_time = max(max(row) for row in times)

    # Obtener los valores mínimos y máximos de los límites inferiores (inf) y superiores (sup)
    min_inf = min(node.inf for node in nodes)
    max_inf = max(node.inf for node in nodes)
    min_sup = min(node.sup for node in nodes)
    max_sup = max(node.sup for node in nodes)

    return min_time, max_time, min_inf, max_inf, min_sup, max_sup


def constructive_route_selection(nodes, capacity, times, c_distance=1.0, c_inf=1.0, c_sup=1.0):
    # Calcular los mínimos y máximos para normalizar
    min_time, max_time, min_inf, max_inf, min_sup, max_sup = calculate_min_max_values(nodes, times)
    
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

            # Normalización de las magnitudes y selección del cliente basado en la ponderación
            next_customer = min(feasible_customers, key=lambda x:
                c_distance * (times[route[-1].index][x.index] - min_time) / (max_time - min_time) +  # Normalizamos la distancia
                c_inf * (x.inf - min_inf) / (max_inf - min_inf) +  # Normalizamos el límite inferior
                c_sup * (x.sup - min_sup) / (max_sup - min_sup)    # Normalizamos el límite superior
            )

            if current_load + next_customer.demand <= capacity:
                route.append(next_customer)
                current_load += next_customer.demand
                customers.remove(next_customer)
            else:
                break

        route.append(depot)  # El vehículo regresa al depósito
        routes.append(route)

    return routes


def vrptw_solver(directory_path, output_filename):
    start_time = time.time()
    wb = Workbook()
    wb.remove(wb.active)
    for filename in os.listdir(directory_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(directory_path, filename)
            n, Q, nodes = read_txt_file(file_path)  # Now using the new function from file_reader.py
            times = travel_times_matrix(nodes)
            routes = constructive_route_selection(nodes, Q, times)
            best_distance = calculate_total_distance(routes, times)
            computation_time = time.time() - start_time
            print(f"Solution for {filename}: Total Distance = {best_distance}")
            sheet_name = filename.split('.')[0]
            save_to_excel(wb, sheet_name, routes, best_distance, computation_time, times)  # Now using the new function from file_writer.py
    wb.save(output_filename)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Tiempo total de ejecución: {elapsed_time:.4f} segundos")


directory_path = 'VRPTW Instances'
output_filename = "VRPTW_Constructive_Method.xlsx"
vrptw_solver(directory_path, output_filename)
