import os
import math
import numpy as np
import matplotlib.pyplot as plt
from openpyxl import Workbook
import random
import time 


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
## Function to read the 18 .txt files (example problems with different properties)
def read_txt_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

        # Read n an Q
        first_line = lines[0].strip().split()
        n = int(first_line[0])
        Q = int(first_line[1])

        nodes = []

        # Read the n+1 next lines for index (i), x and y coordinate (x_i, y_i),
        # demand (q_i), Lower and upper limit for time window (e_i),(l_i),
        # and time service (s_i)
        
        for line in lines[1:n+2]: 
            parts = list(map(int, line.strip().split()))
            node = Nodo(parts[0], parts[1], parts[2], parts[3], parts[4], parts[5], parts[6])
            nodes.append(node)
    return n, Q, nodes


## Time of travel (Define by Euclidean Distance)
## Function given by teacher at [1]
def euclidean_distance(node1, node2):
    return round(math.sqrt((node1.x_cord - node2.x_cord) ** 2 + (node1.y_cord - node2.y_cord) ** 2), 3)

## Function to calculate time travel (t_(i,j))
## Function given by teacher at [1]
def calculate_travel_times(nodes):
    n = len(nodes)
    times = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            times[i][j] = euclidean_distance(nodes[i], nodes[j])
    return times

## Restrictions (CONSTRUCTIVE METHOD)
def is_feasible(route, new_node, capacity, times):
    ## This restricition ensure not to exceed capacity

    total_demand = sum(node.demand for node in route) + new_node.demand
    if total_demand > capacity:
        return False

    # check time windows
    current_time = 0
    for i in range(1, len(route)):
        current_time += times[route[i-1].index][route[i].index]
        if current_time < route[i].time_window[0]:
            current_time = route[i].time_window[0]
        if current_time > route[i].time_window[1]:
            return False
        current_time += route[i].serv_time
    return True

# Función para seleccionar rutas usando GRASP Reactivo

## Math model for reactive grasp
def reactive_grasp_route_selection(nodes, capacity, times, alphas=[0.03, 0.10, 0.11, 0.12], iterations=100):
# def reactive_grasp_route_selection(nodes, capacity, times, alphas=[0.03, 0.08, 0.095, 0.108], iterations=100): FAILED TRY

    alpha_probs = {alpha: 1/len(alphas) for alpha in alphas}  # Probability of \alpha
    best_routes = None
    best_distance = float('inf')
    min_prob = 1e-6  # Umbral mínimo para probabilidades

    for _ in range(iterations):
        # \alpha selection from alpha probs
        alpha = random.choices(list(alpha_probs.keys()), weights=alpha_probs.values())[0]
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
                # 
                feasible_customers.sort(key=lambda x: times[route[-1].index][x.index])
                # RCL LIST
                rcl_size = max(1, int(len(feasible_customers) * alpha))
                rcl = feasible_customers[:rcl_size]
                # Select customer on RCL
                next_customer = random.choice(rcl)
                if current_load + next_customer.demand <= capacity:
                    route.append(next_customer)
                    current_load += next_customer.demand
                    customers.remove(next_customer)
                else:
                    break
            route.append(depot)
            routes.append(route)

        # TOTAL DISTANCE
        total_distance = calculate_total_distance(routes, times)
        if total_distance < best_distance:
            best_distance = total_distance
            best_routes = routes

        # Check probs 
        for alpha_key in alpha_probs:
            if alpha_key == alpha:
                alpha_probs[alpha_key] += 1 / (1 + total_distance - best_distance)
            else:
                alpha_probs[alpha_key] = max(min_prob, alpha_probs[alpha_key] - 1 / (1 + total_distance - best_distance))
        
        # Normal
        total_prob = sum(alpha_probs.values())
        if total_prob == 0 or total_prob != total_prob:  
            alpha_probs = {alpha: 1/len(alphas) for alpha in alphas}  
        else:
            alpha_probs = {k: v / total_prob for k, v in alpha_probs.items()}

    return best_routes, best_distance


## FUNCTION FROM CONSTRUCTIVE METHOD 
## Calculate the route distance for a route in 
def calculate_route_distance(route, times):
    distance = 0.0
    for i in range(len(route) - 1):
        distance += times[route[i].index][route[i + 1].index]
    return distance

## Sum of the distances calculated above 
def calculate_total_distance(routes, times):
    return sum(calculate_route_distance(route, times) for route in routes)

## Plot Solutions with node numeration and with different colors depending the route
def plot_routes(routes, filename):
    plt.figure(figsize=(10, 8))
    
    for route in routes:
        x_coords = [node.x_cord for node in route]
        y_coords = [node.y_cord for node in route]
        plt.plot(x_coords, y_coords, marker='o')
        for i, node in enumerate(route):
            plt.text(node.x_cord, node.y_cord, str(node.index), fontsize=12, ha='right')
    
    plt.title(f"VRPTW Solution: {filename}")
    plt.xlabel("X Coordinate")
    plt.ylabel("Y Coordinate")
    plt.grid(True)
    plt.savefig(filename.replace('.txt', '_solution.png'))
    plt.show()

## SAVE TO EXCEL FILE CODE from [2]
def save_to_excel(workbook, sheet_name, routes, total_distance, computation_time, times):
    ws = workbook.create_sheet(title=sheet_name)

    num_vehicles = len(routes)
    ws.append([num_vehicles, round(total_distance, 0), round(computation_time, 0)])

    for route in routes:
        route_nodes = [0] 
        arrival_times = []
        current_time = 0
        total_load = 0

        for j in range(1, len(route)):
            current_time += times[route[j-1].index][route[j].index]
            if current_time < route[j].time_window[0]:
                current_time = route[j].time_window[0]
            arrival_times.append(round(current_time, 3))  
            total_load += route[j].demand
            route_nodes.append(route[j].index)

            current_time += route[j].serv_time

        route_nodes.append(0)  

        
        ws.append([len(route_nodes) - 3] + route_nodes + arrival_times + [total_load])
        


def vrptw_solver(directory_path, output_filename):
    start_time = time.time() 
    
   
    wb = Workbook()
    
  
    wb.remove(wb.active)

    for filename in os.listdir(directory_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(directory_path, filename)
            n, Q, nodes = read_txt_file(file_path)
            
            times = calculate_travel_times(nodes)
            
           
            routes, best_distance = reactive_grasp_route_selection(nodes, Q, times)
            computation_time = time.time() - start_time
            
            print(f"Solution for {filename}: Total Distance = {best_distance}")
            
           
            sheet_name = filename.split('.')[0]
            save_to_excel(wb, sheet_name, routes, best_distance, computation_time, times)
            
            
            ### FUNCTION TO CHECK THE PROCESS MANUALLY
            
            
            # for idx, route in enumerate(routes):
            #     print(f" Route {idx + 1}: ", " -> ".join([str(node.index) for node in route]))
            
            plot_routes(routes, filename)

    
    wb.save(output_filename)
    
    end_time = time.time()  
    elapsed_time = end_time - start_time 
    print(f"Tiempo total de ejecución: {elapsed_time:.4f} segundos")
    



directory_path = 'VRPTW Instances'
output_filename = "VRPTW_Reactive_GRASP_JuanFernando_Constructivo.xlsx"
vrptw_solver(directory_path, output_filename)

