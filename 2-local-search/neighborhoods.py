from feasibility import is_feasible
from calculate_


def interchange_two_positions(x):
    x = x[1:-1]  # Remove the deposits. If the remaining list has n elements, we will generate nC2 lists.
    best = x
    R = len(x)
    for i in range(R):
        for j in range(i+1, R):
            x_prime = x.copy()  # Create a copy of x before making changes
            x_prime = swap_two(x_prime, i, j)
            if is_feasible():
                print(x_prime)
                if fo(x_prime) < fo(x):
                    best = x_prime
    return best

def swap_two(arr, i,j ):
    aux = arr[i]
    arr[i] = arr[j]
    arr[j] = aux
    return arr

