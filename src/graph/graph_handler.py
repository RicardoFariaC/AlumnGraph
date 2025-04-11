import networkx as nx
import json
from .node import Node

class GraphHandler:
    def __init__(self, json_file=None):
        self.__G = nx.DiGraph()
        self.nodelist = {}
        self.load_json(json_file=json_file)

    def load_json(self, json_file):
        """Load a JSON from file and parse it into the graph."""
        try:
            with open(json_file) as f:
                d = json.load(f)
                self.controllers: list = d['controllers']
                self.groups = d['groups']
                self.nodes =[]
                
                self.__into_nodes()

                # Add levels to control actions and replace "from" and "to" with Node instances
                node_dict = {node.get_id(): node for node in self.nodes}
                self.control_actions = [
                    {
                        **action,
                        'from': node_dict.get(action['from']),
                        'to': node_dict.get(action['to']),
                        'from_level': node_dict.get(action['from']).get_level() if node_dict.get(action['from']) else None,
                        'to_level': node_dict.get(action['to']).get_level() if node_dict.get(action['to']) else None
                    }
                    for action in d['actions']
                ]
        except Exception as e:
            print(f"JsonLoadException: You cannot load a json file without providing a valid file path. \
                \n{e}")

    def __into_nodes(self):
        for node_data in self.controllers:
            node = Node(id=node_data["id"], label=node_data["label"], level=node_data["level"])
            for c in range(len(self.controllers)):
                if node_data["id"] == self.controllers[c]["id"]:
                    self.nodes.append(node)


    def create_graph(self):
        """Creates a directed graph from the loaded JSON data."""
        try:
            # Create Node instances and add them to the graph
            for node_data in self.controllers:
                node = Node(id=node_data["id"], label=node_data["label"], level=node_data["level"])
                self.nodes[node.get_id()] = node
                self.__G.add_node(node.get_id(), node=node)

            # Add edges to the graph
            for action in self.control_actions:
                from_node = self.nodes.get(action["from"])
                to_node = self.nodes.get(action["to"])
                if from_node and to_node:
                    from_node.add_linked_node(to_node)
                    self.__G.add_edge(
                        from_node.get_id(),
                        to_node.get_id(),
                        action=action["action"],
                        feedback=action.get("feedback", "")
                    )
        except Exception as e:
            print(f"GraphCreationException: You cannot create a graph without loading a json file into it. \
                \n{e}")

    def iterate_nodes(self, data=False):
        """Returns a iterable of nodes in the graph."""
        for node in self.__G.nodes(data=data):
            yield node

    def check_nodes(self, data=False, pretty_print=False):
        """Verifies the nodes in the graph by printing them in the stdout."""
        if pretty_print:
            for node in self.__G.nodes(data=data):
                print(node)
        else:
            print(self.__G.nodes(data=data))
        
    def get_linked_nodes(self, node_id):
        """Get all nodes that are linked to the given node_id."""
        linked_nodes = []
        try:
            for edge in self.__G.edges(data=True):
                if edge[0] == node_id:
                    linked_nodes.append(edge[1])
            return linked_nodes
        except Exception as e:
            print(f"GetLinkedNodesException: You cannot get linked nodes without providing a valid node_id. \
                \n{e}")

    def check_edges(self, data=False):
        """Verifies the edges in the graph by printing them in the stdout."""
        print(self.__G.edges(data=data))

    def get_edges(self, data=False):
        """Returns all edges in the graph."""
        return self.__G.edges(data=data)

    def get_control_action(self, json_dump=False):
        """Returns a list of valid control actions."""
        if json_dump:
            dumped_json = json.dumps(self.control_actions)
            return dumped_json
        else:
            return self.control_actions
    
    def get_max_level(self):
        """Query for the maximum level available."""
        if self.controllers:
            return max([node["level"] for node in self.controllers])
        
    def get_node_level(self, node_id):
        """Get the level of a node by its ID."""
        return self.nodelist[node_id].level if node_id in self.nodelist else 0