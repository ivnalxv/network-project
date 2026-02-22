from collections import defaultdict
import dataclasses

import itertools

from typing import Dict, Tuple
from typing import List
from typing import Set

from graph.entities import Node, Graph, NonDirectionalGraph


@dataclasses.dataclass
class Torus:
    topology_graph: NonDirectionalGraph
    base_dimensions: List[str]
    modules: int
    edge_id_to_connected: Dict[int, Tuple[int, int]]

    def __init__(
            self,
            parsed_graph: Graph,
            dimensions: List[str],
            modules: int,
    ):
        self.base_dimensions = dimensions
        self.modules = modules

        builder = TorusGraphBuilder(dimensions, modules, parsed_graph)
        self.topology_graph = builder.build()
        self.edge_id_to_connected = builder.edge_id_to_connected

    def get_by_node_id(self, node_id: int) -> Node:
        return self.topology_graph.get_node_by_id(node_id)

    def next_node(self, from_node_id: int, by_module: int, by_direction: str) -> Node:
        forward_node_ids = self.topology_graph.nodes_from[from_node_id]

        for forward_node_id in forward_node_ids:
            forward_node = self.get_by_node_id(forward_node_id)
            module = forward_node.get_tag_int_value('module')
            direction = forward_node.get_tag_str_value('direction')

            if module != by_module or by_direction != direction:
                continue

            edge_id = forward_node.get_tag_int_value('edge_id')
            edge_nodes = self.get_edge_nodes(edge_id)
            if edge_nodes[0] == from_node_id:
                return self.get_by_node_id(edge_nodes[1])
            return self.get_by_node_id(edge_nodes[0])

        assert False, 'No next node found'

    def get_edge_nodes(self, edge_id: int) -> (int, int):
        return self.edge_id_to_connected[edge_id]


class TorusGraphBuilder:
    def __init__(
            self,
            dimensions: List[str],
            modules: int,
            parsed_graph: Graph,
    ):
        self.base_dimensions = dimensions
        self.modules = modules
        self.parsed_graph = parsed_graph
        self.edge_id_to_connected: Dict[int, (int, int)] = {}

        self._id_to_node: Dict[int, Node] = {}
        self._name_to_node_id: Dict[str, int] = {}

        self._nodes_from: Dict[int, Set[int]] = defaultdict(set)
        self._node_id_iterator = itertools.count(1)
        self._edge_id_iterator = itertools.count(1)

        self._edge_visited: Set[str] = set()

    def build(self) -> NonDirectionalGraph:
        self._build_terminal_nodes()
        self._build_switch_nodes()
        self._build_edges_nodes()
        return NonDirectionalGraph(
            nodes=list(self._id_to_node.values()),
            nodes_from=self._nodes_from,
        )

    def _build_terminal_nodes(self) -> None:
        pg_terminals = [node for node in self.parsed_graph.all_nodes if 'terminal' in node.tags]
        for pg_terminal in pg_terminals:
            node_id = next(self._node_id_iterator)
            name = pg_terminal.name

            new_node = Node(
                id_=node_id, name=name, tags=[f'old_node_id:{pg_terminal.id_}', 'terminal'],
            )
            self._id_to_node[node_id] = new_node
            self._name_to_node_id[pg_terminal.name] = node_id

    def _build_switch_nodes(self) -> None:
        pg_switches = [node for node in self.parsed_graph.all_nodes if 'switch' in node.tags]
        for pg_switch in pg_switches:
            node_id = next(self._node_id_iterator)
            name = pg_switch.name

            new_node = Node(
                id_=node_id, name=name, tags=[f'old_node_id:{pg_switch.id_}', 'switch'],
            )
            self._id_to_node[node_id] = new_node
            self._name_to_node_id[name] = node_id

    def _get_visited_edge_name(self, pg_edge: Node) -> str:
        from_node_name = pg_edge.get_tag_str_value('from_node')
        from_port = pg_edge.get_tag_int_value('from_port')
        from_dir = pg_edge.get_tag_str_value('from_dir')

        to_node_name = pg_edge.get_tag_str_value('to_node')
        to_port = pg_edge.get_tag_int_value('to_port')
        to_dir = pg_edge.get_tag_str_value('to_dir')

        from_meta = f'{from_node_name}_{from_port}_{from_dir}'
        to_meta = f'{to_node_name}_{to_port}_{to_dir}'

        edge_name = f'[{from_meta}]_[{to_meta}]'
        if to_meta < from_meta:
            edge_name = f'[{to_meta}]_[{from_meta}]'
        return edge_name

    def _mark_edge_visited(self, pg_edge: Node) -> None:
        edge_name = self._get_visited_edge_name(pg_edge)
        self._edge_visited.add(edge_name)

    def _is_edge_visited(self, pg_edge: Node) -> bool:
        edge_name = self._get_visited_edge_name(pg_edge)
        # print(f'[TORUS BUILDER] Checking for edge: {edge_name}')
        return edge_name in self._edge_visited

    def _connect_nodes(self, node_id_a: int, node_id_b: int) -> None:
        assert node_id_a in self._id_to_node, f'Node {node_id_a} not found'
        assert node_id_b in self._id_to_node, f'Node {node_id_b} not found'
        self._nodes_from[node_id_a].add(node_id_b)
        self._nodes_from[node_id_b].add(node_id_a)

    def _build_edges_nodes(self) -> None:
        pg_edges = [node for node in self.parsed_graph.all_nodes if 'edge' in node.tags]
        for pg_edge in pg_edges:
            if self._is_edge_visited(pg_edge):
                print(f'[TORUS BUILDER] Edge already visited: {pg_edge.name}')
                continue
            self._mark_edge_visited(pg_edge)

            from_node_name = pg_edge.get_tag_str_value('from_node')
            from_dir = pg_edge.get_tag_str_value('from_dir')
            from_module = pg_edge.get_tag_int_value('from_module')

            to_node_name = pg_edge.get_tag_str_value('to_node')
            to_dir = pg_edge.get_tag_str_value('to_dir')
            to_module = pg_edge.get_tag_int_value('to_module')

            from_node_id = self._name_to_node_id[from_node_name]
            to_node_id = self._name_to_node_id[to_node_name]

            edge_id = next(self._edge_id_iterator)
            self.edge_id_to_connected[edge_id] = (from_node_id, to_node_id)

            to_edge_node_id = next(self._node_id_iterator)
            to_edge_node = Node(
                id_=to_edge_node_id,
                name=f'edge_{to_dir}_{to_module}',
                tags=[
                    'edge',
                    f'direction:{to_dir}',
                    f'module:{to_module}',
                    f'edge_id:{edge_id}'
                ],
            )
            self._id_to_node[to_edge_node_id] = to_edge_node

            back_edge_node_id = next(self._node_id_iterator)
            back_edge_node = Node(
                id_=back_edge_node_id,
                name=f'edge_{from_dir}_{from_module}',
                tags=[
                    'edge',
                    f'direction:{from_dir}',
                    f'module:{from_module}',
                    f'edge_id:{edge_id}'
                ],
            )
            self._id_to_node[back_edge_node_id] = back_edge_node

            self._connect_nodes(from_node_id, to_edge_node_id)
            self._connect_nodes(to_edge_node_id, back_edge_node_id)
            self._connect_nodes(back_edge_node_id, to_node_id)


class TorusChecker:
    torus: Torus

    def __init__(self, torus: Torus):
        self.torus = torus

    def validate(self) -> None:
        pass
