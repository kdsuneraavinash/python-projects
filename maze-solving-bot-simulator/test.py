graph = {
    0: [1],
    1: [14, 2, 0],
    2: [1, 3, 7, 8],
    3: [2, 5, 4],
    4: [3, 6, 13],
    5: [3, 6],
    6: [4, 5],
    7: [2],
    8: [2, 12, 9],
    9: [11, 10, 8],
    10: [9],
    11: [9],
    12: [8],
    13: [4],
    14: [1]
}

visited = set()
def dfs(node):
    for neighbor in graph[node]:
        if neighbor not in visited:
            visited.add(neighbor)
            dfs(neighbor)

def dfs_iter(node):
    stack = [node]
    while stack:
        next_node = stack.pop()
        visited.add(next_node)
        for neighbor in graph[next_node]:
            if neighbor not in visited:
                stack.append(neighbor)

def dfs_iter_rec(node):
    stack = [node]
    while stack:
        print(stack)
        next_node = stack[-1]
        visited.add(next_node)
        for neighbor in graph[next_node]:
            if neighbor not in visited:
                stack.append(neighbor)
                break
        else:
            stack.pop()

dfs_iter_rec(0)
print(sorted(visited))
