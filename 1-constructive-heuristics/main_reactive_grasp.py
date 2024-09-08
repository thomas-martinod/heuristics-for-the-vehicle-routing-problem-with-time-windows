import os
import time
from openpyxl import Workbook
from distance_finder import travel_times_matrix, calculate_total_distance
from file_reader import read_txt_file
from file_writer import save_to_excel_in_folder
from visualization import save_routes_plot_in_folder
from reactive_grasp import reactive_grasp_route_selection  # New import


def vrptw_solver(directory_path, output_filename):
    start_time = time.time()
    wb = Workbook()
    wb.remove(wb.active)

    for filename in os.listdir(directory_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(directory_path, filename)
            n, Q, nodes = read_txt_file(file_path)
            times = travel_times_matrix(nodes)

            # Apply Reactive GRASP
            routes, best_distance = reactive_grasp_route_selection(nodes, Q, times)
            computation_time = time.time() - start_time
            print(f"Solution for {filename}: Total Distance = {best_distance}")

            # Save Excel results
            sheet_name = filename.split('.')[0]
            save_to_excel_in_folder(wb, sheet_name, routes, best_distance, computation_time, times, output_filename)

            # Save the figure in 'figures/grasp' folder
            save_routes_plot_in_folder(routes, f"{sheet_name}.png", folder="figures/grasp")

    wb.save(os.path.join('results', output_filename))
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Tiempo total de ejecución: {elapsed_time:.4f} segundos")


# Set paths for the VRPTW instances and output files
directory_path = 'VRPTW Instances'
output_filename = "VRPTW_Reactive_GRASP.xlsx"
vrptw_solver(directory_path, output_filename)
