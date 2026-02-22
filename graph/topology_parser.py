from collections import defaultdict

import itertools
import json

from typing import Dict
from typing import List
from typing import Set

from graph.entities import Node, Graph


class TopologyParser:
    def __init__(self, dirs: List[str], module_nums: int):
        self._node_id_iterator = itertools.count(1)
        self._name_to_node_id: Dict[str, int] = {}
        self._names: Set[str] = set()
        self._node_id_to_tags: Dict[int, List[str]] = defaultdict(list)

        self._nodes_from: Dict[int, Set[int]] = defaultdict(set)
        self._nodes_to: Dict[int, Set[int]] = defaultdict(set)

        # ['+K', '-K', '+Z', '-Z', '+Y', '-Y', '+X', '-X'], num=8
        self._dir_names = dirs
        self._dir_nums = len(dirs)
        # module 1: 1, 2, 3, ..., 8
        # module 2: 9, 10, 11, ..., 16
        #
        self._module_nums = module_nums
        self._assert_good_init()

    def _assert_good_init(self) -> None:
        assert self._dir_nums == len(set(self._dir_names))
        assert self._dir_nums % 2 == 0
        assert self._module_nums > 0

    def get_direction_name(self, port: int) -> str:
        val = (port - 1) % self._dir_nums
        return self._dir_names[val]

    def get_module(self, port: int) -> int:
        val = (port - 1) // self._dir_nums
        return val + 1

    def add_node_name(self, name: str) -> int:
        if name in self._names:
            raise ValueError(f'Node name "{name}" already exists')
        self._names.add(name)
        self._name_to_node_id[name] = next(self._node_id_iterator)
        return self._name_to_node_id[name]

    def connect_nodes(self, from_node: str, to_node: str) -> None:
        from_node_id = self._name_to_node_id[from_node]
        to_node_id = self._name_to_node_id[to_node]
        #      ---> 3
        # 1 -> 2 -> 4
        #      ---> 5
        # from(2) = {3, 4, 5}
        # to(2) = {1}

        self._nodes_from[from_node_id].add(to_node_id)
        self._nodes_to[to_node_id].add(from_node_id)

    @classmethod
    def gen_device_name(self, device_id: str) -> str:
        if device_id.startswith('sw'):
            device_name = f'switch_{device_id}'
        else:
            device_name = f'node_{device_id}'
        return device_name

    def create_device_nodes(self, json_dict: Dict) -> None:
        for device_id, device_data in json_dict.items():
            device_name = self.gen_device_name(device_id)
            node_id = self.add_node_name(device_name)

            if device_id.startswith('sw'):
                self._node_id_to_tags[node_id] = ['switch']
            else:
                self._node_id_to_tags[node_id] = ['terminal']

    def create_switches_graph(self, json_dict: Dict) -> None:
        for device_id, device_data in json_dict.items():
            device_name = self.gen_device_name(device_id)
            if not device_name.startswith('switch_'): continue

            switches_data = device_data['switches']
            nodes_data = device_data['nodes']
            if not isinstance(switches_data, list) or not isinstance(nodes_data, list): continue

            for connection in switches_data:
                self.create_switch_edge(device_name, connection)

            for connection in nodes_data:
                self.create_node_edge(device_name, connection)

    def create_nodes_graph(self, json_dict: Dict) -> None:
        for device_id, nodes_data in json_dict.items():
            device_name = self.gen_device_name(device_id)
            if device_name.startswith('switch_'): continue
            if not isinstance(nodes_data, list): continue

            for connection in nodes_data:
                self.create_switch_edge(device_name, connection)

    def create_switch_edge(self, device_name: str, connection: Dict) -> None:
        port_a = connection['portA']
        switch_b = connection['switchB']
        port_b = connection['portB']

        switch_b_device_name = self.gen_device_name(switch_b)

        self._create_edge(
            from_node_name=device_name,
            to_node_name=switch_b_device_name,
            from_port=port_a,
            to_port=port_b
        )

    def create_node_edge(self, device_name: str, connection: Dict) -> None:
        port_a = connection['portA']
        node_b = connection['nodeB']
        port_b = connection['portB']

        node_b_device_name = self.gen_device_name(node_b)

        self._create_edge(
            from_node_name=device_name,
            to_node_name=node_b_device_name,
            from_port=port_a,
            to_port=port_b
        )

    def _create_edge(
            self,
            from_node_name: str,
            to_node_name: str,
            from_port: int,
            to_port: int
    ) -> None:
        port_a_dir = self.get_direction_name(from_port)
        port_b_dir = self.get_direction_name(to_port)
        port_a_module = self.get_module(from_port)
        port_b_module = self.get_module(to_port)

        if 'switch' in from_node_name and 'switch' in to_node_name:
            # Верно только ребере между свитчами
            assert port_a_module == port_b_module, 'Modules must be the same in switch edge'

        from_name = f'[{from_node_name}_{from_port}_{port_a_dir}]'
        to_name = f'[{to_node_name}_{to_port}_{port_b_dir}]'
        edge_name = f'edge_from_{from_name}_to_{to_name}'

        node_id = self.add_node_name(edge_name)
        self.connect_nodes(from_node_name, edge_name)
        self.connect_nodes(edge_name, to_node_name)

        self._node_id_to_tags[node_id] = [
            'edge',
            f'from_port:{from_port}',
            f'to_port:{to_port}',
            f'from_dir:{port_a_dir}',
            f'to_dir:{port_b_dir}',
            f'from_node:{from_node_name}',
            f'to_node:{to_node_name}',
            f'from_module:{port_a_module}',
            f'to_module:{port_b_module}',
        ]

    def cast_to_graph(self) -> Graph:
        all_nodes: List[Node] = []
        for node_name, node_id in self._name_to_node_id.items():
            tags = self._node_id_to_tags[node_id]
            node = Node(node_id, node_name, tags)
            all_nodes.append(node)

        return Graph(all_nodes, self._nodes_from, self._nodes_to)

    def parse_topology(self, json_file_path: str) -> Graph:
        with open(json_file_path, 'r') as f:
            data = json.load(f)

        self.create_device_nodes(data)
        self.create_switches_graph(data)
        self.create_nodes_graph(data)

        print(self._names)
        print(self._name_to_node_id)
        print(self._nodes_from)
        print(self._nodes_to)

        return self.cast_to_graph()
