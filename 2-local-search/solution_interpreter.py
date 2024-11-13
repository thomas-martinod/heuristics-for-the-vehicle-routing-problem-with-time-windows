import pandas as pd
from math import isnan


def read_instance_solution(path, sheet_name):
    xls = pd.ExcelFile(path)
    df = pd.read_excel(xls, sheet_name = f'{sheet_name}', header = None)
    return df



def last_index_not_NaN_of_row(arr):
    for i in range(len(arr) - 1):
        if isnan(arr[i]):
            return i - 1
    return -1           # There is a row in which there are not nan values


def find_pair_of_zeros(arr):
    for i in range(len(arr) - 1):               # Loop until the second to last element
        if arr[i] == 0 and arr[i + 1] == 0:
            return i                            # Return the index of the first zero in the pair
    return -1                                   # Return -1 if no pair of consecutive zeros is found



def obtain_route(j, sheet_df):
    row = list(sheet_df.iloc[j])
    # Sabemos que siempre hay dos ceros adyacentes (el final de la ruta y el tiempo del primer depósito)
    zero_pos = find_pair_of_zeros(row)

    visited_nodes = int(row[0])      # otros que no son depósitos
    route = row[1:zero_pos+1]   # +1 porque no incluye el último índice
    route = [int(x) for x in route]

    capacity_used = row[last_index_not_NaN_of_row(row)]

    return visited_nodes, route, capacity_used



def info_of_all_routes(path, sheet_name):
    sheet_df = read_instance_solution(path, sheet_name)

    constructive_number_of_routes = sheet_df[0][0]                   # col 0, row 0 indicates K = number of vehicles
    constructive_total_distance = sheet_df[1][0]
    constructive_execution_time = sheet_df[2][0]


    initial_solution = []
    for i in range(1, constructive_number_of_routes + 1, 1):         # Exclude the first row
        visited_nodes, route, capacity_used = obtain_route(i, sheet_df)
        initial_solution.append({'number_of_visited_nodes': visited_nodes, 'route_objects' : [], 'total_capacity_used' : capacity_used, 'route_index' : i, 'route_indexes' : route})

    return initial_solution, constructive_total_distance, constructive_execution_time




# path = 'C:\\Users\\thomm\\Documents\\GitHub\\heuristica\\2-local-search\\constructive-results\\VRPTW_tm_ACO.xlsx'
# sheet_name = 'VRPTW1'

# initial_solution = info_of_all_routes(path, sheet_name)
# print(initial_solution)


# print(initial_solution)
