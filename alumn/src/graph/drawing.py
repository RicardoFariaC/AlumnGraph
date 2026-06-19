import textwrap
from typing import Any, Dict, List

from diagrams import Cluster, Diagram, Edge, Node

from alumn.src.config import config
from alumn.src.graph.graph_handler import ControlAction, GraphHandler


def wrap_text(text: str, max_length: int = 30, isHTML: bool = False) -> str:
    """Quebra o texto em múltiplas linhas sem cortar palavras, mesmo para palavras muito grandes."""
    lines = textwrap.wrap(text, width=max_length)
    sep = "<br/>" if isHTML else "\n"
    return sep.join(lines)


def set_node(label: str, width: str = "1", fontsize: str = "20") -> Node:
    wrapped_label = wrap_text(label)
    return Node(
        wrapped_label,
        labelloc="c",
        height=config.drawing.NODE_HEIGHT,
        width=width,
        fixedsize="true",
        style="filled",
        fillcolor=config.drawing.DEFAULT_NODE_COLOR,
        fontsize=fontsize,
    )


def set_action_list(graph: GraphHandler) -> List[ControlAction]:
    """
    Gera uma lista de ações a partir das ações de controle do grafo fornecido.

    Cada ação na lista é representada como um dicionário contendo detalhes
    sobre os nós de origem e destino, seus rótulos, níveis, o tipo de ação
    e feedback opcional.

    Args:
        graph (GraphHandler): O objeto manipulador de grafo contendo as ações de controle.

    Returns:
        list: Uma lista de dicionários, onde cada dicionário representa uma ação
              com as seguintes chaves:
              - "from" (str ou None): O ID do nó de origem, ou None se não aplicável.
              - "to" (str ou None): O ID do nó de destino, ou None se não aplicável.
              - "from_label" (str): O rótulo do nó de origem, ou uma string vazia se não aplicável.
              - "to_label" (str): O rótulo do nó de destino, ou uma string vazia se não aplicável.
              - "action" (str): O tipo de ação.
              - "feedback" (str): Feedback opcional associado à ação (padrão é uma string vazia).
              - "from_level" (int): O nível do nó de origem, ou 0 se não aplicável.
              - "to_level" (int): O nível do nó de destino, ou 0 se não aplicável.
    """
    return graph.control_actions


def prepare_diagram_data(
    graph: GraphHandler, action_list: List[ControlAction]
) -> Dict[str, Any]:
    """
    Prepara e organiza os dados necessários para renderizar o diagrama STPA.

    Esta função é responsável por processar os dados de entrada, analisar as relações
    entre nós e grupos, e organizar as estruturas de dados necessárias para visualização.

    Args:
        graph: Instância de GraphHandler contendo as informações do grafo
        action_list: Lista de ações de controle extraídas do grafo

    Returns:
        Dicionário contendo as estruturas de dados organizadas para renderização
    """
    from collections import defaultdict

    level_nodes: Dict[int, str] = {
        level: set() for level in range(graph.get_max_level() + 1)
    }
    node_to_group: Dict[str, List[str]] = defaultdict(list)
    groups_data: Dict[str, Dict[str, Any]] = {}

    for group in graph.groups:
        group_id = group.get("id")
        group_label = group.get("label")
        controllers_list = group.get("controllers_list", [])
        groups_data[group_id] = {"label": group_label, "nodes": controllers_list}

        for node_id in controllers_list:
            node_to_group.setdefault(node_id, []).append(group_id)

    node_info: Dict[str, Any] = {}
    for action in action_list:
        from_node = action.from_node
        to_node = action.to_node

        if from_node and to_node:
            from_id = from_node.get_id()
            to_id = to_node.get_id()
            from_level = from_node.get_level()
            to_level = to_node.get_level()

            if from_id not in node_info:
                node_info[from_id] = from_node
            level_nodes[from_level].add(from_id)

            if to_id not in node_info:
                node_info[to_id] = to_node

            level_nodes[to_level].add(to_id)

    level_nodes = {level: list(nodes) for level, nodes in level_nodes.items()}
    remove_empty_entries(level_nodes)

    nodes_by_level_and_group = defaultdict(lambda: defaultdict(list))
    ungrouped_nodes = defaultdict(list)

    # Definir os nós pelo grupo
    for level in level_nodes:
        nodes_in_level = level_nodes[level]

        for node_id in nodes_in_level:
            if node_id in node_to_group:
                # Associar o nó ao seu grupo principal (primeiro grupo na lista)
                group_id = node_to_group[node_id][0]
                nodes_by_level_and_group[level][group_id].append(node_id)
            else:
                if level not in ungrouped_nodes:
                    ungrouped_nodes[level] = []
                ungrouped_nodes[level].append(node_id)

    group_colors = {
        group_id: config.drawing.DEFAULT_GROUP_COLOR for group_id in groups_data
    }

    return {
        "level_nodes": level_nodes,
        "node_info": node_info,
        "nodes_by_level_and_group": nodes_by_level_and_group,
        "ungrouped_nodes": ungrouped_nodes,
        "groups_data": groups_data,
        "group_colors": group_colors,
        "max_level": len(level_nodes) - 1,
    }


