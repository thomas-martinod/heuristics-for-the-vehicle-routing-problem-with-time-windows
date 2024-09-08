import random
import numpy as np
from distance_finder import calculate_total_distance
from feasibility import is_feasible

random.seed(15)

def reactive_grasp_route_selection(nodes, capacity, times, alphas = list(np.arange(0.03, 0.3, 0.1)), iterations=100):
    alpha_probs = {alpha: 1/len(alphas) for alpha in alphas}  # Initialize probabilities for each alpha
    best_routes = None
    best_distance = float('inf')
    min_prob = 1e-6  # Minimum threshold for probabilities

    for _ in range(iterations):
        # Choose an alpha based on the probabilities
        alpha = random.choices(list(alpha_probs.keys()), weights=alpha_probs.values())[0]
        depot = nodes[0]
        customers = nodes[1:]
        routes = []

        # While there are still customers, build routes
        while customers:
            route = [depot]
            current_load = 0

            while True:
                # Get feasible customers based on capacity and time windows
                feasible_customers = [cust for cust in customers if is_feasible(route, cust, capacity, times)]
                if not feasible_customers:
                    break

                # Sort by distance to the current node and form the RCL
                feasible_customers.sort(key=lambda x: times[route[-1].index][x.index])
                rcl_size = max(1, int(len(feasible_customers) * alpha))
                rcl = feasible_customers[:rcl_size]

                # Randomly select a customer from the RCL
                next_customer = random.choice(rcl)

                if current_load + next_customer.q <= capacity:
                    route.append(next_customer)
                    current_load += next_customer.q
                    customers.remove(next_customer)
                else:
                    break

            route.append(depot)  # Return to depot at the end of the route
            routes.append(route)

        # Calculate total distance for the current solution
        total_distance = calculate_total_distance(routes, times)
        if total_distance < best_distance:
            best_distance = total_distance
            best_routes = routes

        # Update probabilities based on the current alpha
        for alpha_key in alpha_probs:
            if alpha_key == alpha:
                alpha_probs[alpha_key] += 1 / (1 + total_distance - best_distance)
            else:
                alpha_probs[alpha_key] = max(min_prob, alpha_probs[alpha_key] - 1 / (1 + total_distance - best_distance))

        # Normalize probabilities
        total_prob = sum(alpha_probs.values())
        if total_prob == 0 or total_prob != total_prob:  # Handle edge cases
            alpha_probs = {alpha: 1/len(alphas) for alpha in alphas}
        else:
            alpha_probs = {k: v / total_prob for k, v in alpha_probs.items()}

    return best_routes, best_distance
