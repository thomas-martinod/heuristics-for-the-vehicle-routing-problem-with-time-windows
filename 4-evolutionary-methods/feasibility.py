# Function to check if adding a new node to the route doesn't exceed vehicle capacity
def is_capacity_feasible(x, capacity):
    total_demand = sum(node.q for node in x)
    return total_demand <= capacity



# Function to check if adding a new node to the route is feasible based on time windows
def is_time_feasible(x, distances):
    route = x
    current_time = 0  # Initialize the time tracker

    # Loop through the route and calculate the time spent traveling between nodes
    for i in range(1, len(route)):
        current_time += distances[route[i-1].index][route[i].index]  # Add travel time between nodes

        # Adjust the current time if the vehicle arrives earlier than the time window start
        if current_time < route[i].inf:
            current_time = route[i].inf

        # If the vehicle arrives after the time window, return False (infeasible)
        if current_time > route[i].sup:
            return False

        # Add the service time at the current node
        current_time += route[i].t_serv

    return True  # If both time and capacity constraints are satisfied, return True



# Function to check if adding a new node to the route is feasible based on both capacity and time
def is_feasible(route, capacity, distances):
    return is_capacity_feasible(route, capacity) and is_time_feasible(route, distances)
