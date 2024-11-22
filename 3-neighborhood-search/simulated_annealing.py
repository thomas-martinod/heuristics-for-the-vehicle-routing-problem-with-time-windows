import math
import random
import time
from distance_finder import calculate_total_distance
from feasibility import is_feasible


def generate_multiple_neighbors(current_routes, times, capacity, num_neighbors=20):
    """
    Genera múltiples vecinos y selecciona los mejores en términos de costo.
    """
    candidate_neighbors = []
    for _ in range(num_neighbors):
        neighbor_routes = [route.copy() for route in current_routes]
        move_type = random.choice(['swap_within_route', 'merge_routes', 'relocate_customer'])

        if move_type == 'swap_within_route':
            route_idx = random.randint(0, len(neighbor_routes) - 1)
            route = neighbor_routes[route_idx]
            if len(route) > 3:
                i = random.randint(1, len(route) - 3)
                j = random.randint(i + 1, len(route) - 2)
                new_route = route[:i] + route[i:j+1][::-1] + route[j+1:]
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

        candidate_neighbors.append(neighbor_routes)

    candidate_neighbors.sort(key=lambda neighbor: calculate_total_distance(neighbor, times))
    return candidate_neighbors[:5]  # Retorna los mejores 5 vecinos


def simulated_annealing_robust(routes, times, capacity, initial_temperature, cooling_rate, time_limit, start_time, alpha=1, beta=1000, max_no_improvement=500):
    """
    Recocido simulado robusto para optimizar las rutas de un problema VRPTW.
    """
    best_routes = [route.copy() for route in routes]
    best_cost = calculate_total_distance(best_routes, times) + beta * len(best_routes)
    current_routes = best_routes.copy()
    current_cost = best_cost
    temperature = initial_temperature

    no_improvement_counter = 0
    perturbation_chance = 0.2

    while temperature > 0.01 and no_improvement_counter < max_no_improvement:
        current_time = time.time()
        if current_time - start_time >= time_limit:
            break

        candidate_neighbors = generate_multiple_neighbors(current_routes, times, capacity)
        for neighbor_routes in candidate_neighbors:
            neighbor_cost = calculate_total_distance(neighbor_routes, times) + beta * len(neighbor_routes)
            delta = neighbor_cost - current_cost

            if delta < 0 or random.uniform(0, 1) < math.exp(-delta / temperature):
                current_routes = neighbor_routes
                current_cost = neighbor_cost

                if neighbor_cost < best_cost:
                    best_routes = neighbor_routes
                    best_cost = neighbor_cost
                    no_improvement_counter = 0
                else:
                    no_improvement_counter += 1
            else:
                no_improvement_counter += 1

        if no_improvement_counter > max_no_improvement and random.uniform(0, 1) < perturbation_chance:
            perturb_route = random.choice(current_routes)
            for _ in range(len(perturb_route) // 2):
                from_route_idx = random.randint(0, len(current_routes) - 1)
                to_route_idx = random.randint(0, len(current_routes) - 1)
                while from_route_idx == to_route_idx:
                    to_route_idx = random.randint(0, len(current_routes) - 1)
                from_route = current_routes[from_route_idx]
                to_route = current_routes[to_route_idx]
                if len(from_route) > 3:
                    customer_idx = random.randint(1, len(from_route) - 2)
                    customer = from_route.pop(customer_idx)
                    insertion_idx = random.randint(1, len(to_route) - 1)
                    to_route.insert(insertion_idx, customer)
            no_improvement_counter = 0

        temperature *= cooling_rate
        if no_improvement_counter > max_no_improvement * 1.5:
            temperature = initial_temperature

    return best_routes
