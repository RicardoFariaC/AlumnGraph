from diagrams import Cluster, Diagram, Edge, Node
from alumn.src.graph.graph_handler import GraphHandler
import textwrap

def wrap_text(text, max_length=30, isHTML=False):
    """Quebra o texto em múltiplas linhas sem cortar palavras, mesmo para palavras muito grandes."""
    lines = textwrap.wrap(text, width=max_length)
    sep = "<br/>" if isHTML else "\n"
    return sep.join(lines)

def set_node(label, width="1", fontsize="20"):

    wrapped_label = wrap_text(label)
    return Node(wrapped_label, labelloc="c", height="1", width=width, fixedsize="true", style="filled", fillcolor="white", fontsize=fontsize)

def set_action_list(graph: GraphHandler) -> list:
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

    ac_list = []
    for action in graph.get_control_action():
        ac_list.append({
            "from": action["from"].get_id() if action["from"] else None,
            "to": action["to"].get_id() if action["to"] else None,
            "from_label": action["from"].get_label() if action["from"] else "",
            "to_label": action["to"].get_label() if action["to"] else "",
            "action": action["action"],
            "feedback": action.get("feedback", ""),
            "from_level": action["from"].get_level() if action["from"] else 0,
            "to_level": action["to"].get_level() if action["to"] else 0,
        })
    return ac_list

def prepare_diagram_data(graph: GraphHandler, action_list: list):
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
    
    level_nodes = {level: set() for level in range(graph.get_max_level() + 1)}
    node_to_group = defaultdict(list)
    groups_data = {}
    
    # Determinar os grupos
    for group in graph.groups:
        group_id = group.get("id")
        group_label = group.get("label")
        controllers_list = group.get("controllers_list", [])
        groups_data[group_id] = {
            "label": group_label,
            "nodes": controllers_list
        }
        
        for node_id in controllers_list:
            node_to_group.setdefault(node_id, []).append(group_id)
    

    # Identificar nós
    node_info = {}
    for ac in action_list:
        from_id = ac["from"]
        to_id = ac["to"]
        
        if from_id:
            if from_id not in node_info:
                node_info[from_id] = {
                    "level": ac["from_level"],
                    "label": ac["from_label"],
                    "group": node_to_group.get(from_id, [])
                }
            level_nodes[ac["from_level"]].add(from_id)
        
        if to_id:
            if to_id not in node_info:
                node_info[to_id] = {
                    "level": ac["to_level"],
                    "label": ac["to_label"],
                    "group": node_to_group.get(to_id, [])
                }
            level_nodes[ac["to_level"]].add(to_id)
    

    level_nodes = {level: list(nodes) for level, nodes in level_nodes.items()}
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
    
    group_colors = {group_id: "lightblue" for group_id in groups_data}
    
    return {
        "level_nodes": level_nodes,
        "node_info": node_info,
        "nodes_by_level_and_group": nodes_by_level_and_group,
        "ungrouped_nodes": ungrouped_nodes,
        "groups_data": groups_data,
        "group_colors": group_colors,
        "max_level": graph.get_max_level()
    }

