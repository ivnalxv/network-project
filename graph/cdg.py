from collections import defaultdict

import itertools
import json

from typing import Dict, TextIO
from typing import List
from typing import Set

from graph.entities import Node, NonDirectionalGraph
from graph.torus import Torus


class CdgBuilder:
    dimensions_order: List[str]
    torus: Torus

    _builder_node_id_to_node: Dict[int, Node]
    _builder_nodes_from: Dict[int, Set[int]]
    _builder_nodes_to: Dict[int, Set[int]]

    def __init__(self, torus: Torus, dim_order: List[str]):
        self.dimensions_order = dim_order
        self.torus = torus

        # BASE : ['+K', '-K', '+Z', '-Z', '+Y', '-Y', '+X', '-X'], num=8
        # ORDER: ['+K', '+Z', '+Y', '-K', '-Z', '-Y', '+X', '-X'], num=8

        self._assert_good_order()

        self._builder_node_id_to_node = {}
        self._builder_nodes_from = defaultdict(set)

    def _assert_good_order(self):
        assert len(self.torus.base_dimensions) * 2 == len(
            self.dimensions_order), f'base: {self.torus.base_dimensions}, but order: {self.dimensions_order}'
        dims = set(self.torus.base_dimensions)
        for order_dim in self.dimensions_order:
            assert len(order_dim) == 2
            assert order_dim[0] in {'-', '+'}, f'wrong order turn: {order_dim}'
            assert order_dim[1] in dims, f'wrong order turn: {order_dim}'

    def _add_edge(self, node_id_a: int, node_id_b: int):
        self._builder_nodes_from[node_id_a].add(node_id_b)
        self._builder_nodes_from[node_id_b].add(node_id_a)

    def check_turn(self, from_dim: str, to_dim: str) -> bool:
        from_ind = self.dimensions_order.index(from_dim)
        to_ind = self.dimensions_order.index(to_dim)
        return from_ind <= to_ind

    def check_turn_and_add_edge(
            self,
            from_node_id: int,
            to_node_id: int,
            from_dim: str,
            to_dim: str,
    ) -> bool:
        if self.check_turn(from_dim, to_dim):
            from_node = self._builder_node_id_to_node[from_node_id]
            to_node = self._builder_node_id_to_node[to_node_id]
            print(f'[CDG]-EDGE: Possible turn: {from_dim} to {to_dim}, nodes: {from_node}, {to_node}')
            self._add_edge(from_node_id, to_node_id)
        return False

    def build_cdg_graph(self) -> NonDirectionalGraph:
        edge_ids = sorted(self.torus.get_all_edge_ids())

        for edge_id in edge_ids:
            one, two = self.torus.get_pair_node_ids_by_edge(edge_id)
            one_to_two_direction = self.torus.get_direction_by_edge_from_node(
                from_node_id=one,
                by_edge_id=edge_id,
            )
            two_to_one_direction = self.torus.get_direction_by_edge_from_node(
                from_node_id=two,
                by_edge_id=edge_id,
            )
            edge_node = Node(
                id_=edge_id,
                name=f'edge_{edge_id}',
                tags=[
                    f'connect_one:{one}',
                    f'connect_two:{two}',
                    f'direction_one_to_two:{one_to_two_direction}',
                    f'direction_two_to_one:{two_to_one_direction}'
                ],
            )
            self._builder_node_id_to_node[edge_id] = edge_node

        # (Node 1) <-> (Edge A) <-> (Node 2) <-> (Edge B) <-> (Node 3)
        for edge_id_a in edge_ids:
            adjacent_edge_ids = self.torus.get_adjacent_edges_by_edge_id(edge_id_a)
            for edge_id_b in adjacent_edge_ids:
                if edge_id_a == edge_id_b:
                    print(f'[CDG]-SKIP: Same edges: {edge_id_a}, {edge_id_a}')
                    continue

                connecting_node_ids = self.torus.get_connecting_node_id_by_edges(edge_id_a, edge_id_b)
                if len(connecting_node_ids) == 2:
                    #              -> dir_1                  -> dir_2
                    # (Node 1) <-> (Edge A) <-> (Node 2) <-> (Edge B) <-> (Node 1)
                    #              <- dir_4                  <- dir_3
                    node_id_one = connecting_node_ids[0]
                    node_id_two = connecting_node_ids[1]

                    dir_1 = self.torus.get_direction_by_edge_from_node(node_id_one, edge_id_a)
                    dir_2 = self.torus.get_direction_by_edge_from_node(node_id_two, edge_id_b)
                    self.check_turn_and_add_edge(edge_id_a, edge_id_b, dir_1, dir_2)

                    dir_3 = self.torus.get_direction_by_edge_from_node(node_id_one, edge_id_b)
                    dir_4 = self.torus.get_direction_by_edge_from_node(node_id_two, edge_id_a)
                    self.check_turn_and_add_edge(edge_id_b, edge_id_a, dir_3, dir_4)
                elif len(connecting_node_ids) == 1:
                    #              -> dir_1                  -> dir_2
                    # (Node 1) <-> (Edge A) <-> (Node 2) <-> (Edge B) <-> (Node 3)
                    node_id_two = connecting_node_ids[0]
                    node_id_one, two = self.torus.get_pair_node_ids_by_edge(edge_id_a)
                    if node_id_one == node_id_two:
                        node_id_one = two

                    dir_1 = self.torus.get_direction_by_edge_from_node(node_id_one, edge_id_a)
                    dir_2 = self.torus.get_direction_by_edge_from_node(node_id_two, edge_id_b)
                    self.check_turn_and_add_edge(edge_id_a, edge_id_b, dir_1, dir_2)
                else:
                    assert False, f'Bad connected edges: {connecting_node_ids}'

        all_nodes: List[Node] = []
        for node_id, node in self._builder_node_id_to_node.items():
            all_nodes.append(node)

        return NonDirectionalGraph(
            nodes=all_nodes,
            nodes_from=self._builder_nodes_from,
        )


