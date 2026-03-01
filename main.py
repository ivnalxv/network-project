from pathlib import Path
from typing import List

from graph import topology_parser
from graph.cdg import CdgBuilder, CycleChecker
from graph.torus import Torus

script_dir = Path(__file__).parent


def main():
    file_name = "graph/static/input_example.json"
    input_file_path = script_dir / file_name

    base_dimensions, module_nums = ['K', 'Z', 'Y', 'X'], 4
    parser = _get_topology_parser(base_dimensions, module_nums)
    graph = parser.parse_topology(str(input_file_path))

    file_name = "graph/static/output/graph.md"
    file_path = script_dir / file_name
    graph.print_mermaid(str(file_path))

    new_torus = Torus(graph, base_dimensions, module_nums)
    file_name = "graph/static/output/processed_graph.md"
    file_path = script_dir / file_name
    new_torus.topology_graph.print_torus_mermaid(str(file_path))

    next_node = new_torus.next_switch_node(from_node_id=5, by_module=3, by_direction='+K')
    print(f'\nNext node: {next_node}')

    next_node = new_torus.next_switch_node(from_node_id=5, by_module=1, by_direction='+K')
    print(f'\nNext node: {next_node}')

    all_edge_nodes = new_torus.get_all_edge_nodes()
    print('\nAll edge nodes:')
    for node in all_edge_nodes:
        print(f'- {node}')

    direction = new_torus.get_direction_by_edge_from_node(from_node_id=5, by_edge_id=1)
    print(f'\nDirection: {direction}')

    edge_id = 1
    print('\nAdjacent for edge: {edge_id}')
    for edge_adj in new_torus.get_adjacent_edges_by_edge_id(edge_id):
        print(f'- {edge_adj}')

    dim_order = ['+K', '+Z', '+Y', '-K', '-Z', '-Y', '+X', '-X']
    cdg = CdgBuilder(new_torus, dim_order)

    cdg_graph = cdg.build_cdg_graph()

    file_name = "graph/static/output/cdg_graph.md"
    output_file_path = script_dir / file_name
    cdg_graph.print_simple_mermaid(str(output_file_path))

    cycle_checker = CycleChecker(cdg_graph, new_torus)

    file_name = "graph/static/output/cdg_graph_with_cycle.md"
    output_file_path = script_dir / file_name
    cycle_checker.print_detailed_cycle(str(output_file_path))


def _get_topology_parser(
        base_dimensions: List[str],
        module_nums: int,
) -> topology_parser.TopologyParser:
    # ['+K', '-K', '+Z', '-Z', '+Y', '-Y', '+X', '-X'], num=8
    # module 1: 1, 2, 3, ..., 8
    # module 2: 9, 10, 11, ..., 16

    directions = []
    for base_dir in base_dimensions:
        directions.append('+' + base_dir)
        directions.append('-' + base_dir)

    return topology_parser.TopologyParser(directions, module_nums)


if __name__ == "__main__":
    main()
