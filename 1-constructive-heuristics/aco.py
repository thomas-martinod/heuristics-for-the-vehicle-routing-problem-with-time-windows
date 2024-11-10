import os
import time
import math
import numpy as np
from scipy.sparse.csgraph import minimum_spanning_tree
from openpyxl import Workbook
from distance_finder import distance_matrix_generator, calculate_total_distance
from feasibility import is_feasible
from file_reader import read_txt_file
from file_writer import save_to_excel
from visualization import save_routes_plot_in_folder


output_filename = '1-constructive-heuristics/results/VRPTW_th_ACO.xlsx'  # Output file path for storing results

# ACO parameters
aco_params = {
    'num_ants': 50,       # Number of ants used in each iteration
    'num_iterations': 100, # Total number of iterations to be performed
    'alpha': 1.5,          # Influence of the pheromone on decision making
    'beta': 2.0,           # Influence of the distance (visibility) on decision making
    'rho': 0.7,            # Evaporation factor for pheromones
    'Q': 10.0              # Amount of pheromone deposited by ants after finding a solution
}

def lower_bound_routes(customers, vehicle_capacity):
    """
    Calculate the lower bound for the number of routes based on total demand and vehicle capacity.
    :param customers: List of customers with demand.
    :param vehicle_capacity: Maximum capacity of the vehicle.
    :return: Minimum number of routes needed.
    """
    total_demand = sum(customer.q for customer in customers)  # Sum the demand of all customers
    return math.ceil(total_demand / vehicle_capacity)  # Divide total demand by vehicle capacity to get the minimum routes

def lower_bound_mst(depot, customers, distance_matrix):
    """
    Calculate the lower bound on the total distance using the Minimum Spanning Tree (MST) method.
    :param depot: Depot node (starting point for all routes).
    :param customers: List of customer nodes.
    :param distance_matrix: Matrix of distances between nodes.
    :return: Lower bound on the total distance.
    """
    nodes = [depot] + customers  # Combine depot and customers
    n = len(nodes)
    full_matrix = np.zeros((n, n))  # Create a full distance matrix
    for i in range(n):
        for j in range(n):
            full_matrix[i, j] = distance_matrix[nodes[i].index][nodes[j].index]  # Populate distance matrix between nodes
    
    # Calculate the Minimum Spanning Tree (MST) from the distance matrix
    mst = minimum_spanning_tree(full_matrix).toarray()
    mst_distance = mst.sum()  # Sum the edges in the MST to get the lower bound distance
    
    return mst_distance  # Return the total MST distance

def initialize_pheromones(num_nodes, times):
    """
    Initialize pheromones based on the travel times between nodes.
    :param num_nodes: Total number of nodes (depot + customers).
    :param times: Matrix of travel times between nodes.
    :return: Initialized pheromone matrix.
    """
    pheromones = np.ones((num_nodes, num_nodes)) / (times + 1e-6)  # Initialize pheromones inversely proportional to the distance
    return pheromones

def update_pheromones(pheromones, all_routes, Q, rho):
    """
    Update pheromones with evaporation and deposition.
    :param pheromones: Current pheromone matrix.
    :param all_routes: All routes found in the current iteration.
    :param Q: Constant controlling pheromone deposition.
    :param rho: Evaporation rate for pheromones.
    """
    pheromones *= (1 - rho)  # Evaporate pheromones by multiplying by (1 - rho)
    for routes, distance in all_routes:
        for route in routes:
            for i in range(len(route) - 1):
                # Increase pheromone between consecutive nodes on the route
                pheromones[route[i].index][route[i + 1].index] += Q / distance

