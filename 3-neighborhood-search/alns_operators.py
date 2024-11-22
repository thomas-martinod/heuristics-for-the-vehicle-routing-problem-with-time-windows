import random
from feasibility import is_feasible

# Destroy Operator: Random Removal
def destroy_random(routes, times, capacity):
    destroyed_routes = [route.copy() for route in routes]
    num_customers_to_remove = max(1, int(0.1 * sum(len(route) - 2 for route in routes)))
    customers_to_remove = []
    while len(customers_to_remove) < num_customers_to_remove:
        route_idx = random.randint(0, len(destroyed_routes) - 1)
        route = destroyed_routes[route_idx]
        if len(route) > 3:
            cust_idx = random.randint(1, len(route) - 2)
            customer = route.pop(cust_idx)
            customers_to_remove.append(customer)
    return destroyed_routes, customers_to_remove

# Destroy Operator: Worst Removal
def destroy_worst(routes, times, capacity):
    destroyed_routes = [route.copy() for route in routes]
    customer_costs = []
    for route in destroyed_routes:
        for idx in range(1, len(route) - 1):
            prev_node = route[idx - 1]
            current_node = route[idx]
            next_node = route[idx + 1]
            cost = times[prev_node.index][current_node.index] + times[current_node.index][next_node.index] - times[prev_node.index][next_node.index]
            customer_costs.append((cost, current_node, route))
    customer_costs.sort(key=lambda x: x[0], reverse=True)
    num_customers_to_remove = max(1, int(0.1 * len(customer_costs)))
    customers_to_remove = []
    for i in range(num_customers_to_remove):
        cost, customer, route = customer_costs[i]
        route.remove(customer)
        customers_to_remove.append(customer)
    return destroyed_routes, customers_to_remove

# Destroy Operator: Route Removal
def destroy_route_removal(routes, times, capacity):
    destroyed_routes = [route.copy() for route in routes]
    num_routes_to_remove = max(1, int(0.1 * len(routes)))
    routes_to_remove = random.sample(destroyed_routes, num_routes_to_remove)
    customers_to_reinsert = []

    for route in routes_to_remove:
        customers_to_reinsert.extend(route[1:-1])
        destroyed_routes.remove(route)
    return destroyed_routes, customers_to_reinsert

# Destroy Operator: Least Utilized
def destroy_least_utilized(routes, times, capacity):
    destroyed_routes = [route.copy() for route in routes]
    route_loads = [(sum(node.q for node in route[1:-1]), idx) for idx, route in enumerate(destroyed_routes)]
    route_loads.sort(key=lambda x: x[0])
    num_routes_to_remove = max(1, int(0.1 * len(routes)))
    routes_to_remove = [destroyed_routes[idx] for _, idx in route_loads[:num_routes_to_remove]]
    customers_to_reinsert = []
    for route in routes_to_remove:
        customers_to_reinsert.extend(route[1:-1])
        destroyed_routes.remove(route)
    return destroyed_routes, customers_to_reinsert

# Repair Operator: Greedy Insertion
def repair_greedy(partial_routes, customers_to_insert, times, capacity):
    routes = [route.copy() for route in partial_routes]
    for customer in customers_to_insert:
        best_position = None
        best_increase = float('inf')
        best_route_idx = None
        for idx, route in enumerate(routes):
            for pos in range(1, len(route)):
                new_route = route[:pos] + [customer] + route[pos:]
                if is_feasible(new_route, capacity, times):
                    increase = times[route[pos - 1].index][customer.index] + times[customer.index][route[pos].index] - times[route[pos - 1].index][route[pos].index]
                    if increase < best_increase:
                        best_increase = increase
                        best_position = pos
                        best_route_idx = idx
        if best_position is not None:
            routes[best_route_idx] = routes[best_route_idx][:best_position] + [customer] + routes[best_route_idx][best_position:]
        else:
            new_route = [routes[0][0], customer, routes[0][0]]
            if is_feasible(new_route, capacity, times):
                routes.append(new_route)
    return routes

