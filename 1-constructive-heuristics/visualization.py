import os
import matplotlib.pyplot as plt

def plot_routes(routes):
    plt.figure(figsize=(8, 8))

    # Recorremos cada ruta para graficar
    for i, route in enumerate(routes):
        x_coords = [node.x for node in route]
        y_coords = [node.y for node in route]

        # Dibujar la ruta con una línea
        plt.plot(x_coords, y_coords, marker='o', label=f'Ruta {i + 1}')

        # Anotar los números de los nodos (clientes)
        for node in route:
            plt.text(node.x, node.y, f'{node.index}', fontsize=12, ha='right')

    # Configuración del gráfico
    plt.title('Visualización de las Rutas VRPTW')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.grid(True)
    plt.legend()

def save_routes_plot_in_folder(routes, filename, folder="figures/constructive"):
    # Ensure the 'figures/constructive' folder exists
    if not os.path.exists(folder):
        os.makedirs(folder)

    # Plot the routes (using your existing plot function but without showing the plot)
    plot_routes(routes)
    
    # Save the plot to the specified folder and close the plot window
    filepath = os.path.join(folder, filename)
    plt.savefig(filepath)
    plt.close()
    print(f"Figure saved to {filepath}")
