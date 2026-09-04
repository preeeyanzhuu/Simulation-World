GRID_SIZE = 20

def create_grid():
    grid = []       # grid[row][col]  →  row = y (vertical), col = x (horizontal)
    for row in range(GRID_SIZE):
        new_row =[]
        for col in range(GRID_SIZE):
            new_row.append({"type" : "empty"})
        grid.append(new_row)
    return grid 

if __name__ == "__main__":
    g = create_grid()
    print(g[0])       # print just the first row
    print(len(g))      # print how many rows total

    g[5][5] = {"type": "road"}
    g[10][10] = {"type": "building" , "name" : "hospital"}
    print(g[5][5])
    print(g[10][10])
