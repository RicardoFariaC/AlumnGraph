class Node:
    def __init__(self, id, label, level):
        self.__id = id
        self.__label = label
        self.__level = level
        self.__linked_nodes = set()  # Use a set to avoid duplicates

    def add_linked_node(self, node):
        """Add a linked node."""
        self.__linked_nodes.add(node)

    def get_linked_nodes(self):
        """Return linked nodes as a list."""
        return list(self.__linked_nodes)
    
    def get_id(self):
        """Return the ID of the node."""
        return self.__id
    
    def get_label(self):
        """Return the label of the node."""
        return self.__label
    
    def get_level(self):
        """Return the level of the node."""
        return self.__level
    
    def __str__(self):
        """String representation of the node."""
        return f"Node(id={self.__id}, label={self.__label}, level={self.__level})"