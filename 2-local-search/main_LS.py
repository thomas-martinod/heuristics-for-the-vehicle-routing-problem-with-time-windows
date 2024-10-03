import time
from file_reader import read_txt_file
from solution_interpreter import info_of_all_routes
from distance_finder import distance_matrix_generator, calculate_total_distance
from neighborhoods import interchange_two_positions, two_opt, three_opt, length_L_reinsertion, destroy_route, VND
from file_writer import save_to_excel
from openpyxl import Workbook



initial_method = 'constructive'                                                     # Select between 'constructive', 'GRASP' or 'ACO'
neighborhood_method = 'VND'                   # Select between 'Change2Indexes', '2-opt', '3-opt', 'length_L_reinsertion, destroy_route', 'VND'

directory_path = 'VRPTW Instances'
excel_path = f'C:\\Users\\thomm\\Documents\\GitHub\\heuristica\\2-local-search\\local-search-results\\{initial_method}\\VRTPW_tm_{initial_method}_LS_{neighborhood_method}.xlsx'
initial_solution_path = f'C:\\Users\\thomm\\Documents\\GitHub\\heuristica\\2-local-search\\constructive-results\\VRPTW_tm_{initial_method}.xlsx'

wb = Workbook()             # Initialize a new Excel workbook
wb.remove(wb.active)        # Remove the default empty sheet



for i in range(1, 19, 1):
    # Input and output file paths
    sheet_number = i
    sheet_name = f'VRPTW{sheet_number}'

    instance_filename = f'{directory_path}/{sheet_name}.txt'                                         # Generate the file name for each instance

    # Read the number of nodes, vehicle capacity, and nodes (customers) from the file
    n, Q, nodes = read_txt_file(instance_filename)
    distances = distance_matrix_generator(nodes)                                            # Calculate the travel time matrix

    # Initial solution from excel
    initial_solution, constructive_total_distance, constructive_execution_time = info_of_all_routes(initial_solution_path, sheet_name)

    for route_data in initial_solution:
        route_data['route_objects'] = [nodes[node_index] for node_index in route_data['route_indexes']]

    start_time = time.time()

    local_search_results = []

    # Neighborhood selection and LS
    if neighborhood_method == 'Change2Indexes':
        for i in initial_solution:
            local_search_results.append(interchange_two_positions(i, distances=distances))
    elif neighborhood_method == '2-opt':
        for i in initial_solution:
            local_search_results.append(two_opt(i, distances=distances))
    elif neighborhood_method == '3-opt':
        for i in initial_solution:
            local_search_results.append(three_opt(i, distances=distances))
    elif neighborhood_method == 'length_L_reinsertion':
        local_search_results = length_L_reinsertion(initial_solution, capacity = Q, distances = distances, L = 3)
    elif neighborhood_method == 'destroy_route':
        local_search_results = destroy_route(initial_solution, max_capacity = Q, distances = distances)
    elif neighborhood_method == 'VND':
        local_search_results = VND(initial_solution, Q, distances)



    computation_time_ls = time.time() - start_time

    routes = [i['route_objects'] for i in local_search_results]
    route_numbers = [i['route_indexes'] for i in local_search_results]

    save_to_excel(wb, f'VRPTW{sheet_number}', routes, calculate_total_distance(routes, distances), computation_time = computation_time_ls + constructive_execution_time, times=distances)

wb.save(excel_path)