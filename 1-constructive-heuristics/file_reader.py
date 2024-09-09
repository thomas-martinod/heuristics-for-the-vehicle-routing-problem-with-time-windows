# Define a class for representing a Node (or customer) in the VRPTW problem
class Node:
    def __init__(self, index, x, y, q, inf, sup, t_serv):
        """
        Initialize a node with the following attributes:
        :param index: Unique identifier of the node (e.g., customer number).
        :param x: X-coordinate of the node's location.
        :param y: Y-coordinate of the node's location.
        :param q: Demand of the node (how much the vehicle must deliver or pick up).
        :param inf: Time window lower bound (earliest time the vehicle can arrive).
        :param sup: Time window upper bound (latest time the vehicle can arrive).
        :param t_serv: Service time (how long it takes to serve the node).
        """
        self.index = index  # Node ID
        self.x = x          # X-coordinate
        self.y = y          # Y-coordinate
        self.q = q          # Demand
        self.inf = inf      # Earliest allowable arrival time (time window start)
        self.sup = sup      # Latest allowable arrival time (time window end)
        self.t_serv = t_serv  # Time required to serve this node

# Function to read input data from a text file and create a list of nodes
def read_txt_file(file_path):
    """
    Read a text file that describes the VRPTW problem and extract nodes.
    :param file_path: Path to the input file.
    :return: Number of nodes (n), vehicle capacity (Q), and a list of Node objects.
    """
    with open(file_path, 'r') as file:
        lines = file.readlines()  # Read all lines from the file

        # First line contains the number of nodes (n) and vehicle capacity (Q)
        first_line = lines[0].strip().split()
        n = int(first_line[0])  # Number of nodes
        Q = int(first_line[1])  # Vehicle capacity

        nodes = []  # Initialize an empty list to store Node objects

        # For each line representing a node, create a Node object and append it to the list
        for line in lines[1:]:
            parts = list(map(int, line.strip().split()))  # Convert each line into a list of integers
            node = Node(parts[0], parts[1], parts[2], parts[3], parts[4], parts[5], parts[6])
            nodes.append(node)  # Add the node to the list

    return n, Q, nodes  # Return the number of nodes, vehicle capacity, and list of nodes
