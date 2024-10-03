from feasibility import is_feasible, is_time_feasible
from distance_finder import calculate_route_distance

# -----------------------------------------------------------------------------------------------------------
# Interchange two positions

def interchange_two_positions(x_dict, distances):         # x is a node object
    x = x_dict['route_objects']
    best = x
    R = len(x)
    for i in range(1, R-1):
        for j in range(i+1, R-1):
            x_prime = x.copy()                      # Create a copy of x before making changes
            x_prime = swap_two(x_prime, i, j)
            if is_time_feasible(x_prime, distances):
                if calculate_route_distance(x_prime, distances) < calculate_route_distance(best, distances):
                    x_dict['route_objects'] = x_prime
                    x_dict['route_indexes'] = [i.index for i in x_prime]
                    best = x_prime

    return x_dict


def swap_two(arr, i,j):
    aux = arr[i]
    arr[i] = arr[j]
    arr[j] = aux
    return arr


# -----------------------------------------------------------------------------------------------------------
# 2-opt

def two_opt(x_dict, distances):
    x = x_dict['route_objects']
    best = x
    R = len(x)
    for i in range(1, R-1):
        for j in range(i+1, R-1):
            x_prime = invert_subsequence(x, i, j)
            if is_time_feasible(x_prime, distances):
                if calculate_route_distance(x_prime, distances) < calculate_route_distance(best, distances):
                    x_dict['route_objects'] = x_prime
                    x_dict['route_indexes'] = [i.index for i in x_prime]
                    best = x_prime
    return x_dict


def invert_subsequence(seq, i, j):
    subseq1, subseq2, subseq3 = seq[:i], seq[i:j+1], seq[j+1:]
    return subseq1 + subseq2[::-1] + subseq3




# -----------------------------------------------------------------------------------------------------------
# 3-opt


def three_opt(x_dict, distances):
    x = x_dict['route_objects']
    best = x
    R = len(x)
    for i in range(1, R-1):
        for j in range(i+1, R-1):
            for k in range(j+1, R-1):
                candidates = generate_three_opt_candidates(x, i, j, k)
                for candidate in candidates:
                    # Ensure the last node (zero) is not moved
                    if candidate[-1] != 0:
                        continue  # Skip this candidate if the last element is not zero

                    if is_time_feasible(candidate, distances):
                        if calculate_route_distance(candidate, distances) < calculate_route_distance(best, distances):
                            best = candidate  # Update the best route if candidate is better

    # Update the x_dict with the best solution found
    x_dict['route_objects'] = best
    x_dict['route_indexes'] = [node.index for node in best]  # Update route indexes if needed

    return x_dict



def generate_three_opt_candidates(seq, i, j, k):
    """
    Generate all unique and valid 3-opt reconnections by avoiding 2-opt moves.
    """
    subseq1 = seq[:i]      # First segment before i
    subseq2 = seq[i:j+1]   # Second segment between i and j
    subseq3 = seq[j+1:k+1] # Third segment between j and k
    subseq4 = seq[k+1:]    # Remaining segment after k

    # List to store all possible new reconnections
    candidates = []

    # Only generate combinations that involve at least two subsequences being altered

    # 1. Reverse two subsequences, leave others intact
    candidates.append(subseq1[::-1] + subseq2[::-1] + subseq3 + subseq4)  # Reverse subseq1 and subseq2
    candidates.append(subseq1[::-1] + subseq2 + subseq3[::-1] + subseq4)  # Reverse subseq1 and subseq3
    candidates.append(subseq1 + subseq2[::-1] + subseq3[::-1] + subseq4)  # Reverse subseq2 and subseq3

    # 2. Reverse all three subsequences
    candidates.append(subseq1[::-1] + subseq2[::-1] + subseq3[::-1] + subseq4)

    # 3. Swap subsequences B and C (subseq2 and subseq3)
    candidates.append(subseq1 + subseq3 + subseq2 + subseq4)              # Swap subseq2 and subseq3
    candidates.append(subseq1[::-1] + subseq3 + subseq2 + subseq4[::-1])  # Swap subseq2 and subseq3, reverse subseq1 and subseq4

    # 4. Reverse the order of subsequences in various combinations
    candidates.append(subseq1 + subseq3[::-1] + subseq2[::-1] + subseq4)  # Reverse subseq3 and subseq2

    return candidates




# -----------------------------------------------------------------------------------------------------------
# Remover dos secuencias y reinsertarlas en nuevas posiciones (entre rutas)