# Repair Operator: Regret Insertion
def repair_regret(partial_routes, customers_to_insert, times, capacity):
    routes = [route.copy() for route in partial_routes]
    while customers_to_insert:
        regrets = []
        for customer in customers_to_insert:
            insertion_costs = []
            for idx, route in enumerate(routes):
                best_increase = float('inf')
                for pos in range(1, len(route)):
                    new_route = route[:pos] + [customer] + route[pos:]
                    if is_feasible(new_route, capacity, times):
                        increase = times[route[pos - 1].index][customer.index] + times[customer.index][route[pos].index] - times[route[pos - 1].index][route[pos].index]
                        if increase < best_increase:
                            best_increase = increase
                if best_increase < float('inf'):
                    insertion_costs.append(best_increase)
            if len(insertion_costs) >= 2:
                insertion_costs.sort()
                regret = insertion_costs[1] - insertion_costs[0]
            elif len(insertion_costs) == 1:
                regret = insertion_costs[0]
            else:
                regret = float('inf')
            regrets.append((regret, customer))
        regrets.sort(key=lambda x: x[0], reverse=True)
        _, selected_customer = regrets[0]
        best_position = None
        best_increase = float('inf')
        best_route_idx = None
        for idx, route in enumerate(routes):
            for pos in range(1, len(route)):
                new_route = route[:pos] + [selected_customer] + route[pos:]
                if is_feasible(new_route, capacity, times):
                    increase = times[route[pos - 1].index][selected_customer.index] + times[selected_customer.index][route[pos].index] - times[route[pos - 1].index][route[pos].index]
                    if increase < best_increase:
                        best_increase = increase
                        best_position = pos
                        best_route_idx = idx
        if best_position is not None:
            routes[best_route_idx] = routes[best_route_idx][:best_position] + [selected_customer] + routes[best_route_idx][best_position:]
        else:
            new_route = [routes[0][0], selected_customer, routes[0][0]]
            if is_feasible(new_route, capacity, times):
                routes.append(new_route)
        customers_to_insert.remove(selected_customer)
    return routes

# Repair Operator: Savings Insertion
def repair_savings(partial_routes, customers_to_insert, times, capacity):
    routes = [route.copy() for route in partial_routes]
    depot = routes[0][0]
    savings = []
    for i in customers_to_insert:
        for j in customers_to_insert:
            if i != j:
                s = times[depot.index][i.index] + times[depot.index][j.index] - times[i.index][j.index]
                savings.append((s, i, j))
    savings.sort(key=lambda x: x[0], reverse=True)
    inserted_customers = set()
    for s, i, j in savings:
        if i in inserted_customers or j in inserted_customers:
            continue
        new_route = [depot, i, j, depot]
        if is_feasible(new_route, capacity, times):
            routes.append(new_route)
            inserted_customers.update([i, j])
    remaining_customers = [c for c in customers_to_insert if c not in inserted_customers]
    for customer in remaining_customers:
        best_position = None
        best_increase = float('inf')
        best_route_idx = None
        for idx, route in enumerate(routes):
            for pos in range(1, len(route)):
                new_route = route[:pos] + [customer] + route[pos:]
                if is_feasible(new_route, capacity, times):
                    increase = times[route[pos - 1].index][customer.index] + times[customer.index][route[pos].index] - times[route[pos - 1].index][route[pos].index]
                    if increase < best_increase:
                        best_increase = increase
                        best_position = pos
                        best_route_idx = idx
        if best_position is not None:
            routes[best_route_idx] = routes[best_route_idx][:best_position] + [customer] + routes[best_route_idx][best_position:]
        else:
            new_route = [depot, customer, depot]
            if is_feasible(new_route, capacity, times):
                routes.append(new_route)
    return routes
