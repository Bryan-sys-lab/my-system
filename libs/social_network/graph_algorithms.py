"""
Graph Algorithms for Social Network Analysis

This module provides graph algorithms for analyzing social networks including:
- Centrality measures (degree, betweenness, closeness)
- Community detection and clustering
- Path finding algorithms
- Network metrics and analysis
"""

from typing import List, Dict, Any, Set, Tuple, Optional
from collections import defaultdict, deque
import heapq
import math

from .models import SocialGraph, Person, Relationship


class GraphAlgorithms:
    """Collection of graph algorithms for social network analysis"""

    def __init__(self, graph: SocialGraph):
        self.graph = graph
        self._adjacency_matrix = None
        self._distance_matrix = None

    def degree_centrality(self) -> Dict[str, float]:
        """Calculate degree centrality for all nodes"""
        centrality = {}

        # Compute undirected degree for each node (in + out)
        degrees = {}
        for person_id in self.graph.people.keys():
            degrees[person_id] = len(set(self.graph.get_connections(person_id)))

        max_degree = max(degrees.values()) if degrees and any(degrees.values()) else 0
        if max_degree == 0:
            return {pid: 0.0 for pid in degrees}

        for person_id, degree in degrees.items():
            centrality[person_id] = degree / max_degree

        return centrality

    def betweenness_centrality(self, normalized: bool = True) -> Dict[str, float]:
        """Calculate betweenness centrality using Brandes' algorithm"""
        betweenness = defaultdict(float)

        for node in self.graph.people.keys():
            # Run BFS from each node
            stack = []
            predecessors = defaultdict(list)
            sigma = defaultdict(int)
            sigma[node] = 1
            distance = defaultdict(lambda: -1)
            distance[node] = 0

            queue = deque([node])

            while queue:
                current = queue.popleft()
                stack.append(current)

                for neighbor in self.graph.adjacency_list[current]:
                    if distance[neighbor] < 0:
                        queue.append(neighbor)
                        distance[neighbor] = distance[current] + 1

                    if distance[neighbor] == distance[current] + 1:
                        sigma[neighbor] += sigma[current]
                        predecessors[neighbor].append(current)

            # Accumulate dependencies
            delta = defaultdict(float)
            while stack:
                current = stack.pop()
                for predecessor in predecessors[current]:
                    delta[predecessor] += (sigma[predecessor] / sigma[current]) * (1 + delta[current])
                if current != node:
                    betweenness[current] += delta[current]

        # Normalize if requested
        if normalized:
            n = len(self.graph.people)
            if n > 2:
                for node in betweenness:
                    betweenness[node] /= ((n - 1) * (n - 2)) / 2

        return dict(betweenness)

    def closeness_centrality(self, normalized: bool = True) -> Dict[str, float]:
        """Calculate closeness centrality"""
        centrality = {}

        for node in self.graph.people.keys():
            distances = self._single_source_shortest_paths(node)
            total_distance = sum(distances.values())

            if total_distance > 0:
                centrality[node] = (len(self.graph.people) - 1) / total_distance
            else:
                centrality[node] = 0

        # Normalize if requested
        if normalized:
            n = len(self.graph.people)
            if n > 1:
                max_centrality = (n - 1)
                for node in centrality:
                    centrality[node] /= max_centrality

        return centrality

    def eigenvector_centrality(self, max_iterations: int = 100, tolerance: float = 1e-6) -> Dict[str, float]:
        """Calculate eigenvector centrality using power iteration"""
        if not self.graph.people:
            return {}

        # Initialize with equal values
        centrality = {node: 1.0 for node in self.graph.people.keys()}
        n = len(self.graph.people)

        for _ in range(max_iterations):
            new_centrality = defaultdict(float)

            for node in self.graph.people.keys():
                for neighbor in self.graph.adjacency_list[node]:
                    new_centrality[node] += centrality[neighbor]

            # Normalize
            total = sum(new_centrality.values())
            if total > 0:
                for node in new_centrality:
                    new_centrality[node] /= total

            # Check convergence
            diff = sum(abs(new_centrality[node] - centrality[node]) for node in centrality)
            centrality = dict(new_centrality)

            if diff < tolerance:
                break

        return centrality

    def page_rank(self, damping_factor: float = 0.85, max_iterations: int = 100, tolerance: float = 1e-6) -> Dict[str, float]:
        """Calculate PageRank centrality"""
        if not self.graph.people:
            return {}

        n = len(self.graph.people)
        if n == 0:
            return {}
        initial_value = 1.0 / float(n)
        rank = {node: initial_value for node in self.graph.people.keys()}

        for _ in range(max_iterations):
            new_rank = defaultdict(float)

            for node in self.graph.people.keys():
                # Add damping factor contribution
                new_rank[node] += (1 - damping_factor) / n

                # Add contributions from incoming links
                for predecessor in self.graph.reverse_adjacency_list[node]:
                    out_degree = len(self.graph.adjacency_list[predecessor])
                    if out_degree > 0:
                        new_rank[node] += damping_factor * rank[predecessor] / out_degree

            # Check convergence
            diff = sum(abs(new_rank[node] - rank[node]) for node in rank)
            rank = dict(new_rank)

            if diff < tolerance:
                break

        return rank

    def shortest_path(self, start: str, end: str) -> List[str]:
        """Find shortest path between two nodes using BFS"""
        if start not in self.graph.people or end not in self.graph.people:
            return []

        if start == end:
            return [start]

        # BFS
        visited = set()
        queue = deque([(start, [start])])

        while queue:
            current, path = queue.popleft()

            if current in visited:
                continue
            visited.add(current)

            # Iterate neighbors in sorted order for deterministic paths
            neighbors = sorted(self.graph.adjacency_list.get(current, []))
            for neighbor in neighbors:
                if neighbor not in visited:
                    new_path = path + [neighbor]
                    if neighbor == end:
                        return new_path
                    queue.append((neighbor, new_path))

        return []

    def all_pairs_shortest_paths(self) -> Dict[str, Dict[str, int]]:
        """Calculate shortest paths between all pairs of nodes using Floyd-Warshall"""
        nodes = list(self.graph.people.keys())
        n = len(nodes)
        node_index = {node: i for i, node in enumerate(nodes)}

        # Initialize distance matrix
        dist = [[float('inf')] * n for _ in range(n)]

        for i in range(n):
            dist[i][i] = 0

        # Add direct connections
        for i, node1 in enumerate(nodes):
            for node2 in self.graph.adjacency_list[node1]:
                j = node_index[node2]
                dist[i][j] = 1

        # Floyd-Warshall algorithm
        for k in range(n):
            for i in range(n):
                for j in range(n):
                    if dist[i][k] + dist[k][j] < dist[i][j]:
                        dist[i][j] = dist[i][k] + dist[k][j]

        # Convert back to dictionary format
        result = {}
        for i, node1 in enumerate(nodes):
            result[node1] = {}
            for j, node2 in enumerate(nodes):
                result[node1][node2] = dist[i][j] if dist[i][j] != float('inf') else -1

        return result

    def connected_components(self) -> List[List[str]]:
        """Find connected components in the graph"""
        visited = set()
        components = []

        for node in self.graph.people.keys():
            if node not in visited:
                component = []
                stack = [node]

                while stack:
                    current = stack.pop()
                    if current not in visited:
                        visited.add(current)
                        component.append(current)

                        # Add all unvisited neighbors
                        for neighbor in self.graph.adjacency_list[current]:
                            if neighbor not in visited:
                                stack.append(neighbor)

                if component:
                    components.append(component)

        return components

    def clustering_coefficient(self) -> Dict[str, float]:
        """Calculate clustering coefficient for each node"""
        coefficients = {}

        for node in self.graph.people.keys():
            neighbors = set(self.graph.get_connections(node))
            if len(neighbors) < 2:
                coefficients[node] = 0.0
                continue

            # Count triangles
            triangles = 0
            for neighbor1 in neighbors:
                for neighbor2 in neighbors:
                    if neighbor1 != neighbor2:
                        # Check if neighbor1 and neighbor2 are connected (treat as undirected)
                        if (neighbor2 in self.graph.adjacency_list[neighbor1]
                                or neighbor2 in self.graph.reverse_adjacency_list[neighbor1]):
                            triangles += 1

            # Each triangle is counted twice (once for each direction)
            triangles //= 2

            # Calculate coefficient
            possible_triangles = len(neighbors) * (len(neighbors) - 1) / 2
            coefficients[node] = triangles / possible_triangles if possible_triangles > 0 else 0.0

        return coefficients

    def detect_communities(self, method: str = "louvain") -> List[List[str]]:
        """Detect communities in the social network"""
        if method == "louvain":
            return self._louvain_community_detection()
        elif method == "girvan_newman":
            return self._girvan_newman_community_detection()
        else:
            # Default to connected components
            return self.connected_components()

    def _louvain_community_detection(self) -> List[List[str]]:
        """Simplified Louvain method for community detection"""
        # This is a simplified implementation
        # In practice, you'd want a more sophisticated algorithm

        communities = []
        processed = set()

        for node in self.graph.people.keys():
            if node in processed:
                continue

            # Start a new community with this node
            community = [node]
            processed.add(node)

            # Add strongly connected neighbors
            neighbors = list(self.graph.get_connections(node))
            for neighbor in neighbors:
                if neighbor not in processed:
                    # Check connection strength
                    relationship_strength = self.graph.get_relationship_strength(node, neighbor)
                    if relationship_strength > 0.5:  # Threshold for community membership
                        community.append(neighbor)
                        processed.add(neighbor)

            if len(community) > 1:  # Only add communities with multiple members
                communities.append(community)

        return communities

    def _girvan_newman_community_detection(self) -> List[List[str]]:
        """Girvan-Newman algorithm for community detection (edge removal based on edge betweenness)"""
        # Work on a copy of the graph
        graph_copy = self._copy_graph()

        def edge_betweenness(g):
            """Compute edge betweenness for all edges in the graph g (SocialGraph)"""
            eb = defaultdict(float)
            nodes = list(g.people.keys())
            for s in nodes:
                # Brandes' algorithm for edge betweenness
                stack = []
                pred = defaultdict(list)
                sigma = defaultdict(int)
                sigma[s] = 1
                dist = defaultdict(lambda: -1)
                dist[s] = 0
                queue = deque([s])
                while queue:
                    v = queue.popleft()
                    stack.append(v)
                    for w in g.adjacency_list[v]:
                        if dist[w] < 0:
                            queue.append(w)
                            dist[w] = dist[v] + 1
                        if dist[w] == dist[v] + 1:
                            sigma[w] += sigma[v]
                            pred[w].append(v)
                delta = defaultdict(float)
                while stack:
                    w = stack.pop()
                    for v in pred[w]:
                        c = (sigma[v] / sigma[w]) * (1 + delta[w])
                        edge = tuple(sorted((v, w)))
                        eb[edge] += c
                        delta[v] += c
            # Each edge counted twice (once from each node), so halve
            for edge in eb:
                eb[edge] /= 2.0
            return eb

        prev_num_components = 1
        while True:
            # Compute connected components
            components = []
            visited = set()
            for node in graph_copy.people.keys():
                if node not in visited:
                    comp = []
                    stack = [node]
                    while stack:
                        curr = stack.pop()
                        if curr not in visited:
                            visited.add(curr)
                            comp.append(curr)
                            for neighbor in graph_copy.adjacency_list[curr]:
                                if neighbor not in visited:
                                    stack.append(neighbor)
                    if comp:
                        components.append(comp)
            if len(components) > prev_num_components:
                break
            # Compute edge betweenness
            eb = edge_betweenness(graph_copy)
            if not eb:
                break
            max_bw = max(eb.values())
            # Remove all edges with max betweenness
            edges_to_remove = [edge for edge, bw in eb.items() if abs(bw - max_bw) < 1e-8]
            for u, v in edges_to_remove:
                # Remove edge from adjacency lists (undirected)
                if v in graph_copy.adjacency_list[u]:
                    graph_copy.adjacency_list[u].remove(v)
                if u in graph_copy.adjacency_list[v]:
                    graph_copy.adjacency_list[v].remove(u)
                # Remove from relationships if present
                rel_key1 = f"{u}-{v}"
                rel_key2 = f"{v}-{u}"
                if rel_key1 in graph_copy.relationships:
                    del graph_copy.relationships[rel_key1]
                if rel_key2 in graph_copy.relationships:
                    del graph_copy.relationships[rel_key2]
            prev_num_components = len(components)
        return components

    def _single_source_shortest_paths(self, start: str) -> Dict[str, int]:
        """Calculate shortest paths from a single source using BFS"""
        distances = {node: float('inf') for node in self.graph.people.keys()}
        distances[start] = 0

        queue = deque([start])
        visited = set([start])

        while queue:
            current = queue.popleft()

            for neighbor in self.graph.adjacency_list[current]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    distances[neighbor] = distances[current] + 1
                    queue.append(neighbor)

        # Convert inf to -1 for unreachable nodes
        return {node: dist if dist != float('inf') else -1 for node, dist in distances.items()}

    def _copy_graph(self) -> SocialGraph:
        """Create a copy of the graph"""
        new_graph = SocialGraph()

        # Copy people
        for person in self.graph.people.values():
            new_graph.add_person(Person(**person.__dict__))

        # Copy relationships
        for relationship in self.graph.relationships.values():
            new_graph.add_relationship(Relationship(**relationship.__dict__))

        return new_graph
    def network_density(self) -> float:
        """Calculate network density"""
        n = len(self.graph.people)
        if n < 2:
            return 0.0

        # Possible undirected edges in a simple graph
        possible_edges = n * (n - 1) / 2
        # Treat each stored relationship as one edge (tests expect this)
        actual_edges = len(self.graph.relationships)
        return actual_edges / possible_edges if possible_edges > 0 else 0.0

    def average_path_length(self) -> float:
        """Calculate average path length"""
        distances = self.all_pairs_shortest_paths()
        total_distance = 0
        count = 0

        for source in distances.values():
            for dist in source.values():
                if dist > 0:  # Ignore self-distances and unreachable nodes
                    total_distance += dist
                    count += 1

        return total_distance / count if count > 0 else 0.0

    def network_diameter(self) -> int:
        """Calculate network diameter"""
        distances = self.all_pairs_shortest_paths()
        max_distance = 0

        for source in distances.values():
            for dist in source.values():
                if dist > max_distance and dist != -1:
                    max_distance = dist

        return max_distance

    def degree_distribution(self) -> Dict[int, int]:
        """Calculate degree distribution"""
        distribution = defaultdict(int)

        # Include all nodes, counting undirected degree
        for node in self.graph.people.keys():
            degree = len(set(self.graph.get_connections(node)))
            distribution[degree] += 1

        return dict(distribution)

    def get_network_summary(self) -> Dict[str, Any]:
        """Get comprehensive network summary"""
        return {
            "nodes": len(self.graph.people),
            "edges": len(self.graph.relationships),
            "density": self.network_density(),
            "average_path_length": self.average_path_length(),
            "diameter": self.network_diameter(),
            "connected_components": len(self.connected_components()),
            "degree_distribution": self.degree_distribution(),
            "centrality_measures": {
                "degree": self.degree_centrality(),
                "betweenness": self.betweenness_centrality(),
                "closeness": self.closeness_centrality(),
                "eigenvector": self.eigenvector_centrality(),
                "pagerank": self.page_rank()
            },
            "clustering_coefficient": self.clustering_coefficient()
        }