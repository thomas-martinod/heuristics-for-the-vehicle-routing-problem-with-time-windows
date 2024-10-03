# Function to save the results of the vehicle routes to an Excel sheet
def save_to_excel(workbook, sheet_name, routes, total_distance, computation_time, times):
    # Create a new sheet in the workbook with the provided sheet name
    ws = workbook.create_sheet(title=sheet_name)

    # Number of vehicles used (each route corresponds to a vehicle)
    num_vehicles = len(routes)

    # First row: number of vehicles, total distance (rounded to 3 decimals), and computation time
    ws.append([num_vehicles, round(total_distance, 3), round(computation_time)])

    # For each vehicle's route, save the detailed information
    for route in routes:
        route_nodes = [0]  # Start from the depot (node 0)
        arrival_times = []  # To store the time of arrival at each node
        current_time = 0  # Track the current time during the route
        total_load = 0  # Track the total load of the vehicle

        # Iterate over each node in the route (excluding the depot at the start)
        for j in range(1, len(route)):
            # Add the travel time between consecutive nodes
            current_time += times[route[j-1].index][route[j].index]

            # If the vehicle arrives before the time window starts, wait until the earliest time
            if current_time < route[j].inf:
                current_time = route[j].inf  # Adjust for time window

            # Record the arrival time (rounded to 3 decimals)
            arrival_times.append(round(current_time, 3))

            # Add the demand of the current node to the total load of the vehicle
            total_load += route[j].q

            # Add the current node to the route nodes list
            route_nodes.append(route[j].index)

            # Add the service time at the current node
            current_time += route[j].t_serv

        route_nodes.append(0)

        # Calculate the number of customers served in this route (excluding the depot at both ends)
        num_customers = len(route_nodes) - 3  # Subtract the two depot nodes (start and end)

        # Save the number of customers, the route nodes, arrival times, and total load to the sheet
        ws.append([num_customers] + route_nodes + arrival_times + [total_load])
