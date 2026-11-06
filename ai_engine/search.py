from collections import deque
import heapq


def bfs(graph, start):
    visited = set()
    queue = deque([start])
    order = []
    while queue:
        node = queue.popleft()
        if node in visited:
            continue
        visited.add(node)
        order.append(node)
        for neighbor in graph.neighbors(node):
            if neighbor not in visited:
                queue.append(neighbor)
    return {"algorithm": "BFS", "order": order, "visited": order, "nodes_explored": len(order)}


def dfs(graph, start):
    visited = set()
    order = []

    def visit(node):
        if node in visited:
            return
        visited.add(node)
        order.append(node)
        for neighbor in graph.neighbors(node):
            visit(neighbor)

    visit(start)
    return {"algorithm": "DFS", "order": order, "visited": order, "nodes_explored": len(order)}


def greedy_best_first(graph, start, destinations, heuristic):
    queue = []
    serial = 0
    start_score = heuristic(start) if start in graph.graph else heuristic("Destination root")
    heapq.heappush(queue, (-start_score, serial, start))
    visited = set()
    order = []
    evaluated = {}
    while queue:
        _, _, node = heapq.heappop(queue)
        if node in visited:
            continue
        visited.add(node)
        order.append(node)
        score = heuristic(node)
        evaluated[node] = round(score, 2)
        for neighbor in graph.neighbors(node):
            if neighbor not in visited:
                serial += 1
                heapq.heappush(queue, (-heuristic(neighbor), serial, neighbor))
    return {"algorithm": "Greedy Best-First Search", "order": order, "visited": list(visited),
            "nodes_explored": len(order), "heuristic_scores": evaluated}
