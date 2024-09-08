class Node:
    def __init__(self, index, x, y, q, inf, sup, t_serv):
        self.index = index
        self.x = x
        self.y = y
        self.q = q
        self.inf = inf
        self.sup = sup
        self.t_serv = t_serv

def read_txt_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        first_line = lines[0].strip().split()
        n = int(first_line[0])
        Q = int(first_line[1])
        nodes = []
        for line in lines[1:]:
            parts = list(map(int, line.strip().split()))
            node = Node(parts[0], parts[1], parts[2], parts[3], parts[4], parts[5], parts[6])
            nodes.append(node)
    return n, Q, nodes
