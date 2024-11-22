# Define a class for representing a Node (or customer) in the VRPTW problem
class Node:
    def __init__(self, index, x, y, q, inf, sup, t_serv):
        self.index = index  # Node ID
        self.x = x          # X-coordinate
        self.y = y          # Y-coordinate
        self.q = q          # Demand
        self.inf = inf      # Earliest allowable arrival time (time window start)
        self.sup = sup      # Latest allowable arrival time (time window end)
        self.t_serv = t_serv  # Time required to serve this node



# Function to read input data from a text file and create a list of nodes
def read_txt_file(file_path):
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
