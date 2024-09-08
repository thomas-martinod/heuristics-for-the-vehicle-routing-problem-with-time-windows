import numpy as np
import random
import math
import time
from openpyxl import Workbook

# Definimos la estructura de un nodo
class Nodo:
    def __init__(self, index, x_cord, y_cord, demand, inflim, suplim, serv):
        self.index = index
        self.x_cord = x_cord
        self.y_cord = y_cord
        self.demand = demand
        self.time_window = (inflim, suplim)
        self.serv_time = serv

    def __repr__(self):
        return f"Customer <{self.index}>"

# Cálculo de distancia euclidiana entre dos nodos
def euclidean_distance(node1, node2):
    return round(math.sqrt((node1.x_cord - node2.x_cord) ** 2 + (node1.y_cord - node2.y_cord) ** 2), 3)

# Cálculo de matriz de tiempos
def calculate_travel_times(nodes):
    n = len(nodes)
    times = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            times[i][j] = euclidean_distance(nodes[i], nodes[j])
    return times

# Verificación de la factibilidad de agregar un nodo a la ruta
def is_feasible(route, new_node, capacity, times):
    total_demand = sum(node.demand for node in route) + new_node.demand
    if total_demand > capacity:
        return False

    current_time = 0
    for i in range(1, len(route)):
        current_time += times[route[i-1].index][route[i].index]
        if current_time < route[i].time_window[0]:
            current_time = route[i].time_window[0]
        if current_time > route[i].time_window[1]:
            return False
        current_time += route[i].serv_time
    return True

# Hormiga
class Ant:
    def __init__(self, graph, start_node):
        self.graph = graph
        self.start_node = start_node
        self.current_node = start_node
        self.travel_path = [start_node]
        self.total_travel_distance = 0
        self.index_to_visit = list(range(1, graph.node_count))  # Excluimos el depósito

    def move_to_next_index(self, next_index):
        self.travel_path.append(self.graph.nodes[next_index])
        self.total_travel_distance += self.graph.times[self.current_node.index][next_index]
        self.current_node = self.graph.nodes[next_index]
        if next_index in self.index_to_visit:
            self.index_to_visit.remove(next_index)

    def index_to_visit_empty(self):
        return len(self.index_to_visit) == 0

# Grafo con nodos, matriz de tiempos y feromonas
class VrptwGraph:
    def __init__(self, nodes, vehicle_capacity):
        self.nodes = nodes
        self.vehicle_capacity = vehicle_capacity
        self.node_count = len(nodes)
        self.times = calculate_travel_times(nodes)
        self.pheromone_mat = np.ones((self.node_count, self.node_count))

    def local_update_pheromone(self, i, j):
        self.pheromone_mat[i][j] = (1 - 0.1) * self.pheromone_mat[i][j] + 0.1 * (1 / self.times[i][j])

    def global_update_pheromone(self, path, distance):
        for i in range(len(path) - 1):
            self.pheromone_mat[path[i].index][path[i+1].index] = (1 - 0.1) * self.pheromone_mat[path[i].index][path[i+1].index] + 0.1 * (1 / distance)

# ACO para VRPTW
class MultipleAntColonySystem:
    def __init__(self, graph, ants_num=10, beta=1, q0=0.1):
        self.graph = graph
        self.ants_num = ants_num
        self.beta = beta
        self.q0 = q0
        self.best_path = None
        self.best_distance = float('inf')

    def run(self, iterations=100):
        for iteration in range(iterations):
            ants = [Ant(self.graph, self.graph.nodes[0]) for _ in range(self.ants_num)]

            for ant in ants:
                while not ant.index_to_visit_empty():
                    feasible_nodes = [node for node in ant.index_to_visit if is_feasible(ant.travel_path, self.graph.nodes[node], self.graph.vehicle_capacity, self.graph.times)]
                    if not feasible_nodes:
                        break
                    
                    transition_prob = self.calculate_transition_prob(ant, feasible_nodes)
                    
                    if np.random.rand() < self.q0:
                        next_node = feasible_nodes[np.argmax(transition_prob)]
                    else:
                        next_node = self.stochastic_accept(feasible_nodes, transition_prob)
                    
                    ant.move_to_next_index(next_node)
                    self.graph.local_update_pheromone(ant.current_node.index, next_node)

                if ant.index_to_visit_empty() and ant.total_travel_distance < self.best_distance:
                    self.best_path = ant.travel_path
                    self.best_distance = ant.total_travel_distance
                    self.graph.global_update_pheromone(self.best_path, self.best_distance)

        return self.best_path, self.best_distance

    def calculate_transition_prob(self, ant, feasible_nodes):
        closeness = [1 / self.graph.times[ant.current_node.index][node] for node in feasible_nodes]
        pheromone = [self.graph.pheromone_mat[ant.current_node.index][node] for node in feasible_nodes]
        total = np.array(pheromone) * np.array(closeness) ** self.beta
        return total / np.sum(total)

    @staticmethod
    def stochastic_accept(feasible_nodes, transition_prob):
        sum_prob = np.sum(transition_prob)
        norm_transition_prob = transition_prob / sum_prob
        while True:
            ind = int(len(feasible_nodes) * random.random())
            if random.random() <= norm_transition_prob[ind]:
                return feasible_nodes[ind]

# Función para resolver el VRPTW usando ACO
def vrptw_aco_solver(nodes, vehicle_capacity, ants_num=10, beta=1, q0=0.1, iterations=100):
    graph = VrptwGraph(nodes, vehicle_capacity)
    aco = MultipleAntColonySystem(graph, ants_num, beta, q0)
    best_path, best_distance = aco.run(iterations)
    return best_path, best_distance

# Ejemplo de ejecución
def main():
    nodes = [
        Nodo(0, 0, 0, 0, 0, 100, 0),  # Depósito
        Nodo(1, 10, 10, 10, 0, 100, 5),
        Nodo(2, 20, 10, 10, 0, 100, 5),
        Nodo(3, 30, 10, 10, 0, 100, 5),
        Nodo(4, 40, 10, 10, 0, 100, 5)
    ]
    vehicle_capacity = 50
    best_path, best_distance = vrptw_aco_solver(nodes, vehicle_capacity)
    print(f"Mejor distancia: {best_distance}")
    print("Mejor ruta:")
    for node in best_path:
        print(f"Cliente {node.index}")

if __name__ == "__main__":
    main()
