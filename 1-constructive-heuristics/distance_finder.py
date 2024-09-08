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

def calculate_min_max_times(nodes):
    # Obtener los valores mínimos y máximos de los límites inferiores (inf) y superiores (sup)
    min_inf = min(node.inf for node in nodes)
    max_inf = max(node.inf for node in nodes)
    min_sup = min(node.sup for node in nodes)
    max_sup = max(node.sup for node in nodes)
    return min_inf, max_inf, min_sup, max_sup

def calculate_min_max_distances(times):
    return min(min(row) for row in times), max(max(row) for row in times)