def aco_vrptw(nodes, capacity, times, num_ants, num_iterations, alpha, beta, rho, Q):
    """
    Ant Colony Optimization (ACO) algorithm for VRPTW.
    :param nodes: List of nodes (depot + customers).
    :param capacity: Vehicle capacity.
    :param times: Matrix of travel times between nodes.
    :param num_ants: Number of ants.
    :param num_iterations: Number of iterations.
    :param alpha: Weight of pheromones.
    :param beta: Weight of distances (visibility).
    :param rho: Pheromone evaporation rate.
    :param Q: Amount of pheromone deposited by ants.
    :return: Best routes found and their total distance.
    """
    num_nodes = len(nodes)
    pheromones = initialize_pheromones(num_nodes, times)  # Initialize pheromone matrix
    best_routes = None
    best_distance = float('inf')  # Start with the best distance as infinity

    for iteration in range(num_iterations):  # Repeat for the specified number of iterations
        all_routes = []
        for ant in range(num_ants):  # Each ant finds a solution
            depot = nodes[0]
            customers = set(range(1, num_nodes))  # Set of customer indices (excluding depot)
            routes = []

            while customers:  # While there are still customers left to visit
                route = [depot]
                current_load = 0

                while True:
                    # Find feasible customers based on vehicle capacity and time windows
                    feasible_customers = [cust for cust in customers if is_feasible(route, nodes[cust], capacity, times)]
                    if not feasible_customers:
                        break

                    # Calculate probabilities based on pheromone levels and visibility (distance)
                    probabilities = []
                    for cust in feasible_customers:
                        pheromone = pheromones[route[-1].index][cust]
                        travel_time = times[route[-1].index][cust]
                        visibility = 1 / (travel_time if travel_time > 0 else 1e-6)  # Avoid division by zero
                        probabilities.append((pheromone ** alpha) * (visibility ** beta))

                    total_prob = sum(probabilities)
                    # Normalize probabilities or choose uniformly if all probabilities are zero
                    probabilities = np.array(probabilities) / total_prob if total_prob > 0 else np.ones(len(feasible_customers)) / len(feasible_customers)

                    # Randomly select the next customer based on the calculated probabilities
                    next_customer_index = np.random.choice(feasible_customers, p=probabilities)
                    next_customer = nodes[next_customer_index]

                    # Check if adding the next customer exceeds the vehicle's capacity
                    if current_load + next_customer.q <= capacity:
                        route.append(next_customer)
                        current_load += next_customer.q
                        customers.remove(next_customer_index)  # Remove the customer from the list
                    else:
                        break

                route.append(depot)  # Return to the depot at the end of the route
                routes.append(route)

            total_distance = sum(calculate_total_distance([route], times) for route in routes)  # Calculate the total distance for all routes
            all_routes.append((routes, total_distance))

            # Update the best solution if this one is better
            if total_distance < best_distance:
                best_distance = total_distance
                best_routes = routes

        # Update pheromone levels after all ants have finished
        update_pheromones(pheromones, all_routes, Q, rho)

    return best_routes, best_distance  # Return the best routes and distance

def vrptw_solver(directory_path, output_filename):
    """
    ACO-based solution for VRPTW with lower bound and GAP calculation, and saves results.
    :param directory_path: Path to the input files.
    :param output_filename: Path to save the output results (Excel file).
    """
    wb = Workbook()  # Initialize the Excel workbook
    wb.remove(wb.active)

    execution_times = []  # List to store the execution time for each instance

    for i in range(1, 19):  # Loop through all instances from VRPTW1 to VRPTW18
        filename = f'{directory_path}/VRPTW{i}.txt'
        file_start_time = time.time()  # Start timing the computation for this instance

        # Read the instance file and calculate the travel times
        n, Q, nodes = read_txt_file(filename)
        times = distance_matrix_generator(nodes)

        depot = nodes[0]
        customers = nodes[1:]

        # Calculate lower bounds for routes and distance
        lb_routes = lower_bound_routes(customers, Q)
        lb_distance = lower_bound_mst(depot, customers, times)

        # Apply ACO to find the best routes and distance
        routes, best_distance = aco_vrptw(nodes, Q, times, **aco_params)
        computation_time = (time.time() - file_start_time) * 1000  # Execution time in milliseconds
        execution_times.append(computation_time)

        # Calculate the GAP for the number of routes and distance
        actual_routes = len(routes)
        gap_routes = max(((actual_routes - lb_routes) / lb_routes) * 100 if lb_routes > 0 else 0, 0)
        gap_distance = max(((best_distance - lb_distance) / lb_distance) * 100 if lb_distance > 0 else 0, 0)

        # Print the solution details
        print(f"Solution for {filename}:")
        print(f"  - Total Distance = {best_distance}")
        print(f"  - Lower Bound Distance (MST) = {lb_distance:.2f}")
        print(f"  - GAP Distance = {gap_distance:.2f}%")
        print(f"  - Actual Routes = {actual_routes}")
        print(f"  - Lower Bound Routes = {lb_routes}")
        print(f"  - GAP Routes = {gap_routes:.2f}%")
        print(f"  - Execution Time = {computation_time:.0f} ms\n")

        # Save results to Excel
        sheet_name = f'VRPTW{i}'
        save_to_excel(wb, sheet_name, routes, best_distance, computation_time, times)

        # Save the plot of routes
        save_routes_plot_in_folder(routes, f"{sheet_name}.png", folder='1-constructive-heuristics/figures/aco')

    # Save the Excel workbook with all results
    wb.save(output_filename)

    total_elapsed_time = sum(execution_times)  # Calculate total execution time
    print(f"\nTotal execution time: {total_elapsed_time:.0f} ms")  # Display total execution time


# Execute the ACO solution with lower bound and GAP calculation
vrptw_solver('VRPTW Instances', output_filename)
