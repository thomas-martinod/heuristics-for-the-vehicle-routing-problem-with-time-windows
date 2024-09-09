import math
import numpy as np

# Calculate the Euclidean distance between two nodes n1 and n2
def dist(n1, n2):
    return math.sqrt((n1.x - n2.x) ** 2 + (n1.y - n2.y) ** 2)

# Generate a matrix of travel times (or distances) between all nodes
def travel_times_matrix(nodes):
    n = len(nodes)
    travel_times = np.zeros((n, n))  # Initialize an empty matrix of size n x n
    for i in range(n):
        for j in range(n):
            travel_times[i][j] = dist(nodes[i], nodes[j])  # Compute distance between nodes i and j
    return travel_times

# Calculate the total distance of a single route, given the travel times matrix
def calculate_route_distance(route, times):
    distance = 0.0
    for i in range(len(route) - 1):
        distance += times[route[i].index][route[i + 1].index]  # Sum up distances between consecutive nodes in the route
    return distance

# Calculate the total distance for all routes
def calculate_total_distance(routes, times):
    return sum(calculate_route_distance(route, times) for route in routes)  # Sum up the distance of all routes

# Calculate the minimum and maximum time window bounds for all nodes
def calculate_min_max_times(nodes):
    min_inf = min(node.inf for node in nodes)  # Minimum lower bound of time windows
    max_inf = max(node.inf for node in nodes)  # Maximum lower bound of time windows
    min_sup = min(node.sup for node in nodes)  # Minimum upper bound of time windows
    max_sup = max(node.sup for node in nodes)  # Maximum upper bound of time windows
    return min_inf, max_inf, min_sup, max_sup

# Calculate the minimum and maximum distances between nodes from the travel time matrix
def calculate_min_max_distances(times):
    return min(min(row) for row in times), max(max(row) for row in times)  # Return minimum and maximum values from the matrix
