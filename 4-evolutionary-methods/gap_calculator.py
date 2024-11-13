import pandas as pd
from openpyxl import Workbook

# Function to read lower bounds
def read_lower_bounds(path, sheet_name):
    xls = pd.ExcelFile(path)
    df = pd.read_excel(xls, sheet_name = f'{sheet_name}', header = None)
    routes_LB = df[1]
    distance_LB = df[2]
    return list(routes_LB), list(distance_LB)


def calculate_GAP(LB, actual_value):
    return abs(LB - actual_value) / LB


def write_GAP_excel(wb, LB_K, K, LB_distances, distances, ex, sheet_name):
    # Create a new sheet in the workbook with the provided sheet name
    ws = wb.create_sheet(title=sheet_name)

    ws.append(['Instances', 'LB_K', 'K', 'GAP_K', 'LB_D', 'D', 'GAP_D', 'Execution time (ms)'])
    for i in range(len(K)):
        ws.append([f'VRPTW{i+1}', LB_K[i], K[i], calculate_GAP(LB_K[i], K[i]), LB_distances[i], distances[i], calculate_GAP(LB_distances[i], distances[i]), ex[i]])


