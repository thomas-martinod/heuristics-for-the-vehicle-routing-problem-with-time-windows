def is_capacity_feasible(route, new_node, capacity):
    total_demand = sum(node.q for node in route) + new_node.q
    return total_demand <= capacity

def is_time_feasible(route, new_node, times):
    current_time = 0
    for i in range(1, len(route)):
        current_time += times[route[i-1].index][route[i].index]
        if current_time < route[i].inf:
            current_time = route[i].inf
        if current_time > route[i].sup:
            return False
        current_time += route[i].t_serv

    # Verificación de tiempo para el nuevo nodo
    new_node_arrival_time = current_time + times[route[-1].index][new_node.index]
    if new_node_arrival_time < new_node.inf:
        new_node_arrival_time = new_node.inf
    if new_node_arrival_time > new_node.sup:
        return False

    return True

def is_feasible(route, new_node, capacity, times):
    return is_capacity_feasible(route, new_node, capacity) and is_time_feasible(route, new_node, times)
