import random
import time
from distance_finder import calculate_total_distance
from feasibility import is_feasible

MAX_NO_IMPROVEMENT = 500

# Function to select an operator based on their scores
def select_operator(operators, operator_scores):
    total_score = sum(operator_scores[op] for op in operators)
    pick = random.uniform(0, total_score)
    current = 0
    for op in operators:
        current += operator_scores[op]
        if current >= pick:
            return op
    return operators[-1]

# ALNS algorithm
def alns_algorithm(routes, times, capacity, destroy_operators, repair_operators, time_limit, start_time, alpha=10.0, beta=450.0):
    best_routes = [route.copy() for route in routes]
    best_cost = calculate_total_cost(best_routes, times, alpha, beta)
    current_routes = best_routes.copy()

    operator_scores = {op: 1 for op in destroy_operators + repair_operators}

    no_improvement_counter = 0

    while no_improvement_counter < MAX_NO_IMPROVEMENT:
        current_time = time.time()
        if current_time - start_time >= time_limit:
            break

        # Select operators
        destroy_op = select_operator(destroy_operators, operator_scores)
        repair_op = select_operator(repair_operators, operator_scores)

        # Apply destroy and repair operators
        partial_routes, customers_to_reinsert = destroy_op(current_routes, times, capacity)
        new_routes = repair_op(partial_routes, customers_to_reinsert, times, capacity)
        new_cost = calculate_total_cost(new_routes, times, alpha, beta)

        # Update best solution
        if new_cost < best_cost:
            best_routes = new_routes
            best_cost = new_cost
            operator_scores[destroy_op] += 1
            operator_scores[repair_op] += 1
            no_improvement_counter = 0  # Reset counter
        else:
            operator_scores[destroy_op] = max(1, operator_scores[destroy_op] - 1)
            operator_scores[repair_op] = max(1, operator_scores[repair_op] - 1)
            no_improvement_counter += 1

        current_routes = new_routes

    return best_routes

# Calculate total cost of a solution
def calculate_total_cost(routes, times, alpha=1, beta=1000):
    total_distance = calculate_total_distance(routes, times)
    num_routes = len(routes)
    total_cost = alpha * total_distance + beta * num_routes
    return total_cost
