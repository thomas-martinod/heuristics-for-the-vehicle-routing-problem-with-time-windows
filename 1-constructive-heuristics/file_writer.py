import os
from openpyxl import Workbook

def save_to_excel_in_folder(workbook, sheet_name, routes, total_distance, computation_time, times, filename, folder="results"):
    # Ensure the 'results' folder exists
    if not os.path.exists(folder):
        os.makedirs(folder)

    # Save data to Excel
    save_to_excel(workbook, sheet_name, routes, total_distance, computation_time, times)

    # Save the workbook to the desired folder
    filepath = os.path.join(folder, filename)
    workbook.save(filepath)


def save_to_excel(workbook, sheet_name, routes, total_distance, computation_time, times):
    ws = workbook.create_sheet(title=sheet_name)
    num_vehicles = len(routes)
    ws.append([num_vehicles, round(total_distance, 0), round(computation_time, 0)])
    for route in routes:
        route_nodes = [0]
        arrival_times = []
        current_time = 0
        total_load = 0
        for j in range(1, len(route)):
            current_time += times[route[j-1].index][route[j].index]
            if current_time < route[j].inf:
                current_time = route[j].inf
            arrival_times.append(round(current_time, 3))
            total_load += route[j].q
            route_nodes.append(route[j].index)
            current_time += route[j].t_serv
        route_nodes.append(0)
        ws.append([len(route_nodes) - 3] + route_nodes + arrival_times + [total_load])
