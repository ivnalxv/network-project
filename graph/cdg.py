from collections import defaultdict

import itertools
import json

from typing import Dict
from typing import List
from typing import Set

from graph.entities import Node, Graph, NdTorus


class CdgBuilder:
    dimensions_order: List[str]
    torus: NdTorus

    _builder_node_id_to_node: Dict[int, Node]
    _builder_nodes_from: Dict[int, Set[int]]
    _builder_nodes_to: Dict[int, Set[int]]

    def __init__(self, torus: NdTorus, dim_order: List[str]):
        self.dimensions_order = dim_order
        self.torus = torus

        # BASE : ['+K', '-K', '+Z', '-Z', '+Y', '-Y', '+X', '-X'], num=8
        # ORDER: ['+K', '+Z', '+Y', '-K', '-Z', '-Y', '+X', '-X'], num=8

        self._assert_good_order()

        self._builder_node_id_to_node = {}
        self._builder_nodes_from = defaultdict(set)
        self._builder_nodes_to = defaultdict(set)

    def _assert_good_order(self):
        assert len(self.torus.base_dimensions) * 2 == len(
            self.dimensions_order), f'base: {self.torus.base_dimensions}, but order: {self.dimensions_order}'
        dims = set(self.torus.base_dimensions)
        for order_dim in self.dimensions_order:
            assert len(order_dim) == 2
            assert order_dim[0] in {'-', '+'}, f'wrong order turn: {order_dim}'
            assert order_dim[1] in dims, f'wrong order turn: {order_dim}'

    def _add_edge(self, from_node_id: int, to_node_id: int):
        self._builder_nodes_from[from_node_id].add(to_node_id)
        self._builder_nodes_to[to_node_id].add(from_node_id)

    def check_turn(self, from_dim: str, to_dim: str) -> bool:
        from_ind = self.dimensions_order.index(from_dim)
        to_ind = self.dimensions_order.index(to_dim)
        return from_ind <= to_ind

    def build_cdg_graph(self) -> Graph:
        edge_nodes = self.torus.get_edges()
        print('\nALL EDGES:')
        print(edge_nodes)

        for edge_node in edge_nodes:
            self._builder_node_id_to_node[edge_node.id_] = edge_node

        for edge_node_a in edge_nodes:
            edge_from_terminal = edge_node_a.has_tag('terminal')

            connected_nodes = self.torus.nodes_from[edge_node_a.id_]
            for connected_node_id in connected_nodes:
                edge_node_b_ids = self.torus.nodes_from[connected_node_id]
                for edge_node_b_id in edge_node_b_ids:
                    edge_node_b = self.torus.get_node_by_id(edge_node_b_id)
                    edge_to_terminal = edge_node_b.has_tag('terminal')

                    if edge_from_terminal:
                        print(f'[CDG]-EDGE: Possible turn, edge FROM terminal: {edge_node_a}, {edge_node_b}')
                        self._add_edge(edge_node_a.id_, edge_node_b.id_)
                        continue

                    if edge_to_terminal:
                        print(f'[CDG]-EDGE: Possible turn, edge TO terminal: {edge_node_a}, {edge_node_b}')
                        self._add_edge(edge_node_a.id_, edge_node_b.id_)
                        continue

                    if edge_node_a.id_ == edge_node_b.id_:
                        print(f'[CDG]-SKIP: Same node-edges: {edge_node_a}, {edge_node_b}')
                        continue

                    # module_a = edge_node_a.get_tag_int_value('')
                    dir_a = edge_node_a.get_tag_str_value('to_dir')
                    dir_b = edge_node_b.get_tag_str_value('to_dir')

                    if self.check_turn(dir_a, dir_b):
                        print(f'[CDG]-EDGE: Possible turn: {edge_node_a}, {edge_node_b}')
                        self._add_edge(edge_node_a.id_, edge_node_b.id_)
                        continue

                    print(f'[CDG]-SKIP: No route for node-edges: {edge_node_a}, {edge_node_b}')

        all_nodes: List[Node] = []
        for node_id, node in self._builder_node_id_to_node.items():
            all_nodes.append(node)

        return Graph(
            nodes=all_nodes,
            nodes_from=self._builder_nodes_from,
            nodes_to=self._builder_nodes_to,
        )


class CycleChecker:
    visited_node_ids: Set[int]
    in_recursion: Set[int]
    graph: Graph
    cycle_path: List[int]
    # TODO:: добавить вывод цикла

    def __init__(self, graph: Graph):
        self.graph = graph
        self.visited_node_ids = set()
        self.in_recursion = set()
        self.cycle_path = []

    def has_cycle(self) -> bool:
        all_nodes = self.graph.all_nodes

        for node in all_nodes:
            node_id = node.id_
            if (not self._is_visited(node_id)) and self._dfs(node_id):
                return True
        return False

    def find_cycle(self) -> List[int]:
        all_nodes = self.graph.all_nodes

        for node in all_nodes:
            node_id = node.id_
            self.cycle_path = []
            if (not self._is_visited(node_id)) and self._dfs(node_id):
                return self.cycle_path
        return []

    def print_detailed_cycle(self):
        cycle = self.find_cycle()

        print('\nCycle:')
        for node_id in cycle:
            print(self.graph.get_node_by_id(node_id))


    def _dfs(self, node_id: int) -> bool:
        self.cycle_path.append(node_id)

        if self._is_in_recursion(node_id):
            return True

        if self._is_visited(node_id):
            self.cycle_path.pop()
            return False

        self.in_recursion.add(node_id)
        self.visited_node_ids.add(node_id)

        adj_node_ids = self.graph.nodes_from[node_id]
        for adj_node_id in adj_node_ids:
            if self._dfs(adj_node_id):
                return True

        self.in_recursion.remove(node_id)
        self.cycle_path.pop()
        return False

    def _is_visited(self, node_id: int) -> bool:
        return node_id in self.visited_node_ids

    def _is_in_recursion(self, node_id: int) -> bool:
        return node_id in self.in_recursion
