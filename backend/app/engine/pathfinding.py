import heapq


GRID_SIZE = 20 

def heuristic(a,b):
    return abs(a[0]- b[0])+ abs(a[1]- b[1])



def get_neighbors(cell , grid):
    row =  cell[0]
    col =  cell[1]
    
    candidates = [
        (row + 1, col),
        (row - 1, col),
        (row, col + 1),
        (row, col - 1)
    ]
    
    valid_neighbors = []
    
    for n in candidates:
        if 0<= n[0]< GRID_SIZE:
            if 0<= n[1]< GRID_SIZE:
                if grid[n[0]][n[1]]["type"] != "building":
                    valid_neighbors.append(n)
        
    
    return valid_neighbors

def astar(start,goal,grid):
    open_set =[]
    heapq.heappush(open_set,(0,start))
    came_from ={}
    g_score = {start: 0}

    while open_set:
        current_f , current =heapq.heappop(open_set)

        if current == goal:
            path = [current]
            while current in came_from:
                current = came_from[current]
                path.append(current)
            path.reverse()
            return path 
        
        for neighbor in get_neighbors(current,grid):
            tentative_g = g_score[current]+1

            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                g_score[neighbor] = tentative_g
                came_from[neighbor] = current 
                f_score = tentative_g + heuristic(neighbor,goal)
                heapq.heappush(open_set,(f_score,neighbor))

             




