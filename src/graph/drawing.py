from diagrams import Cluster, Diagram, Edge, Node
from src.graph.graph_handler import GraphHandler

def wrap_text(text, max_length=15, isHTML=False):
    """Quebra o texto em múltiplas linhas sem cortar palavras, mesmo para palavras muito grandes."""
    words = text.split()
    lines = []
    current_line = []

    for word in words:
        # Se a palavra for maior que o comprimento máximo e a linha atual estiver vazia
        if len(word) > max_length and not current_line:
            lines.append(word)  # Adiciona a palavra como uma linha separada
        # Adiciona a palavra à linha atual se não ultrapassar o comprimento máximo
        elif sum(len(w) for w in current_line) + len(current_line) + len(word) <= max_length:
            current_line.append(word)
        else:
            # Junta as palavras da linha atual e adiciona à lista de linhas
            lines.append(" ".join(current_line))
            current_line = [word]  # Inicia uma nova linha com a palavra atual

    # Adiciona a última linha, se houver
    if current_line:
        lines.append(" ".join(current_line))

    if isHTML:
        return "<br/>".join(lines)  # Junta as linhas com quebras de linha em HTML
    else:
        return "\n".join(lines)

def set_node(label, width):
    wrapped_label = wrap_text(label)
    return Node(wrapped_label, labelloc="c", height="2", width=width)

def set_action_list(graph: GraphHandler) -> list:
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

def define_diagram(graph: GraphHandler, action_list: list):
    with Diagram("STPA", "stpa", direction="TB", curvestyle="ortho", graph_attr={
        "ranksep": "2.0",
        "constraint": "false",
    }):
        nodes = {}
        level_nodes = {0: [], 1: [], 2: [], 3: []} # Organizando nós por níveis
        
        # Primeira passagem: criar todos os nós para cada nível
        for level in range(graph.get_max_level() + 1):
            # Criar um sub-cluster para cada nível
            with Cluster(f"Level {level}", graph_attr={"rank": "same"}):
                # Encontrar todos os nós que pertencem a este nível
                for ac in action_list:
                    from_id = ac["from"]
                    to_id = ac["to"]
                    
                    # Processar nó de origem se estiver neste nível
                    if from_id and ac["from_level"] == level and from_id not in nodes:
                        from_width = "7"  # Aumentado para acomodar melhor o texto
                        nodes[from_id] = set_node(ac["from_label"], width=from_width)
                        level_nodes[level].append(from_id)
                        
                    # Processar nó de destino se estiver neste nível
                    if to_id and ac["to_level"] == level and to_id not in nodes:
                        to_width = "7"  # Aumentado para acomodar melhor o texto
                        nodes[to_id] = set_node(ac["to_label"], width=to_width)
                        level_nodes[level].append(to_id)
        
        # Segunda passagem: criar todas as conexões
        for ac in action_list:
            from_id = ac["from"]
            to_id = ac["to"]
            
            if from_id and to_id:
                action_label = wrap_text(ac["action"], max_length=10, isHTML=False)
                feedback_label = wrap_text(ac["feedback"], max_length=10, isHTML=False)
                
                # Adicionar conexão de ação
                nodes[from_id] >> Edge(
                    xlabel=f"{action_label}",
                    minlen="2" # Aumentar minlen para dar mais espaço
                ) >> nodes[to_id]
                
                # Adicionar conexão de feedback se existir
                if feedback_label:
                    nodes[to_id] >> Edge(
                        xlabel=f"{feedback_label}",
                        minlen="2",
                        style="dashed"
                    ) >> nodes[from_id]
        
        # Adicionar conexões invisíveis para forçar o fluxo vertical entre níveis
        # Isso garante que cada nível fique abaixo do anterior
        for level in range(graph.get_max_level()):
            if level_nodes[level] and level_nodes[level+1]:
                # Conectar o primeiro nó de cada nível ao primeiro nó do próximo nível
                # com uma aresta invisível para forçar a ordem vertical
                nodes[level_nodes[level][0]] >> Edge(constraint="true", style="invis") >> nodes[level_nodes[level+1][0]]