import networkx as nx
import json
from alumn.src.graph.node import Node

class GraphHandler:
    def __init__(self, json_file=None):
        """
        Initializes the GraphHandler object.

        Args:
            json_file (str, optional): Path to a JSON file containing graph data. 
                                       Defaults to None.

        Attributes:
            __G (networkx.DiGraph): A directed graph instance from NetworkX.
            nodelist (dict): A dictionary to store node-related data.
        """
        self.__G = nx.DiGraph()
        self.nodelist = {}
        self.load_json(json_file=json_file)

    def load_json(self, json_file):
        """
        Load a JSON file and parse its contents into the graph structure.
        Args:
            json_file (str): The file path to the JSON file to be loaded.
        Raises:
            Exception: If the file cannot be loaded or parsed, an exception is raised with an error message.
        Notes:
            - The JSON file is expected to contain the following keys:
                - 'controllers': A list of controllers.
                - 'groups': A list of groups.
                - 'actions': A list of control actions, where each action contains 'from' and 'to' keys.
            - The 'from' and 'to' keys in actions are replaced with corresponding Node instances.
            - Additional levels ('from_level' and 'to_level') are added to each action based on the nodes.
        """
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
        """
        Private method to populate the `self.nodes` list with `Node` objects 
        based on the data in `self.controllers`.

        Iterates through the `self.controllers` list, creating a `Node` object 
        for each entry using its "id", "label", and "level" attributes. The 
        created `Node` is appended to `self.nodes` if its "id" matches an 
        entry in `self.controllers`.

        Note:
            This method assumes that `self.controllers` is a list of dictionaries 
            where each dictionary contains the keys "id", "label", and "level".

        Raises:
            KeyError: If any of the required keys ("id", "label", "level") are 
                      missing in the dictionaries within `self.controllers`.
        """
        for node_data in self.controllers:
            node = Node(id=node_data["id"], label=node_data["label"], level=node_data["level"])
            for c in range(len(self.controllers)):
                if node_data["id"] == self.controllers[c]["id"]:
                    self.nodes.append(node)


    def create_graph(self):
        """
        Creates a directed graph from the loaded JSON data.

        This method processes the JSON data stored in `self.controllers` and 
        `self.control_actions` to construct a directed graph. Nodes are created 
        from the `self.controllers` data and added to the graph, while edges 
        are created from the `self.control_actions` data to establish connections 
        between the nodes.

        Raises:
            Exception: If the JSON data required to create the graph is not loaded 
            or if there is an issue during the graph creation process.

        Notes:
            - Each node is represented as an instance of the `Node` class and is 
              stored in `self.nodes`.
            - Edges are added to the graph with attributes such as `action` and 
              optional `feedback`.

        Attributes:
            self.controllers (list): A list of dictionaries containing node data 
                with keys "id", "label", and "level".
            self.control_actions (list): A list of dictionaries containing edge 
                data with keys "from", "to", "action", and optional "feedback".
            self.__G (networkx.DiGraph): The directed graph instance where nodes 
                and edges are added.

        Example:
            Assuming `self.controllers` and `self.control_actions` are populated 
            with valid data:
            
            self.create_graph()
        """
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
        """
        Iterate over the nodes in the graph.

        Args:
            data (bool, optional): If True, yield a tuple of (node, node_data) 
            for each node. If False, yield only the node. Defaults to False.

        Yields:
            Union[Hashable, Tuple[Hashable, Any]]: The node or a tuple of 
            (node, node_data) depending on the value of the `data` parameter.
        """
        for node in self.__G.nodes(data=data):
            yield node

    def check_nodes(self, data=False, pretty_print=False):
        """
        Checks and prints the nodes of the graph.

        Args:
            data (bool, optional): If True, includes node data in the output. Defaults to False.
            pretty_print (bool, optional): If True, prints each node on a separate line. 
                                            Otherwise, prints all nodes in a single line. Defaults to False.

        Returns:
            None
        """
        if pretty_print:
            for node in self.__G.nodes(data=data):
                print(node)
        else:
            print(self.__G.nodes(data=data))
        
    def get_linked_nodes(self, node_id):
        """
        Retrieves all nodes that are directly linked to the specified node.

        Args:
            node_id (Any): The identifier of the node whose linked nodes are to be retrieved.

        Returns:
            list: A list of nodes that are directly linked to the given node_id.

        Raises:
            Exception: If an error occurs during the retrieval process, an exception is raised
                       with a message indicating that a valid node_id must be provided.
        """
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
        print(self.__G.edges(data=data))

    def get_edges(self, data=False):
        return self.__G.edges(data=data)

    def get_control_action(self, json_dump=False):
        """
        Retrieves a list of valid control actions.

        Args:
            json_dump (bool, optional): If True, returns the control actions as a JSON-formatted string.
                                        Defaults to False.

        Returns:
            list or str: A list of valid control actions if `json_dump` is False,
                         otherwise a JSON-formatted string representing the control actions.
        """
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