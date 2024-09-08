import math
import numpy as np

def dist(n1, n2):
    return math.sqrt((n1.x - n2.x) ** 2 + (n1.y - n2.y) ** 2)

def travel_times_matrix(nodes):
    n = len(nodes)
    travel_times = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            travel_times[i][j] = dist(nodes[i], nodes[j])
    return travel_times

def calculate_route_distance(route, times):
    distance = 0.0
    for i in range(len(route) - 1):
        distance += times[route[i].index][route[i + 1].index]
    return distance

def calculate_total_distance(routes, times):
    return sum(calculate_route_distance(route, times) for route in routes)
