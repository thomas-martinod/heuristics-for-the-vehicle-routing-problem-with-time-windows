import os
from openpyxl import Workbook


def save_to_excel(workbook, sheet_name, routes, total_distance, computation_time, times):
    ws = workbook.create_sheet(title=sheet_name)
    num_vehicles = len(routes)
    
    # Primera fila con m, distancia total, y tiempo de cómputo redondeado
    ws.append([num_vehicles, round(total_distance, 3), round(computation_time)])
    
    # Filas para cada vehículo
    for route in routes:
        route_nodes = [0]  # Empezamos con el depósito (nodo 0)
        arrival_times = []
        current_time = 0
        total_load = 0
        
        # Para cada cliente en la ruta (omitimos el depósito al principio)
        for j in range(1, len(route)):
            current_time += times[route[j-1].index][route[j].index]  # Tiempo de viaje entre nodos
            if current_time < route[j].inf:
                current_time = route[j].inf  # Ajustar por la ventana de tiempo
            arrival_times.append(round(current_time, 3))  # Agregamos el tiempo de llegada
            total_load += route[j].q  # Carga total acumulada
            route_nodes.append(route[j].index)  # Agregamos el nodo visitado a la ruta
            current_time += route[j].t_serv  # Añadimos el tiempo de servicio
        
        # Agregamos de nuevo el depósito al final de la ruta
        route_nodes.append(0)
        
        # Formato: Número de nodos (sin contar el depósito), ruta, tiempos de llegada, carga total
        num_customers = len(route_nodes) - 3  # No contamos los dos depósitos (inicio y fin)
        ws.append([num_customers] + route_nodes + arrival_times + [total_load])