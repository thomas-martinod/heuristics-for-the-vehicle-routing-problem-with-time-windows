import os
import time
import math
import numpy as np
from scipy.sparse.csgraph import minimum_spanning_tree
from openpyxl import Workbook
from distance_finder import travel_times_matrix, calculate_total_distance
from file_reader import read_txt_file
from file_writer import save_to_excel
from visualization import save_routes_plot_in_folder
from reactive_grasp import reactive_grasp_route_selection  # New import


directory_path = 'VRPTW Instances'
output_filename = '1-constructive-heuristics/results/VRPTW_tm_GRASP.xlsx'


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


def vrptw_solver(directory_path, output_filename):
    wb = Workbook()
    wb.remove(wb.active)

    execution_times = []  # List to store execution times for each file

    for i in range(1, 19):  # Looping over the files from VRPTW1 to VRPTW18
        filename = f'{directory_path}/VRPTW{i}.txt'
        file_start_time = time.time()  # Start time for each file

        n, Q, nodes = read_txt_file(filename)
        times = travel_times_matrix(nodes)

        depot = nodes[0]
        customers = nodes[1:]

        # Calculate the lower bounds
        lb_routes = lower_bound_routes(customers, Q)
        lb_distance = lower_bound_mst(depot, customers, times)  # Using MST-based lower bound

        # Apply Reactive GRASP
        routes, best_distance = reactive_grasp_route_selection(nodes, Q, times)
        computation_time = (time.time() - file_start_time) * 1000  # Time in milliseconds
        execution_times.append(computation_time)  # Store the time in milliseconds

        # Calculate the GAP for number of routes and total distance, ensuring GAP is not negative
        actual_routes = len(routes)
        gap_routes = max(((actual_routes - lb_routes) / lb_routes) * 100 if lb_routes > 0 else 0, 0)
        gap_distance = max(((best_distance - lb_distance) / lb_distance) * 100 if lb_distance > 0 else 0, 0)

        # Print solution details
        print(f"Solution for {filename}:")
        print(f"  - Total Distance = {best_distance}")
        print(f"  - Lower Bound Distance (MST) = {lb_distance:.2f}")
        print(f"  - GAP Distance = {gap_distance:.2f}%")
        print(f"  - Actual Routes = {actual_routes}")
        print(f"  - Lower Bound Routes = {lb_routes}")
        print(f"  - GAP Routes = {gap_routes:.2f}%")
        print(f"  - Execution Time = {computation_time:.0f} ms\n")

        # Save Excel results
        sheet_name = f'VRPTW{i}'
        save_to_excel(wb, sheet_name, routes, best_distance, computation_time, times)

        # Save the figure in 'figures/grasp' folder
        save_routes_plot_in_folder(routes, f"{sheet_name}.png", folder='1-constructive-heuristics/figures/grasp')

    # Save the Excel workbook
    wb.save(output_filename)

    total_elapsed_time = sum(execution_times)  # Total time in milliseconds
    print(f"\nTotal execution time: {total_elapsed_time:.0f} ms")


# Call the solver
vrptw_solver(directory_path, output_filename)
