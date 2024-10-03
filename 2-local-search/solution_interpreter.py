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
    # we know there is always two adjacent zeros (the end of the route and the time of the first deposit)
    zero_pos = find_pair_of_zeros(row)

    visited_nodes = row[0]      # other than the deposits
    route = row[1:zero_pos+1]   # +1 because it don't include the last index
    capacity_used = row[last_index_not_NaN_of_row(row)]

    return visited_nodes, route, capacity_used


def info_of_all_routes(sheet_df):
    number_of_routes = sheet_df[0][0]   # col 0, row 0 indicates K = number of vehicles

    initial_solution = []
    for i in range(1, number_of_routes + 1, 1):         # Exclude the first row
        visited_nodes, route, capacity_used = obtain_route(i, sheet_df)
        initial_solution.append({'number_of_visited_nodes': visited_nodes, 'route' : route, 'total_capacity_used' : capacity_used})

    return initial_solution




# path = 'C:\\Users\\thomm\\Documents\\GitHub\\heuristica\\2-local-search\\constructive-results\\VRPTW_tm_ACO.xlsx'
# sheet_name = 'VRPTW1'

# df = read_instance_solution(path, sheet_name)
# initial_solution = info_of_all_routes(df)

# print(initial_solution)