def render_diagram(diagram_data, action_list):
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

    DEFAULT_PARAMS = {
        "node_width": "15",
        "node_separation": "1.5",  
        "solo_node_width": "10",
        "wrap_max_length": 15,
        "edge_min_length": "2",
        "label_font_size": "30",
        "edge_font_size": "20",
    }

    level_nodes = diagram_data["level_nodes"]
    node_info = diagram_data["node_info"]
    nodes_by_level_and_group = diagram_data["nodes_by_level_and_group"]
    ungrouped_nodes = diagram_data["ungrouped_nodes"]
    groups_data = diagram_data["groups_data"]
    group_colors = diagram_data["group_colors"]
    max_level = diagram_data["max_level"]
    
    with Diagram("STPA", "stpa", direction="TB", curvestyle="ortho", graph_attr={
        "ranksep": "1.5",
        "nodesep": DEFAULT_PARAMS["node_separation"],
        "constraint": "true",
        "splines": "ortho",
        "newrank": "true",
        "center": "true",
    }, outformat="svg"):
        nodes = {}
        
        # FASE 1: Criar clusters por nível para manter a hierarquia vertical
        for level in range(max_level + 1):
            if not level_nodes[level]:
                continue
            
            with Cluster(f"Level {level}", graph_attr={
                "rank": "same",
                "style": "invis",
                "labeljust": "c",
            }):
                # Criar sub-clusters para grupos neste nível
                if level in nodes_by_level_and_group:
                    for group_id, grouped_nodes_list in nodes_by_level_and_group[level].items():
                        # Criar um sub-cluster visível para este grupo neste nível
                        with Cluster(f"{groups_data[group_id]['label']} (Level {level})", graph_attr={
                            "style": "", 
                            "color": "darkblue",
                            "bgcolor": group_colors[group_id],
                            "fontsize": DEFAULT_PARAMS["label_font_size"],
                            "labeljust": "c",
                            "rank": "same",
                            "margin": "10"
                        }):
                            # Criar nós dentro deste grupo
                            for node_id in grouped_nodes_list:
                                node_label = node_info[node_id]["label"]
                                solo_node = len(grouped_nodes_list) == 1
                                nodes[node_id] = set_node(node_label, width=DEFAULT_PARAMS["node_width"] if not 
                                                  solo_node else DEFAULT_PARAMS["solo_node_width"], fontsize=DEFAULT_PARAMS["label_font_size"])
                
                # Criar nós não agrupados neste nível
                if level in ungrouped_nodes:
                    for node_id in ungrouped_nodes[level]:
                        node_label = node_info[node_id]["label"]
                        solo_node = len(ungrouped_nodes[level]) == 1 and not nodes_by_level_and_group.get(level)
                        nodes[node_id] = set_node(node_label, width=DEFAULT_PARAMS["node_width"] if not 
                                                  solo_node else DEFAULT_PARAMS["solo_node_width"], fontsize=DEFAULT_PARAMS["label_font_size"])
                
                # Conectar todos os nós deste nível horizontalmente para manter o rank
                level_node_ids = level_nodes[level]
                for i in range(len(level_node_ids) - 1):
                    if level_node_ids[i] in nodes and level_node_ids[i+1] in nodes:
                        nodes[level_node_ids[i]] >> Edge(style="invis", constraint="true", weight="5") >> nodes[level_node_ids[i+1]]
        
        # FASE 2: Criar todas as conexões reais e invisíveis
        for ac in action_list:
            from_id = ac["from"]
            to_id = ac["to"]
            
            if from_id and to_id and from_id in nodes and to_id in nodes:
                action_label = wrap_text(ac["action"], max_length=DEFAULT_PARAMS["wrap_max_length"], isHTML=False)
                feedback_label = wrap_text(ac["feedback"], max_length=DEFAULT_PARAMS["wrap_max_length"], isHTML=False)
                nodes[from_id] >> Edge(
                    xlabel=f"{action_label}",
                    minlen=DEFAULT_PARAMS["edge_min_length"],
                    weight="1",
                    fontsize=DEFAULT_PARAMS["edge_font_size"]
                ) >> nodes[to_id]
                
                if feedback_label:
                    nodes[to_id] >> Edge(
                        xlabel=f"{feedback_label}",
                        minlen=DEFAULT_PARAMS["edge_min_length"],
                        style="dashed",
                        weight="1",
                        fontsize=DEFAULT_PARAMS["edge_font_size"]
                    ) >> nodes[from_id]
        
        # Criar conexões invisíveis fortes entre níveis
        for level in range(max_level):
            if level_nodes[level] and level_nodes[level+1]:
                fst_node_cur = next((n for n in level_nodes[level] if n in nodes), None)
                fst_node_nxt = next((n for n in level_nodes[level+1] if n in nodes), None)

                if fst_node_cur and fst_node_nxt:
                    nodes[fst_node_cur] >> Edge(
                        constraint="true", 
                        style="", 
                        color="red",
                        weight="30"
                    ) >> nodes[fst_node_nxt]

def define_diagram(graph: GraphHandler, action_list: list):
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
    render_diagram(diagram_data, action_list)