class CycleChecker:
    visited_node_ids: Set[int]
    in_recursion: Set[int]
    cycle_path: List[int]
    graph: NonDirectionalGraph
    torus: Torus

    def __init__(self, graph: NonDirectionalGraph, torus: Torus):
        self.graph = graph
        self.torus = torus
        self.visited_node_ids = set()
        self.in_recursion = set()
        self.cycle_path = []

    def has_cycle(self) -> bool:
        cycle = self.find_cycle()
        return len(cycle) > 0

    def find_cycle(self) -> List[int]:
        self._clear_checker_data()
        all_nodes = self.graph.all_nodes

        for node in all_nodes:
            node_id = node.id_
            self.cycle_path = []
            if (not self._is_visited(node_id)) and self._dfs(node_id):
                cycle = self._extract_true_cycle_path()
                return cycle
        return []

    def print_detailed_cycle(self, file_name: str):
        self._clear_checker_data()
        cycle = self.find_cycle()

        if len(cycle) == 0:
            print('\nHas cycle: False')
            return

        print('\nHas cycle: True\nCycle:')
        for node_id in cycle:
            print(self.graph.get_node_by_id(node_id))

        self._print_mermaid(cycle, file_name)

    def _clear_checker_data(self):
        self.visited_node_ids = set()
        self.in_recursion = set()
        self.cycle_path = []

    def _dfs(self, node_id: int) -> bool:
        self.cycle_path.append(node_id)

        if self._is_in_recursion(node_id):
            is_bubble = self._check_found_cycle_for_bubble()
            if is_bubble:
                self.cycle_path.pop()
                return False
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

    def _extract_true_cycle_path(self) -> List[int]:
        assert len(self.cycle_path) > 0, 'Cycle path is empty'

        last_node_id = self.cycle_path[-1]
        found_cycle_right_index = len(self.cycle_path) - 1
        found_cycle_left_index = -1
        for index in range(len(self.cycle_path) - 2, -1, -1):
            current_node_id = self.cycle_path[index]
            if last_node_id == current_node_id:
                found_cycle_left_index = index

        assert found_cycle_left_index != -1, f'Cycle has no true cycle: {self.cycle_path}'
        return self.cycle_path[found_cycle_left_index:found_cycle_right_index + 1]

    def _check_found_cycle_for_bubble(self) -> bool:
        cycle = self._extract_true_cycle_path()

        last_cycle_node = self.graph.get_node_by_id(cycle[-1])
        cycle_dim = last_cycle_node.get_tag_str_value('direction_one_to_two')[1]
        for index in range(len(cycle) - 1, -1, -1):
            cycle_node = self.graph.get_node_by_id(cycle[index])
            node_dim = cycle_node.get_tag_str_value('direction_one_to_two')[1]
            node_dim_two = cycle_node.get_tag_str_value('direction_two_to_one')[1]
            if node_dim != cycle_dim and node_dim_two != cycle_dim:
                return False
        return True

    def _print_mermaid(self, cycle: List[int], file_name: str):
        with open(file_name, 'w') as f:
            self._print_mermaid_io(cycle, f)

    def _print_mermaid_io(self, cycle: List[int], file: TextIO) -> None:
        file.write('graph LR\n')

        file.write('%% Ноды\n')
        for node in self.graph.all_nodes:
            if node.id_ in cycle:
                file.write(f'\t{node.id_}[Нода {node.name}]:::cycleNode\n')
            else:
                file.write(f'\t{node.id_}[Нода {node.name}]:::node\n')

        file.write('\n%% Ребра графа\n')
        for from_node_id, to_node_ids in self.graph.nodes_from.items():
            for to_node_id in to_node_ids:
                if to_node_id >= from_node_id:
                    file.write(f'\t{from_node_id} <---> {to_node_id}\n')

        file.write("""
                \nclassDef node fill:#F45B69,stroke:#333,stroke-width:2px
                \nclassDef cycleNode fill:#688EB6,stroke:#333,stroke-width:2px
                \n""")
