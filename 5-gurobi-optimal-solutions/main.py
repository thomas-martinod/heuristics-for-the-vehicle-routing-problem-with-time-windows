import gurobipy as gp
from gurobipy import GRB
from file_reader import read_txt_file
import math

# Cargar datos desde el archivo
file_path = 'VRPTW Instances/VRPTW17.txt'  # Cambia esto por la ruta a tu archivo de entrada
n, Q, nodes = read_txt_file(file_path)

# Determinar el número inicial de vehículos necesario
total_demand = sum(node.q for node in nodes if node.index != 0)
K = math.ceil(total_demand / Q) # Número inicial de vehículos

# Definir parámetros y variables
depot = 0
customers = [node.index for node in nodes if node.index != depot]
locations = [node.index for node in nodes]
connections = [(i, j) for i in locations for j in locations if i != j]

# Diccionario de costos de distancia euclidiana entre nodos
coords = {node.index: (node.x, node.y) for node in nodes}
costs = {
    (i, j): ((coords[i][0] - coords[j][0])**2 + (coords[i][1] - coords[j][1])**2)**0.5
    for i, j in connections
}

# Crear modelo para VRPTW
model = gp.Model("VRPTW")

# Variables de decisión
x = model.addVars(connections, range(1, K + 1), vtype=GRB.BINARY, name="x")  # x[i, j, k] = 1 si el vehículo k viaja de i a j
y = model.addVars(locations, range(1, K + 1), vtype=GRB.BINARY, name="y")    # y[i, k] = 1 si el vehículo k sirve al cliente i
t = model.addVars(locations, name="t")                                        # t[j] es el tiempo de llegada al nodo j
w = model.addVars(customers, lb=0, name="w")                                  # Tiempo de espera en cada cliente

# Función objetivo: minimizar la distancia total recorrida
distance_objective = gp.quicksum(costs[i, j] * x[i, j, k] for i, j in connections for k in range(1, K + 1))
model.setObjective(distance_objective, GRB.MINIMIZE)

# Restricciones

# 1. Restricción de entrada y salida para cada cliente
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

# Nueva restricción: Cada vehículo puede salir del depósito solo una vez
model.addConstrs(
    (gp.quicksum(x[depot, j, k] for j in customers) <= 1 for k in range(1, K + 1)),
    name="salida_unica_deposito"
)

# Nueva restricción: Cada vehículo debe regresar al depósito solo una vez
model.addConstrs(
    (gp.quicksum(x[i, depot, k] for i in customers) <= 1 for k in range(1, K + 1)),
    name="retorno_unico_deposito"
)

# 2. Restricción de unicidad: cada cliente debe ser atendido por exactamente un vehículo
model.addConstrs(
    (gp.quicksum(y[i, k] for k in range(1, K + 1)) == 1 for i in customers),
    name="unicidad"
)

# 3. Restricción de capacidad: la carga total de cada vehículo no debe exceder su capacidad
model.addConstrs(
    (gp.quicksum(y[i, k] * nodes[i].q for i in locations) <= Q for k in range(1, K + 1)),
    name="capacidad"
)

# 4. Restricción de inicio en el depósito: cada vehículo debe partir del depósito
model.addConstr(
    gp.quicksum(y[depot, k] for k in range(1, K + 1)) == K,
    name="inicio_deposito"
)

# 5. Restricciones de tiempo entre clientes
model.addConstrs(
    (t[i] + nodes[i].t_serv + costs[i, j] <= t[j] + (1 - x[i, j, k]) * 1e6
     for i in locations for j in customers for k in range(1, K + 1) if i != j),
    name="tiempo_ventanas"
)

# 6. Restricción de ventanas de tiempo para cada cliente
model.addConstrs(
    (nodes[j].inf <= t[j] for j in customers),
    name="ventana_inicio"
)

model.addConstrs(
    (t[j] <= nodes[j].sup for j in customers),
    name="ventana_fin"
)

# 7. Restricción de tiempo de espera
model.addConstrs(
    (w[j] >= nodes[j].inf - (t[i] + nodes[i].t_serv + costs[i, j]) * x[i, j, k]
     for i in locations for j in customers for k in range(1, K + 1) if i != j),
    name="tiempo_espera"
)

# Optimizar el modelo
model.optimize()

print('Optimización completada')

# # Imprimir las conexiones activas como paso de depuración
# print("Conexiones activas en la solución óptima:")
# for (i, j, k) in x.keys():
#     if x[i, j, k].X > 0.5:
#         print(f"Vehículo {k} viaja de {i} a {j}")

# Imprimir solución de rutas
if model.status == GRB.OPTIMAL:
    rutas = []
    visitados = set([depot])  # Mantiene el registro de nodos visitados

    for k in range(1, K + 1):  # Iterar para cada vehículo
        ruta = [depot]
        nodo_actual = depot

        while len(visitados) < len(locations):  # Mientras no se hayan visitado todos los clientes
            siguiente_nodo = None

            # Buscar el siguiente nodo en la ruta para el vehículo k
            for j in locations:
                if (nodo_actual, j, k) in x and x[nodo_actual, j, k].X > 0.5 and j not in visitados:
                    siguiente_nodo = j
                    break

            if siguiente_nodo is None:
                # Si no se encuentra un siguiente nodo, el vehículo regresa al depósito y se termina la ruta actual
                ruta.append(depot)
                rutas.append(ruta)  # Guardar la ruta
                break  # Salir del bucle para el vehículo k

            # Agregar el siguiente nodo a la ruta y marcarlo como visitado
            ruta.append(siguiente_nodo)
            visitados.add(siguiente_nodo)
            nodo_actual = siguiente_nodo

        # Si todos los clientes ya fueron visitados y la ruta aún no ha regresado al depósito
        if ruta[-1] != depot:
            ruta.append(depot)
            rutas.append(ruta)

    # Mostrar cada ruta en el formato solicitado
    for i, ruta in enumerate(rutas, start=1):
        print(f"Ruta {i}: {' -> '.join(map(str, ruta))}")
else:
    print("No se encontró solución óptima.")