def render_diagram(
    diagram_data: Dict[str, Any],
    action_list: List[ControlAction],
    filename: str,
    output_format: str,
) -> None:
    """
    Renderiza o diagrama STPA com base nos dados preparados.

    Esta função é responsável pela parte visual do diagrama, criando clusters,
    nós e conexões conforme as estruturas de dados fornecidas.

    Args:
        diagram_data: Dicionário contendo as estruturas de dados organizadas
        action_list: Lista de ações de controle

    Returns:
        None (o diagrama é salvo como arquivo)
    """

    drawing_params = config.get_drawing_params()

    level_nodes = diagram_data["level_nodes"]
    node_info = diagram_data["node_info"]
    nodes_by_level_and_group = diagram_data["nodes_by_level_and_group"]
    ungrouped_nodes = diagram_data["ungrouped_nodes"]
    groups_data = diagram_data["groups_data"]
    group_colors = diagram_data["group_colors"]
    max_level = diagram_data["max_level"]

    with Diagram(
        filename.split("/")[-1].upper(),
        filename,
        direction="TB",
        curvestyle="ortho",
        graph_attr={
            "ranksep": drawing_params["ranksep"],
            "nodesep": drawing_params["nodesep"],
            "constraint": "true",
            "splines": config.drawing.GRAPH_SPLINES,
            "newrank": "true",
            "center": "true",
        },
        edge_attr={
            "decorate": config.drawing.EDGE_DECORATE,
            "arrowsize": config.drawing.EDGE_ARROWSIZE,
            "fontsize": config.drawing.EDGE_FONT_SIZE,
        },
        outformat=output_format,
    ):
        nodes: Dict[str, Any] = {}

        # FASE 1: Criar clusters por nível para manter a hierarquia vertical
        for level in range(max_level + 1):
            if not level_nodes[level]:
                continue

            with Cluster(
                f"Level {level}",
                graph_attr={
                    "rank": "same",
                    "style": "invis",
                    "labeljust": config.drawing.CLUSTER_LABELJUST,
                    "margin": "2",
                },
            ):
                if level in nodes_by_level_and_group:
                    for group_id, grouped_nodes_list in nodes_by_level_and_group[
                        level
                    ].items():
                        with Cluster(
                            f"{groups_data[group_id]['label']} (Level {level})",
                            graph_attr={
                                "color": config.drawing.DEFAULT_EDGE_COLOR,
                                "bgcolor": group_colors[group_id],
                                "fontsize": drawing_params["label_font_size"],
                                "labeljust": config.drawing.CLUSTER_LABELJUST,
                                "rank": config.drawing.CLUSTER_RANK,
                                "margin": config.drawing.CLUSTER_MARGIN,
                            },
                        ):
                            for node_id in grouped_nodes_list:
                                node_label = node_info[node_id].get_label()
                                solo_node = len(grouped_nodes_list) == 1
                                nodes[node_id] = set_node(
                                    node_label,
                                    width=drawing_params["node_width"]
                                    if not solo_node
                                    else drawing_params["solo_node_width"],
                                    fontsize=drawing_params["label_font_size"],
                                )
                if level in ungrouped_nodes:
                    for node_id in ungrouped_nodes[level]:
                        node_label = node_info[node_id].get_label()
                        solo_node = len(
                            ungrouped_nodes[level]
                        ) == 1 and not nodes_by_level_and_group.get(level)
                        nodes[node_id] = set_node(
                            node_label,
                            width=drawing_params["node_width"]
                            if not solo_node
                            else drawing_params["solo_node_width"],
                            fontsize=drawing_params["label_font_size"],
                        )

                level_node_ids = level_nodes[level]
                for i in range(len(level_node_ids) - 1):
                    if level_node_ids[i] in nodes and level_node_ids[i + 1] in nodes:
                        (
                            nodes[level_node_ids[i]]
                            >> Edge(style="invis", constraint="true", weight="5")
                            >> nodes[level_node_ids[i + 1]]
                        )

        # FASE 2: Criar todas as conexões reais e invisíveis
        for action in action_list:
            from_node = action.from_node
            to_node = action.to_node

            if from_node and to_node:
                from_id = from_node.get_id()
                to_id = to_node.get_id()

                if from_id in nodes and to_id in nodes:
                    action_label = wrap_text(
                        action.action,
                        max_length=drawing_params["wrap_max_length"],
                        isHTML=False,
                    )
                    feedback_label = wrap_text(
                        action.feedback,
                        max_length=drawing_params["wrap_max_length"],
                        isHTML=False,
                    )

                    (
                        nodes[from_id]
                        >> Edge(
                            xlabel=action_label,
                            minlen=drawing_params["minlen"],
                            weight="1",
                            fontsize=drawing_params["edge_font_size"],
                            labeldistance="4.0",
                        )
                        >> nodes[to_id]
                    )

                    if feedback_label:
                        (
                            nodes[to_id]
                            >> Edge(
                                xlabel=feedback_label,
                                minlen=drawing_params["minlen"],
                                style="dashed",
                                weight="1",
                                fontsize=drawing_params["edge_font_size"],
                                color="darkorchid3",
                                fontcolor="darkorchid4",
                                labeldistance="4.0",
                            )
                            >> nodes[from_id]
                        )

        # Criar conexões invisíveis fortes entre níveis
        for level in range(max_level):
            if level_nodes[level] and level_nodes[level + 1]:
                fst_node_cur = next((n for n in level_nodes[level] if n in nodes), None)
                fst_node_nxt = next(
                    (n for n in level_nodes[level + 1] if n in nodes), None
                )

                if fst_node_cur and fst_node_nxt:
                    (
                        nodes[fst_node_cur]
                        >> Edge(constraint="true", style="invis", weight="30")
                        >> nodes[fst_node_nxt]
                    )


