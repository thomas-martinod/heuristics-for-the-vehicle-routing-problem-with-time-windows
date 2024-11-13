

def genetic_algorithm(initial_routes, times, Q, remaining_time):
    """
    Implementación del algoritmo genético para mejorar la solución.
    """
    start_time = time.time()  # Definir el tiempo de inicio

    population_size = 150
    crossover_rate = 0.8
    mutation_rate = 0.09
    generations = 1000

    # Generar la población inicial
    population = generate_initial_population(initial_routes, population_size)

    # Evaluar la población inicial
    fitness_values = evaluate_population(population, times, Q)

    # Ejecutar el ciclo de generaciones del algoritmo genético
    for generation in range(generations):
        # Verificar si se ha excedido el tiempo límite
        if time.time() - start_time > remaining_time:
            print(f"Tiempo límite alcanzado en la generación {generation}")
            break

        # Seleccionar padres para el cruce
        parents = select_parents(population, fitness_values)

        # Realizar el cruce
        offspring = crossover(parents, crossover_rate)

        # Aplicar mutación
        mutated_offspring = mutate(offspring, mutation_rate)

        # Evaluar la descendencia
        offspring_fitness = evaluate_population(mutated_offspring, times, Q)

        # Seleccionar sobrevivientes
        population = select_survivors(population, mutated_offspring, offspring_fitness, times, Q)

        # Evaluar la nueva población
        fitness_values = evaluate_population(population, times, Q)

    # Obtener la mejor solución encontrada
    best_solution = get_best_solution(population, fitness_values)
    return best_solution

def generate_initial_population(initial_routes, population_size):
    """
    Genera una población inicial de rutas aleatorias basadas en la solución inicial.
    """
    population = []
    for _ in range(population_size):
        # Realiza una copia aleatoria de la solución inicial o variaciones de ella
        individual = random.sample(initial_routes, len(initial_routes))
        population.append(individual)
    return population

def evaluate_population(population, times, Q):
    """
    Evalúa la población calculando la aptitud (fitness) de cada individuo.
    Cuanto menor sea el costo, mejor es la solución.
    """
    fitness_values = []
    epsilon = 1e-6  # Pequeño valor para evitar división por cero y problemas numéricos
    
    # Calcular el total_cost para cada individuo
    total_costs = []
    for individual in population:
        total_cost = calculate_total_cost(individual, times, alpha=20.0, beta=200.0)  # Ajusta alpha y beta según sea necesario
        total_costs.append(total_cost)
    
    # Encontrar el costo máximo y mínimo para normalizar
    max_cost = max(total_costs)
    min_cost = min(total_costs)
    cost_range = max_cost - min_cost + epsilon  # Añadimos epsilon para evitar división por cero si max_cost == min_cost
    
    # Calcular el fitness normalizado inverso (mejor costo => mayor fitness)
    for total_cost in total_costs:
        # Normalizar el costo entre 0 y 1
        normalized_cost = (total_cost - min_cost) / cost_range
        # Invertir el costo normalizado para que menor costo dé mayor fitness
        fitness = 1 / (normalized_cost + epsilon)
        fitness_values.append(fitness)
    
    return fitness_values

def select_parents(population, fitness_values):
    """
    Selecciona a los padres utilizando el método de ruleta o selección por torneo.
    """
    total_fitness = sum(fitness_values)
    selection_probs = [fitness / total_fitness for fitness in fitness_values]
    parents = random.choices(population, weights=selection_probs, k=2)  # Selecciona 2 padres
    return parents

def crossover(parents, crossover_rate):
    """
    Realiza el cruce de dos padres para generar descendencia.
    """
    if random.random() < crossover_rate:
        # Cruza dos padres y genera un hijo
        crossover_point = random.randint(1, len(parents[0]) - 1)
        child1 = parents[0][:crossover_point] + [x for x in parents[1] if x not in parents[0][:crossover_point]]
        child2 = parents[1][:crossover_point] + [x for x in parents[0] if x not in parents[1][:crossover_point]]
        return [child1, child2]
    else:
        # No hay cruce, los padres pasan directamente a la siguiente generación
        return parents

def mutate(offspring, mutation_rate):
    """
    Realiza una mutación aleatoria en la descendencia.
    """
    for child in offspring:
        if random.random() < mutation_rate:
            # Realiza una mutación al cambiar el orden de dos rutas
            idx1, idx2 = random.sample(range(len(child)), 2)
            child[idx1], child[idx2] = child[idx2], child[idx1]
    return offspring

def get_best_solution(population, fitness_values):
    """
    Devuelve la mejor solución de la población, priorizando primero el menor fitness (distancia total) y, 
    en caso de empate, el menor número de rutas.
    """
    # Validaciones
    if not population or not fitness_values or len(population) != len(fitness_values):
        raise ValueError("La población y los valores de fitness deben ser listas no vacías de igual longitud.")
    
    # Encontrar el mínimo valor de fitness
    min_fitness = min(fitness_values)
    # Indices de individuos con el mínimo fitness
    best_indices = [i for i, fitness in enumerate(fitness_values) if fitness == min_fitness]
    
    if len(best_indices) == 1:
        # Solo hay un individuo con el mejor fitness
        best_idx = best_indices[0]
    else:
        # Si hay múltiples soluciones óptimas en términos de fitness, considerar el número de rutas
        min_routes = min(len(population[i]) for i in best_indices)
        # Indices de individuos con el menor número de rutas entre los mejores fitness
        candidates = [i for i in best_indices if len(population[i]) == min_routes]
        
        if len(candidates) == 1:
            # Solo hay un individuo con el mejor fitness y menor número de rutas
            best_idx = candidates[0]
        else:
            # Si aún hay empate, seleccionamos el primer candidato
            best_idx = candidates[0]
    
    return population[best_idx]

def select_survivors(population, offspring, fitness_values, times, Q):
    """
    Selecciona a los mejores individuos (padres + descendencia) para formar la nueva población.
    """
    combined_population = population + offspring
    combined_fitness = evaluate_population(combined_population, times, Q)
    
    # Selecciona los mejores individuos (top k) para sobrevivir
    survivors_idx = sorted(range(len(combined_fitness)), key=lambda i: combined_fitness[i], reverse=True)[:len(population)]
    survivors = [combined_population[i] for i in survivors_idx]
    return survivors

