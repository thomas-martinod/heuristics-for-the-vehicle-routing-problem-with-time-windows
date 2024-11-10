import os
import time  # Used to measure execution time
import math  # Mathematical functions like ceiling
import numpy as np  # For numerical operations and matrix manipulation
from scipy.sparse.csgraph import minimum_spanning_tree  # To compute the minimum spanning tree (MST)
from openpyxl import Workbook  # To write results into Excel files
from distance_finder import distance_matrix_generator, calculate_total_distance  # Helper functions to compute distances
from feasibility import is_feasible  # Check feasibility of routes (capacity and time window constraints)
from file_reader import read_txt_file  # Read the input data files
from file_writer import save_to_excel  # Save results into an Excel file
from visualization import save_routes_plot_in_folder  # To generate and save visualizations of the routes

# Constants used for customer selection based on weighted criteria
c_distance = 0.5  # Weight for distance
c_inf = 0.4 # Weight for the lower time window bound (infeasible time)
c_sup = 0.1  # Weight for the upper time window bound

# Input and output file paths
instances_directory_path = r'C:\Users\thomm\Documents\GitHub\heuristica\VRPTW Instances'  # Directory with the VRPTW problem instances
output_filename = '1-constructive-heuristics/results/VRPTW_tm_constructive.xlsx'  # Output Excel file path


# Function to perform constructive route selection based on capacity and time windows
def constructive_route_selection(nodes, capacity, times):
    depot = nodes[0]  # The depot node (starting point and end point of all routes)
    customers = nodes[1:]  # All other nodes are customer nodes
    routes = []  # List to store the constructed routes

    while customers:  # While there are still customers to be served
        route = [depot]  # Start a new route from the depot
        current_load = 0  # Initialize the current load of the vehicle

        while True:
            # Find all feasible customers based on vehicle capacity and time windows
            feasible_customers = [cust for cust in customers if is_feasible(route, cust, capacity, times)]
            if not feasible_customers:
                break  # If no feasible customers, break out of the loop

            # Select the next customer using weighted criteria (distance, time window bounds)
            next_customer = min(feasible_customers, key=lambda x:
                c_distance * (times[route[-1].index][x.index]) +  # Minimize distance
                c_inf * x.inf +  # Time window lower bound
                c_sup * x.sup)  # Time window upper bound

            # Check if adding the next customer exceeds the vehicle capacity
            if current_load + next_customer.q <= capacity:
                route.append(next_customer)  # Add the customer to the route
                current_load += next_customer.q  # Update the current load
                customers.remove(next_customer)  # Remove the customer from the list
            else:
                break  # Stop if capacity is exceeded

        route.append(depot)  # Return to the depot at the end of the route
        routes.append(route)  # Add the route to the list of routes

    return routes  # Return the constructed routes

# Main function to solve the VRPTW using the constructive heuristic method
def vrptw_solver(directory_path, output_filename):
    wb = Workbook()  # Initialize a new Excel workbook
    wb.remove(wb.active)  # Remove the default empty sheet

    execution_times = []  # List to store execution times for each instance
    gaps_k = []  # List to store gaps for number of routes (K)
    gaps_d = []  # List to store gaps for distances (D)

    # Loop over all problem instances from VRPTW1 to VRPTW18
    for i in range(1, 19):
        filename = f'{directory_path}/VRPTW{i}.txt'  # Generate the file name for each instance
        file_start_time = time.time()  # Record the start time for each instance

        # Read the number of nodes, vehicle capacity, and nodes (customers) from the file
        n, Q, nodes = read_txt_file(filename)
        times = distance_matrix_generator(nodes)  # Calculate the travel time matrix

        depot = nodes[0]  # The depot node
        customers = nodes[1:]  # List of customer nodes

        # Calculate the lower bounds (for routes and total distance)
        lb_routes = lower_bound_routes(customers, Q)
        lb_distance = lower_bound_mst(depot, customers, times)  # Use MST to get the lower bound distance

        # Generate routes using the constructive heuristic method
        routes = constructive_route_selection(nodes, Q, times)
        best_distance = calculate_total_distance(routes, times)  # Calculate the total distance for the solution
        computation_time = (time.time() - file_start_time) * 1000  # Compute the execution time in milliseconds
        execution_times.append(computation_time)  # Store the execution time

        # Calculate the GAP for number of routes and total distance
        actual_routes = len(routes)
        gap_routes = max(((actual_routes - lb_routes) / lb_routes) * 100 if lb_routes > 0 else 0, 0)  # GAP for routes
        gap_distance = max(((best_distance - lb_distance) / lb_distance) * 100 if lb_distance > 0 else 0, 0)  # GAP for distance

        # Store the GAPs for calculating mean later
        gaps_k.append(gap_routes)
        gaps_d.append(gap_distance)

        # Print the solution details for this instance
        print(f"Solution for {filename}:")
        print(f"  - Total Distance = {best_distance}")
        print(f"  - Lower Bound Distance (MST) = {lb_distance:.3f}")
        print(f"  - GAP Distance = {gap_distance:.3f}%")
        print(f"  - Actual Routes = {actual_routes}")
        print(f"  - Lower Bound Routes = {lb_routes}")
        print(f"  - GAP Routes = {gap_routes:.3f}%")
        print(f"  - Execution Time = {computation_time:.3f} ms\n")

        # Save the results to Excel and plot the routes
        sheet_name = f'VRPTW{i}'  # Each sheet is named based on the instance
        save_to_excel(wb, sheet_name, routes, best_distance, computation_time, times)  # Save to Excel
        save_routes_plot_in_folder(routes, f"{sheet_name}.png", folder='1-constructive-heuristics/figures/constructive')  # Save the plot

    # Save the final Excel workbook with all the results
    wb.save(output_filename)

    # Calculate the total and mean execution times
    total_elapsed_time = sum(execution_times)  # Total time
    mean_gap_k = sum(gaps_k) / len(gaps_k)  # Mean GAP for routes
    mean_gap_d = sum(gaps_d) / len(gaps_d)  # Mean GAP for distances

    # Print total execution time and mean GAPs
    print(f"\nTotal execution time: {total_elapsed_time:.0f} ms")
    print(f"Mean GAP for routes (K): {mean_gap_k:.3f}%")
    print(f"Mean GAP for distances (D): {mean_gap_d:.3f}%")

# Run the solver function
vrptw_solver(instances_directory_path, output_filename)
