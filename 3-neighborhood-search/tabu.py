import time
import random
from distance_finder import calculate_total_distance
from feasibility import is_feasible

# Function to extract moves between current and candidate routes
def extract_move(current_routes, candidate_routes):
    current_routes_set = set(frozenset(route) for route in current_routes)
    candidate_routes_set = set(frozenset(route) for route in candidate_routes)
    move = current_routes_set.symmetric_difference(candidate_routes_set)
    return move

# Function to generate a neighborhood of routes
def generate_neighborhood(current_routes, times, capacity, neighborhood_size=10):
    neighborhood = []
    for _ in range(neighborhood_size):
        neighbor = generate_neighbor(current_routes, times, capacity)
        neighborhood.append(neighbor)
    return neighborhood

# Function to generate a single neighbor
def generate_neighbor(current_routes, times, capacity):
    neighbor_routes = [route.copy() for route in current_routes]
    move_type = random.choice(['swap_within_route', 'merge_routes', 'relocate_customer'])

    if move_type == 'swap_within_route':
        route_idx = random.randint(0, len(neighbor_routes) - 1)
        route = neighbor_routes[route_idx]
        if len(route) > 3:
            i = random.randint(1, len(route) - 3)
            j = random.randint(i + 1, len(route) - 2)
            new_route = route[:i] + route[i:j + 1][::-1] + route[j + 1:]
            if is_feasible(new_route, capacity, times):
                neighbor_routes[route_idx] = new_route

    elif move_type == 'merge_routes':
        if len(neighbor_routes) > 1:
            idx1, idx2 = random.sample(range(len(neighbor_routes)), 2)
            route1 = neighbor_routes[idx1]
            route2 = neighbor_routes[idx2]
            merged_route = route1[:-1] + route2[1:]
            if is_feasible(merged_route, capacity, times):
                neighbor_routes.pop(max(idx1, idx2))
                neighbor_routes.pop(min(idx1, idx2))
                neighbor_routes.append(merged_route)

    elif move_type == 'relocate_customer':
        from_route_idx = random.randint(0, len(neighbor_routes) - 1)
        to_route_idx = random.randint(0, len(neighbor_routes) - 1)
        while from_route_idx == to_route_idx:
            to_route_idx = random.randint(0, len(neighbor_routes) - 1)
        from_route = neighbor_routes[from_route_idx]
        to_route = neighbor_routes[to_route_idx]
        if len(from_route) > 3:
            customer_idx = random.randint(1, len(from_route) - 2)
            customer = from_route.pop(customer_idx)
            insertion_idx = random.randint(1, len(to_route) - 1)
            new_to_route = to_route[:insertion_idx] + [customer] + to_route[insertion_idx:]
            if is_feasible(new_to_route, capacity, times) and is_feasible(from_route, capacity, times):
                neighbor_routes[from_route_idx] = from_route
                neighbor_routes[to_route_idx] = new_to_route
            else:
                from_route.insert(customer_idx, customer)

    return neighbor_routes

# Main Tabu Search function
def tabu_search_dynamic(routes, times, capacity, initial_tabu_tenure, time_limit, start_time, alpha=1.0, beta=500.0, max_no_improvement=500):
    best_routes = [route.copy() for route in routes]
    best_cost = calculate_total_cost(best_routes, times, alpha, beta)
    current_routes = best_routes.copy()
    current_cost = best_cost
    tabu_list = []
    tabu_tenure = initial_tabu_tenure
    max_tabu_size = initial_tabu_tenure
    no_improvement_counter = 0

    initial_neighborhood_size = 100
    neighborhood_size = initial_neighborhood_size

    while no_improvement_counter < max_no_improvement * 2:
        current_time = time.time()
        if current_time - start_time >= time_limit:
            break

        neighborhood = generate_neighborhood(current_routes, times, capacity, neighborhood_size)
        best_candidate = None
        best_candidate_cost = float('inf')
        best_move = None

        for candidate in neighborhood:
            candidate_cost = calculate_total_cost(candidate, times, alpha, beta)
            move = extract_move(current_routes, candidate)

            if move not in tabu_list or candidate_cost < best_cost * 1.05:
                if candidate_cost < best_candidate_cost:
                    best_candidate = candidate
                    best_candidate_cost = candidate_cost
                    best_move = move

        if best_candidate is None:
            break

        current_routes = best_candidate
        current_cost = best_candidate_cost

        if best_candidate_cost < best_cost:
            best_routes = best_candidate
            best_cost = best_candidate_cost
            no_improvement_counter = 0
            neighborhood_size = initial_neighborhood_size
        else:
            no_improvement_counter += 1

        if best_move:
            tabu_list.append(best_move)
            if len(tabu_list) > max_tabu_size:
                tabu_list.pop(0)

        if no_improvement_counter > max_no_improvement / 2:
            neighborhood_size = int(initial_neighborhood_size * 1.5)
            tabu_tenure = min(tabu_tenure + 1, initial_tabu_tenure * 2)
            max_tabu_size = tabu_tenure
        else:
            neighborhood_size = max(initial_neighborhood_size, neighborhood_size - 1)
            tabu_tenure = max(1, tabu_tenure - 1)
            max_tabu_size = tabu_tenure

    return best_routes

# Cost calculation function (defined for completeness)
def calculate_total_cost(routes, times, alpha=1.0, beta=500.0):
    total_distance = calculate_total_distance(routes, times)
    num_routes = len(routes)
    total_cost = alpha * total_distance + beta * num_routes
    return total_cost
