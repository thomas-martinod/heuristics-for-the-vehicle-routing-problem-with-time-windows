import gurobipy as gp
from gurobipy import GRB
from file_reader import read_txt_file
from file_writer import save_to_excel
import math
import utilities as ut
import openpyxl
import time

# Directorio de las instancias
instances_directory_path = 'VRPTW Instances'
# Ruta de salida para el archivo Excel de resultados
excel_path = '5-gurobi-optimal-solutions/gurobi-results/gurobi-results-12.xlsx'

# Crear el archivo de Excel donde se guardarán los resultados
workbook = openpyxl.Workbook()
workbook.remove(workbook.active)  # Elimina la hoja vacía inicial

for file_index in range(12, 13):  # Itera sobre los 18 archivos
    print(f'\nVamos con VRPTW{file_index}')
    # Configuración de la instancia
    sheet_name = f'VRPTW{file_index}'
    file_path = f'{instances_directory_path}/{sheet_name}.txt'
    n, Q, nodes = read_txt_file(file_path)

    # Crear un diccionario que mapea los índices de los nodos a objetos Node
    nodes_dict = {node.index: node for node in nodes}

    # Determinar cotas para el número de vehículos
    total_demand = sum(node.q for node in nodes if node.index != 0)
    K_min = math.ceil(total_demand / Q)  # Cota inferior
    K_max = n  # Cota superior

    # Definir parámetros y variables constantes
    depot = 0
    customers = [node.index for node in nodes if node.index != depot]
    locations = [node.index for node in nodes]
    connections = [(i, j) for i in locations for j in locations if i != j]

    # Construir la matriz completa de distancias (distances)
    num_nodes = len(nodes)
    distances = [[0] * num_nodes for _ in range(num_nodes)]
    coords = {node.index: (node.x, node.y) for node in nodes}

    for i, j in connections:
        distances[i][j] = ((coords[i][0] - coords[j][0])**2 + (coords[i][1] - coords[j][1])**2)**0.5

    # Bucle para encontrar el mínimo valor de K que produce una solución factible
    K = K_min
    solution_found = False

    while K <= K_max and not solution_found:
        # Crear modelo para VRPTW
        model = gp.Model("VRPTW")

        # Desactivar la salida de Gurobi
        # model.setParam('OutputFlag', 0)

        # Variables de decisión
        x = model.addVars(connections, range(1, K + 1), vtype=GRB.BINARY, name="x")
        y = model.addVars(locations, range(1, K + 1), vtype=GRB.BINARY, name="y")
        t = model.addVars(locations, name="t")
        w = model.addVars(customers, lb=0, name="w")

        # Función objetivo: minimizar la distancia total recorrida
        distance_objective = gp.quicksum(distances[i][j] * x[i, j, k] for i, j in connections for k in range(1, K + 1))
        model.setObjective(distance_objective, GRB.MINIMIZE)

        # Agregar restricciones
        model.addConstrs(
            (gp.quicksum(x[i, j, k] for i in locations if i != j) == y[j, k]
             for j in customers for k in range(1, K + 1)),
            name="entrada"
        )
        model.addConstrs(
            (gp.quicksum(x[i, j, k] for j in locations if i != j) == y[i, k]
             for i in customers for k in range(1, K + 1)),
            name="salida"
        )
        model.addConstrs(
            (gp.quicksum(x[depot, j, k] for j in customers) <= 1 for k in range(1, K + 1)),
            name="salida_unica_deposito"
        )
        model.addConstrs(
            (gp.quicksum(x[i, depot, k] for i in customers) <= 1 for k in range(1, K + 1)),
            name="retorno_unico_deposito"
        )
        model.addConstrs(
            (gp.quicksum(y[i, k] for k in range(1, K + 1)) == 1 for i in customers),
            name="unicidad"
        )
        model.addConstrs(
            (gp.quicksum(y[i, k] * nodes[i].q for i in locations) <= Q for k in range(1, K + 1)),
            name="capacidad"
        )
        model.addConstr(
            gp.quicksum(y[depot, k] for k in range(1, K + 1)) == K,
            name="inicio_deposito"
        )
        model.addConstrs(
            (t[i] + nodes[i].t_serv + distances[i][j] <= t[j] + (1 - x[i, j, k]) * 1e6
             for i in locations for j in customers for k in range(1, K + 1) if i != j),
            name="tiempo_ventanas"
        )
        model.addConstrs(
            (nodes[j].inf <= t[j] for j in customers),
            name="ventana_inicio"
        )
        model.addConstrs(
            (t[j] <= nodes[j].sup for j in customers),
            name="ventana_fin"
        )
        model.addConstrs(
            (w[j] >= nodes[j].inf - (t[i] + nodes[i].t_serv + distances[i][j]) * x[i, j, k]
             for i in locations for j in customers for k in range(1, K + 1) if i != j),
            name="tiempo_espera"
        )

        # Calcular el tiempo de optimización
        start_time = time.time()
        model.optimize()

        # Verificar si se encontró una solución factible
        if model.status == GRB.OPTIMAL:
            solution_found = True
            print(f'Solución encontrada con K = {K} para {sheet_name}')

            # Recuperar las rutas y calcular la distancia total
            routes = ut.extract_routes(model, x, locations, K, depot, nodes_dict)
            total_distance = model.objVal
            computation_time = time.time() - start_time

            # Guardar los resultados en el archivo Excel
            save_to_excel(workbook, sheet_name, routes, total_distance, computation_time, distances)
        else:
            print(f'No se encontró solución factible con K = {K} para {sheet_name}')
            K += 1

    # Mensaje en caso de no encontrar solución para la instancia actual
    if not solution_found:
        print(f"No se encontró solución óptima para {sheet_name} en el rango de K especificado.")

# Guardar el archivo Excel con los resultados de todas las instancias
workbook.save(excel_path)
print(f"Resultados guardados en {excel_path}")
