import copy
import dataclasses
from typing import Dict, TextIO
from typing import List
from typing import Optional
from typing import Set


@dataclasses.dataclass
class Node:
    id_: int
    name: str
    tags: List[str]

    def __init__(self, id_: int, name: str, tags: Optional[List[str]] = None):
        self.id_ = id_
        self.name = name
        self.tags = tags or []

    @classmethod
    def from_dict(cls, raw_dict: dict) -> 'Node':
        return cls(
            id_=raw_dict['id'],
            name=raw_dict['name'],
        )

    def to_dict(self) -> dict:
        return {
            'id': self.id_,
            'name': self.name,
        }

    def get_tag_int_value(self, tag_key) -> int:
        val = self.get_tag_str_value(tag_key)
        return int(val)

    def get_tag_str_value(self, tag_key) -> str:
        for _tag in self.tags:
            if tag_key == _tag.split(':')[0]:
                return _tag.split(':')[1]
        assert False, f'unable to find key {tag_key} in node {self}'

    def has_tag(self, tag) -> bool:
        for _tag in self.tags:
            if _tag == tag:
                return True
        return False


@dataclasses.dataclass
class Graph:
    all_nodes: List[Node]
    id_to_node: Dict[int, Node]
    nodes_from: Dict[int, Set[int]]
    nodes_to: Dict[int, Set[int]]

    def __init__(self, nodes: List[Node], nodes_from: Dict[int, Set[int]], nodes_to: Dict[int, Set[int]]) -> 'Graph':
        self.id_to_node: Dict[int, Node] = {}
        self.all_nodes = copy.deepcopy(nodes)
        self.nodes_from = copy.deepcopy(nodes_from)
        self.nodes_to = copy.deepcopy(nodes_to)

        for node in self.all_nodes:
            self.id_to_node[node.id_] = node

    def insert_node(self, node: Node, nodes_from: Set[int], nodes_to: Set[int]) -> None:
        self.all_nodes.append(node)
        self.id_to_node[node.id_] = node
        self.nodes_from[node.id_] = nodes_from
        self.nodes_to[node.id_] = nodes_to

    def get_node_by_id(self, node_id: int) -> Node:
        if node_id not in self.id_to_node:
            raise ValueError(f'Node with id {node_id} not found')
        return self.id_to_node[node_id]

    def print_mermaid(self, file_name: str) -> None:
        with open(file_name, 'w') as f:
            self._print_mermaid(f)

    def _print_mermaid(self, file: TextIO) -> None:
        file.write('graph LR\n')

        file.write('%% Терминал\n')
        for node in self.all_nodes:
            if not node.name.startswith('node_'): continue
            file.write(f'\t{node.id_}[Терминал {node.name}]:::terminal\n')

        file.write('\n%% Коммутаторы\n')
        for node in self.all_nodes:
            if not node.name.startswith('switch_'): continue
            file.write(f'\t{node.id_}[Коммутатор {node.name}]:::switch\n')

        file.write('\n%% Узлы-ребра\n')
        for node in self.all_nodes:
            if not node.name.startswith('edge_'): continue
            file.write(f'\t{node.id_}["{node.name}"]:::edgenode\n')

        file.write('\n%% Ребры графа\n')
        for from_node_id, to_node_ids in self.nodes_from.items():
            for to_node_id in to_node_ids:
                file.write(f'\t{from_node_id} ---> {to_node_id}\n')
                # sw1 ---> sw2

        file.write("""
        \nclassDef terminal fill:#F45B69,stroke:#333,stroke-width:2px
        classDef switch fill:#688EB6,stroke:#333,stroke-width:2px
        classDef edgenode fill:#E4FDE1,stroke:#333,stroke-width:2px\n""")


@dataclasses.dataclass
class NonDirectionalGraph:
    all_nodes: List[Node]
    id_to_node: Dict[int, Node]
    nodes_from: Dict[int, Set[int]]

    def __init__(self, nodes: List[Node], nodes_from: Dict[int, Set[int]]) -> 'NonDirectionalGraph':
        self.id_to_node: Dict[int, Node] = {}
        self.all_nodes = copy.deepcopy(nodes)
        self.nodes_from = copy.deepcopy(nodes_from)

        for node in self.all_nodes:
            self.id_to_node[node.id_] = node

    def get_node_by_id(self, node_id: int) -> Node:
        if node_id not in self.id_to_node:
            raise ValueError(f'Node with id {node_id} not found')
        return self.id_to_node[node_id]

    def print_mermaid(self, file_name: str) -> None:
        with open(file_name, 'w') as f:
            self._print_mermaid(f)

    def _print_mermaid(self, file: TextIO) -> None:
        file.write('graph LR\n')

        file.write('%% Терминал\n')
        for node in self.all_nodes:
            if not node.name.startswith('node_'): continue
            file.write(f'\t{node.id_}[Терминал {node.name}]:::terminal\n')

        file.write('\n%% Коммутаторы\n')
        for node in self.all_nodes:
            if not node.name.startswith('switch_'): continue
            file.write(f'\t{node.id_}[Коммутатор {node.name}]:::switch\n')

        file.write('\n%% Узлы-ребра\n')
        for node in self.all_nodes:
            if not node.name.startswith('edge_'): continue
            file.write(f'\t{node.id_}["{node.name}"]:::edgenode\n')

        file.write('\n%% Ребры графа\n')
        for from_node_id, to_node_ids in self.nodes_from.items():
            for to_node_id in to_node_ids:
                if to_node_id >= from_node_id:
                    file.write(f'\t{from_node_id} <---> {to_node_id}\n')
                    # sw1 --- sw2

        file.write("""
        \nclassDef terminal fill:#F45B69,stroke:#333,stroke-width:2px
        classDef switch fill:#688EB6,stroke:#333,stroke-width:2px
        classDef edgenode fill:#E4FDE1,stroke:#333,stroke-width:2px\n""")


