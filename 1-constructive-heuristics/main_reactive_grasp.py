import os
import time
import math
import numpy as np
from scipy.sparse.csgraph import minimum_spanning_tree  # Used for calculating the MST lower bound
from openpyxl import Workbook  # Used to write results to Excel
from distance_finder import distance_matrix_generator, calculate_total_distance  # Functions to handle travel distances
from file_reader import read_txt_file  # Function to read data from the problem instance files
from file_writer import save_to_excel  # Function to write results into an Excel file
from visualization import save_routes_plot_in_folder  # Function to visualize and save routes
from reactive_grasp import reactive_grasp_route_selection  # Import the GRASP algorithm function

# Directory where problem instances are located and where results will be stored
directory_path = 'VRPTW Instances'
output_filename = '1-constructive-heuristics/results/VRPTW_tm_GRASP.xlsx'  # Excel output file

# Function to calculate the lower bound for the number of routes based on total demand and vehicle capacity
def lower_bound_routes(customers, vehicle_capacity):
    """
    Calculate the lower bound on the number of routes based on total demand and vehicle capacity.
    :param customers: List of customer nodes, each with a demand attribute.
    :param vehicle_capacity: Maximum capacity of a single vehicle.
    :return: Lower bound on the number of routes (vehicles).
    """
    total_demand = sum(customer.q for customer in customers)  # Total demand of all customers
    return math.ceil(total_demand / vehicle_capacity)  # Lower bound on number of routes based on vehicle capacity

# Function to calculate the lower bound on total distance using Minimum Spanning Tree (MST)
def lower_bound_mst(depot, customers, distance_matrix):
    """
    Calculate the lower bound on the total distance using the Minimum Spanning Tree (MST).
    :param depot: The depot node (starting point for all routes).
    :param customers: List of customer nodes.
    :param distance_matrix: Precomputed matrix of distances between nodes.
    :return: Lower bound on the total distance using MST.
    """
    # Combine depot and customers to form a full graph
    nodes = [depot] + customers
    n = len(nodes)

    # Create a distance matrix for all nodes
    full_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            full_matrix[i, j] = distance_matrix[nodes[i].index][nodes[j].index]  # Fill matrix with distances

    # Compute the MST for the graph and sum its edges to get the lower bound distance
    mst = minimum_spanning_tree(full_matrix).toarray()
    mst_distance = mst.sum()  # Total MST distance

    return mst_distance  # Return the MST lower bound distance

# Function to solve the VRPTW using the Reactive GRASP approach
def vrptw_solver(directory_path, output_filename):
    wb = Workbook()  # Initialize a new Excel workbook
    wb.remove(wb.active)  # Remove the default empty sheet

    execution_times = []  # List to store execution times for each file

    # Loop through each problem instance (VRPTW1 to VRPTW18)
    for i in range(1, 19):
        filename = f'{directory_path}/VRPTW{i}.txt'  # Build the filename
        file_start_time = time.time()  # Start timing the execution

        # Read the number of customers (n), vehicle capacity (Q), and nodes from the file
        n, Q, nodes = read_txt_file(filename)
        times = distance_matrix_generator(nodes)  # Calculate travel time matrix

        depot = nodes[0]  # First node is the depot
        customers = nodes[1:]  # All other nodes are customers

        # Calculate lower bounds for routes and total distance
        lb_routes = lower_bound_routes(customers, Q)
        lb_distance = lower_bound_mst(depot, customers, times)  # MST-based lower bound

        # Apply the Reactive GRASP algorithm to find the best routes and total distance
        routes, best_distance = reactive_grasp_route_selection(nodes, Q, times)
        computation_time = (time.time() - file_start_time) * 1000  # Calculate execution time in milliseconds
        execution_times.append(computation_time)  # Store the execution time

        # Calculate the GAP for both routes and distances
        actual_routes = len(routes)  # Number of routes found
        gap_routes = max(((actual_routes - lb_routes) / lb_routes) * 100 if lb_routes > 0 else 0, 0)  # GAP for routes
        gap_distance = max(((best_distance - lb_distance) / lb_distance) * 100 if lb_distance > 0 else 0, 0)  # GAP for distances

        # Print solution details for this problem instance
        print(f"Solution for {filename}:")
        print(f"  - Total Distance = {best_distance}")
        print(f"  - Lower Bound Distance (MST) = {lb_distance:.3f}")
        print(f"  - GAP Distance = {gap_distance:.3f}%")
        print(f"  - Actual Routes = {actual_routes}")
        print(f"  - Lower Bound Routes = {lb_routes}")
        print(f"  - GAP Routes = {gap_routes:.3f}%")
        print(f"  - Execution Time = {computation_time:.0f} ms\n")

        # Save the results to Excel
        sheet_name = f'VRPTW{i}'  # Each sheet named according to the problem instance
        save_to_excel(wb, sheet_name, routes, best_distance, computation_time, times)

        # Save a plot of the routes to the figures folder
        save_routes_plot_in_folder(routes, f"{sheet_name}.png", folder='1-constructive-heuristics/figures/grasp')

    # Save the entire Excel workbook with all results
    wb.save(output_filename)

    # Print the total execution time for all instances
    total_elapsed_time = sum(execution_times)  # Sum the execution times
    print(f"\nTotal execution time: {total_elapsed_time:.0f} ms")


# Execute the VRPTW solver using Reactive GRASP
vrptw_solver(directory_path, output_filename)
