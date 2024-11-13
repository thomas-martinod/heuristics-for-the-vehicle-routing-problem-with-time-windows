# Function to check if adding a new node to the route doesn't exceed vehicle capacity
def is_capacity_feasible(route, new_node, capacity):
    # Calculate the total demand by summing the demand of all nodes in the route and the new node
    total_demand = sum(node.q for node in route) + new_node.q
    # Return True if the total demand is within the vehicle's capacity, False otherwise
    return total_demand <= capacity

# Function to check if adding a new node to the route is feasible based on time windows
def is_time_feasible(route, new_node, times):
    current_time = 0  # Initialize the time tracker

    # Loop through the route and calculate the time spent traveling between nodes
    for i in range(1, len(route)):
        current_time += times[route[i-1].index][route[i].index]  # Add travel time between nodes

        # Adjust the current time if the vehicle arrives earlier than the time window start
        if current_time < route[i].inf:
            current_time = route[i].inf

        # If the vehicle arrives after the time window, return False (infeasible)
        if current_time > route[i].sup:
            return False

        # Add the service time at the current node
        current_time += route[i].t_serv

    # Calculate the arrival time at the new node
    new_node_arrival_time = current_time + times[route[-1].index][new_node.index]

    # Check if the arrival time fits within the time window of the new node
    if new_node_arrival_time < new_node.inf:
        new_node_arrival_time = new_node.inf
    if new_node_arrival_time > new_node.sup:
        return False  # If the vehicle arrives too late, return False

    return True  # If both time and capacity constraints are satisfied, return True

# Function to check if adding a new node to the route is feasible based on both capacity and time
def is_feasible(route, new_node, capacity, times):
    # Check both capacity and time feasibility
    return is_capacity_feasible(route, new_node, capacity) and is_time_feasible(route, new_node, times)
