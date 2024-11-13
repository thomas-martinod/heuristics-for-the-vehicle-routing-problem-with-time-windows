import os
import matplotlib.pyplot as plt

def plot_routes(routes):
    plt.figure(figsize=(8, 8))

    # Iterate through each route to plot
    for i, route in enumerate(routes):
        x_coords = [node.x for node in route]
        y_coords = [node.y for node in route]

        # Plot the route with a line and markers for the nodes
        plt.plot(x_coords, y_coords, marker='o', label=f'Route {i + 1}')

        # Annotate the node numbers (customers)
        for node in route:
            plt.text(node.x, node.y, f'{node.index}', fontsize=12, ha='right')

    # Configure the graph
    plt.title('Visualization of VRPTW Routes')
    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.grid(True)
    plt.legend()

def save_routes_plot_in_folder(routes, filename, folder):
    # Ensure the folder exists (create it if it doesn't)
    if not os.path.exists(folder):
        os.makedirs(folder)

    # Plot the routes without displaying the plot
    plot_routes(routes)

    # Save the plot to the specified folder and close the plot
    filepath = os.path.join(folder, filename)
    plt.savefig(filepath)
    plt.close()
