from pathlib import Path
from typing import List

from graph import topology_parser
from graph.cdg import CdgBuilder, CycleChecker
from graph.entities import Graph, NdTorus

script_dir = Path(__file__).parent


def main():
    file_name = "graph/static/input_example.json"
    input_file_path = script_dir / file_name

    base_dimensions, module_nums = ['K', 'Z', 'Y', 'X'], 4
    parser = _get_topology_parser(base_dimensions, module_nums)
    graph = parser.parse_topology(str(input_file_path))

    file_name = "graph/static/output/graph.md"
    output_file_path = script_dir / file_name
    graph.print_mermaid(str(output_file_path))

    torus = NdTorus(graph, base_dimensions, module_nums)

    print('\nReal nodes:')
    for node in torus.get_real_nodes():
        print(node)

    dim_order = ['+K', '+Z', '+Y', '-K', '-Z', '-Y', '+X', '-X']
    cdg = CdgBuilder(torus, dim_order)

    from_dim = '-X'
    to_dim = '+X'
    print(f'\nTurn from "{from_dim}" to "{to_dim}" possible: {cdg.check_turn(from_dim, to_dim)}')

    cdg_graph = cdg.build_cdg_graph()

    file_name = "graph/static/output/cdg_graph.md"
    output_file_path = script_dir / file_name
    cdg_graph.print_mermaid(str(output_file_path))

    cycle_checker = CycleChecker(cdg_graph)
    print(f'Has cycle: {cycle_checker.has_cycle()}')


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
