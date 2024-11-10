import gurobipy as gp
from gurobipy import GRB
from file_reader import read_txt_file

# Cargar datos desde el archivo de texto
file_path = 'ruta_al_archivo.txt'  # Cambia esto por la ruta a tu archivo de entrada
n, Q, nodes = read_txt_file(file_path)

# Obtener los clientes (todos los nodos excepto el depósito)
depot = 0
customers = [node.index for node in nodes if node.index != depot]
locations = [node.index for node in nodes]
connections = [(i, j) for i in locations for j in locations if i != j]

# Crear diccionario de coordenadas y de costos de distancia euclidiana entre nodos
coords = {node.index: (node.x, node.y) for node in nodes}
costs = {
    (i, j): int(((coords[i][0] - coords[j][0])**2 + (coords[i][1] - coords[j][1])**2)**0.5)
    for i, j in connections
}

# Crear modelo para el VRPTW
model = gp.Model("VRPTW")

# Variables binarias x[i, j] = 1 si el vehículo va de nodo i a j, 0 en caso contrario
x = model.addVars(connections, vtype=GRB.BINARY, name="x")

# Función objetivo: minimizar la suma de los costos de conexión
model.setObjective(x.prod(costs), GRB.MINIMIZE)

# Restricciones de flujo: cada cliente debe tener una entrada y una salida
model.addConstrs((x.sum('*', j) == 1 for j in customers), name="entrada")
model.addConstrs((x.sum(i, '*') == 1 for i in customers), name="salida")

# Limitar el número de vehículos que salen del depósito
model.addConstr(x.sum(depot, '*') <= n, name="maxNumVehicles")

# Cargar las demandas, ventanas de tiempo y tiempos de servicio
demands = {node.index: node.q for node in nodes}
timeWindows = {node.index: (node.inf, node.sup) for node in nodes}
serviceTimes = {node.index: node.t_serv for node in nodes}

# Modelo de carga usando Big-M
y = model.addVars(locations, lb=0, ub=Q, name="y")
y[depot].UB = 0  # El depósito tiene carga cero

model.addConstrs(
    (y[i] + demands[j] <= y[j] + Q * (1 - x[i, j])
     for i in locations for j in customers if i != j),
    name="loadBigM1"
)
model.addConstrs(
    (y[i] + demands[j] >= y[j] - (Q - demands[i] - demands[j]) * (1 - x[i, j])
     for i in locations for j in customers if i != j),
    name="loadBigM2"
)

# Modelo de tiempo usando Big-M
t = model.addVars(locations, name="t")
for i in locations:
    t[i].LB = timeWindows[i][0]
    t[i].UB = timeWindows[i][1]

model.addConstrs(
    (t[i] + serviceTimes[i] + costs[i, j] <= t[j] + (timeWindows[i][1] + serviceTimes[i] + costs[i, j] - timeWindows[j][0]) * (1 - x[i, j])
     for i in locations for j in customers if i != j),
    name="timeBigM"
)

# Optimización
model.optimize()

# Extraer y mostrar las rutas
if model.status == GRB.OPTIMAL:
    for i, j in connections:
        if x[i, j].X > 0.5:
            print(f"Ruta de {i} a {j} con costo {costs[i, j]}")
else:
    print("No se encontró solución óptima.")