def define_diagram(
    graph: GraphHandler,
    action_list: List[ControlAction],
    filename: str = "stpa",
    output_format: str = "svg",
) -> None:
    """
    Função principal que configura e renderiza o diagrama STPA.

    Esta função agora está separada em duas etapas:
    1. Preparação dos dados (prepare_diagram_data)
    2. Renderização do diagrama (render_diagram)

    Args:
        graph: Instância de GraphHandler contendo as informações do grafo
        action_list: Lista de ações de controle extraídas do grafo

    Returns:
        None (o diagrama é salvo como arquivo)
    """
    diagram_data = prepare_diagram_data(graph, action_list)
    render_diagram(diagram_data, action_list, filename, output_format)


def remove_empty_entries(level_nodes: Dict[int, List[str]]) -> None:
    """
    Esta função removerá entradas vazias e ajustará os níveis conforme a necessidade

    Considerando que `level_nodes` tenha a seguinte conformação:
    {
        1: [],
        2: [],
        3: []
    }

    e que `action_list` tenha a seguinte conformação:
    [
        {
            "from":"",
            "to":"",
            "action":"",
            "feedback":""
        }
    ]
    """
    for level in level_nodes:
        next_level = level_nodes.get(level + 1, None)

        if level_nodes[level] == [] and next_level:
            level_nodes[level] = level_nodes[level + 1]
            level_nodes[level + 1] = []

    remove_level = []
    for level in level_nodes:
        if level_nodes[level] == []:
            remove_level.append(level)

    for i in remove_level:
        del level_nodes[i]
