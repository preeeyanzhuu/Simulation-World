GRID_SIZE = 20

def create_grid():
    grid = []       
    for row in range(GRID_SIZE):
        new_row =[]
        for col in range(GRID_SIZE):
            new_row.append({"type" : "empty"})
        grid.append(new_row)
    return grid 