def length_L_reinsertion(all_routes, capacity, distances, L=2):
    x = [t['route_objects'] for t in all_routes]
    R = len(x)  # Número de rutas

    for l1 in range(L, 0, -1):  # Bucle para la longitud de la subsecuencia en la primera ruta
        for l2 in range(L, 0, -1):  # Bucle para la longitud de la subsecuencia en la segunda ruta

            for i in range(R):  # Iterar sobre la primera ruta
                route1 = x[i]
                if len(route1) - 2 <= l1:  # Verificar que route1 tiene una subsecuencia de longitud l1
                    continue  # Si no es suficiente, saltar

                for i2 in range(1, len(route1) - 1 - l1 + 1):  # Posición inicial de subsecuencia en route1
                    subseq1 = route1[i2 : i2 + l1]  # Extraer subsecuencia de longitud l1

                    for j in range(i + 1, R):  # Iterar sobre la segunda ruta
                        route2 = x[j]
                        if len(route2) - 2 < l2:  # Verificar que route2 tiene una subsecuencia de longitud l2
                            continue  # Si no es suficiente, saltar

                        for j2 in range(1, len(route2) - 1 - l2 + 1):  # Posición inicial en route2
                            subseq2 = route2[j2 : j2 + l2]  # Extraer subsecuencia de longitud l2

                            # Crear nuevas rutas con subsecuencias intercambiadas
                            new_route1 = route1[:i2] + subseq2 + route1[i2 + l1:]
                            new_route2 = route2[:j2] + subseq1 + route2[j2 + l2:]

                            # Verificar factibilidad
                            if is_feasible(new_route1, capacity, distances) and is_feasible(new_route2, capacity, distances):
                                # Evaluar si la nueva solución es mejor
                                if calculate_route_distance(new_route1, distances) + calculate_route_distance(new_route2, distances) < \
                                   calculate_route_distance(x[i], distances) + calculate_route_distance(x[j], distances):

                                    # Actualizar la mejor solución encontrada
                                    all_routes[i]['route_objects'] = new_route1
                                    all_routes[i]['route_indexes'] = [t.index for t in new_route1]

                                    all_routes[j]['route_objects'] = new_route2
                                    all_routes[j]['route_indexes'] = [t.index for t in new_route2]

                                    return all_routes  # Retornar al encontrar la primera mejora
    return all_routes  # Retornar si no se encuentran mejoras






# -----------------------------------------------------------------------------------------------------------
# Destruir una ruta a la fuerza


def destroy_route(all_routes, max_capacity, distances):
    # Sort routes by number of nodes first, then by capacity
    sorted_routes = sort_by_number_of_nodes_and_capacity(all_routes)
    # Select the shortest route (excluding the zeros at the start and end)
    route_to_destroy = sorted_routes[0]['route_objects'][1:-1]  # Shortest route without the zeros
    original_routes = sorted_routes[1:]  # Remove the route to be destroyed from the list
    # Sort the remaining routes by current capacity
    sorted_routes = sort_by_capacity(original_routes)

    inserted_nodes = []
    # Iterate over the nodes in the route to be destroyed
    for node in route_to_destroy:
        node_inserted = False
        # Try to insert the node into the remaining routes
        for i in range(len(sorted_routes)):
            if node_inserted:
                break
            current_route = sorted_routes[i]['route_objects'].copy()  # Take a copy of the current route
            # Iterate over valid positions to insert (without touching the zeros)
            for k in range(1, len(current_route)):
                # Create a temporary copy of the route to test the insertion
                temp_route = current_route[:k] + [node] + current_route[k:]
                # Check if the new route is feasible (capacity and other constraints)
                if is_feasible(temp_route, max_capacity, distances):
                    # Mark the node as inserted and update the route
                    node_inserted = True
                    sorted_routes[i]['route_objects'] = temp_route  # Update the route
                    inserted_nodes.append(node)
                    break  # Exit the position loop since the node was inserted
        if not node_inserted:
            # If we can't insert a node, we need to revert all changes
            for inserted_node in inserted_nodes:
                for route in sorted_routes:
                    if inserted_node in route['route_objects']:
                        route['route_objects'].remove(inserted_node)
            return all_routes  # Return the original routes if we can't insert all nodes

    # Sort routes by their original index before returning
    sorted_routes = sort_by_index(sorted_routes)
    # If we managed to insert all nodes, return the new routes
    return sorted_routes


# The other helper functions remain the same
def sort_by_number_of_nodes_and_capacity(arr):
    return sorted(arr, key=lambda x: (len(x['route_objects']), x['total_capacity_used']))

def sort_by_capacity(arr):
    return sorted(arr, key=lambda x: x['total_capacity_used'])

def sort_by_index(arr):
    return sorted(arr, key=lambda x: x['route_indexes'])



# -----------------------------------------------------------------------------------------------------------
# VND

def VND(initial_sln, Q, distances):
    s = initial_sln  # Original solution
    while True:
        # Start by making a copy of the current solution
        s_prime = s.copy()

        # Step 1: Apply destroy_route (or similar local search function)
        # s_prime = destroy_route(s_prime, Q, distances)  # Apply the destroy_route function

        # Step 2: Interchange two positions
        temp_s = [interchange_two_positions(route, distances) for route in s_prime.copy()]  # New copy before the operation
        if temp_s == s_prime:
            # Step 3: Try two-opt
            temp_s = [two_opt(route, distances) for route in s_prime.copy()]  # New copy before the operation
            if temp_s == s_prime:
                # Step 4: Try length-L reinsertion (L = 3 in this case)
                temp_s = length_L_reinsertion(s_prime.copy(), Q, distances, 3)  # New copy before the operation
                if temp_s == s_prime:
                    # Step 5: Try 3-opt
                    temp_s = [three_opt(route, distances) for route in s_prime.copy()]  # New copy before the operation
                    if temp_s == s_prime:  # If no improvement after 3-opt
                        return s  # Return the original solution as it can't be improved
                    else:
                        s = temp_s.copy()  # Update the solution with the improved one
                else:
                    s = temp_s.copy()  # Update the solution with the improved one
            else:
                s = temp_s.copy()  # Update the solution with the improved one
        else:
            s = temp_s.copy()  # Update the solution with the improved one



