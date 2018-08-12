from assets import graph
from collections import deque

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


visited = set()