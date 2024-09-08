import os
import time
import matplotlib.pyplot as plt
from openpyxl import Workbook
from distance_finder import dist, travel_times_matrix, calculate_total_distance
from feasibility import is_feasible
from file_reader import read_txt_file  # New import
from file_writer import save_to_excel  # New import


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

            next_customer = min(feasible_customers, key=lambda x: times[route[-1].index][x.index])
            if current_load + next_customer.q <= capacity:
                route.append(next_customer)
                current_load += next_customer.q
                customers.remove(next_customer)
            else:
                break

        route.append(depot)
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
