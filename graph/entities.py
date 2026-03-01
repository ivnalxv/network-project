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

    def print_torus_mermaid(self, file_name: str) -> None:
        with open(file_name, 'w') as f:
            self._print_torus_mermaid(f)

    def _print_torus_mermaid(self, file: TextIO) -> None:
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
            edge_id = node.get_tag_int_value('edge_id')
            file.write(f'\t{node.id_}["{node.name}({edge_id})"]:::edgenode\n')

        file.write('\n%% Ребра графа\n')
        for from_node_id, to_node_ids in self.nodes_from.items():
            for to_node_id in to_node_ids:
                if to_node_id >= from_node_id:
                    file.write(f'\t{from_node_id} <---> {to_node_id}\n')
                    # sw1 --- sw2

        file.write("""
        \nclassDef terminal fill:#F45B69,stroke:#333,stroke-width:2px
        classDef switch fill:#688EB6,stroke:#333,stroke-width:2px
        classDef edgenode fill:#E4FDE1,stroke:#333,stroke-width:2px\n""")

    def print_simple_mermaid(self, file_name: str) -> None:
        with open(file_name, 'w') as f:
            self._print_simple_mermaid(f)

    def _print_simple_mermaid(self, file: TextIO) -> None:
        file.write('graph LR\n')

        file.write('%% Ноды\n')
        for node in self.all_nodes:
            file.write(f'\t{node.id_}[Нода {node.name}]:::node\n')

        file.write('\n%% Ребра графа\n')
        for from_node_id, to_node_ids in self.nodes_from.items():
            for to_node_id in to_node_ids:
                if to_node_id >= from_node_id:
                    file.write(f'\t{from_node_id} <---> {to_node_id}\n')
                    # sw1 --- sw2

        file.write("""
        \nclassDef node fill:#F45B69,stroke:#333,stroke-width:2px""")