@dataclasses.dataclass
class NdTorus(Graph):
    base_dimensions: List[str]
    modules: int

    def get_real_nodes(self):
        return [node for node in self.all_nodes if 'edge' not in node.tags]

    def get_switches(self):
        return [node for node in self.all_nodes if 'switch' in node.tags]

    def get_terminals(self):
        return [node for node in self.all_nodes if 'terminal' in node.tags]

    def get_edges(self):
        return [node for node in self.all_nodes if 'edge' in node.tags]

    def __init__(
            self,
            graph: Graph,
            dimensions: List[str],
            modules: int,
    ):
        super().__init__(
            nodes=graph.all_nodes,
            nodes_from=graph.nodes_from,
            nodes_to=graph.nodes_to,
        )
        self.base_dimensions = dimensions
        self.modules = modules
        self._assert_good_torus_init()

    def _assert_good_torus_init(self) -> None:
        assert len(self.base_dimensions) > 0
        self._assert_good_dims()
        self._assert_edges_has_tags()
        self._assert_switches_edges_has_same_module()

    def _assert_good_dims(self) -> None:
        node_dims: Set[str] = set()
        for node in self.all_nodes:
            if not node.name.startswith('edge_'): continue
            for tag in node.tags:
                if tag.startswith('from_dir:') or tag.startswith('to_dir:'):
                    direction = tag.split(':')[1]
                    assert len(direction) == 2, f'dimension should have direction: {node}'
                    node_dims.add(direction[1])

        torus_dims = set(self.base_dimensions)
        assert node_dims.issubset(torus_dims), f'dimensions should be in {torus_dims}: {node_dims}'

    def _assert_edges_has_tags(self) -> None:
        tag_pairs = [['from_port', 'to_port'], ['from_dir', 'to_dir'], ['from_node', 'to_node']]
        for node in self.all_nodes:
            if not node.name.startswith('edge_'): continue

            for tag_pair in tag_pairs:
                self._assert_edge_node_has_both_tags(node, tag_pair[0], tag_pair[1])

            self._assert_switch_edge_has_same_module(node)

    def _assert_switches_edges_has_same_module(self) -> None:
        for node in self.all_nodes:
            if not node.name.startswith('edge_'): continue
            self._assert_switch_edge_has_same_module(node)

    @classmethod
    def _assert_edge_node_has_both_tags(self, node: Node, tag_one: str, tag_two: str) -> None:
        has_tag_one = False
        has_tag_two = False
        for tag in node.tags:
            if tag.startswith(tag_one):
                has_tag_one = True
                split_tag = tag.split(':')
                assert len(split_tag) == 2
            if tag.startswith(tag_two):
                has_tag_two = True
                split_tag = tag.split(':')
                assert len(split_tag) == 2

        has_both_tags = has_tag_one and has_tag_two
        assert has_both_tags, f'should has both tags=[{tag_one}, {tag_two}]: {node}'

    @classmethod
    def _assert_switch_edge_has_same_module(self, node: Node) -> None:
        from_node = ''
        to_node = ''
        from_port = -1
        to_port = -1
        for tag in node.tags:
            if tag.startswith('from_node:'):
                from_node = tag.split(':')[1]
            if tag.startswith('to_node:'):
                to_node = tag.split(':')[1]
            if tag.startswith('from_port:'):
                from_port = int(tag.split(':')[1])
            if tag.startswith('to_port:'):
                to_port = int(tag.split(':')[1])

        if not from_node.startswith('switch_:') or not to_node.startswith('switch_:'):
            return

        assert self.ports_has_same_module(from_port, to_port), f'ports should be in the same module: {node}'

    def ports_has_same_module(self, from_port: int, to_port: int) -> bool:
        dist = abs(from_port - to_port + 1)
        return dist <= 2 * len(self.base_dimensions)
