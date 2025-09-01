from typing import Set, List
from dataclasses import dataclass

@dataclass
class NodeConfig:
    MIN_LEVEL: int = 0
    MAX_LEVEL: int = 10
    MIN_LABEL_LENGTH: int = 1
    MAX_LABEL_LENGTH: int = 100
    MIN_ID_LENGTH: int = 1
    MAX_ID_LENGTH: int = 50

class Node:
    def __init__(self, id: str, label: str, level: int) -> None:
        self._validate_params(id, label, level)
        
        self.__id = id
        self.__label = label
        self.__level = level
        self.__linked_nodes: Set["Node"] = set()

    @staticmethod
    def _validate_params(id: str, label: str, level: int) -> None:
        config = NodeConfig()

        if len(id) < config.MIN_ID_LENGTH or len(id) >  config.MAX_ID_LENGTH:
            raise ValueError(f"Node eID length must be between {config.MIN_ID_LENGTH} and {config.MAX_ID_LENGTH}")
        if not id.strip():
            raise ValueError("Node ID cannot be empty or whitespace")
        if len(label) < config.MIN_LABEL_LENGTH or len(label) > config.MAX_LABEL_LENGTH:
            raise ValueError(f"Node label legnth must be between {config.MIN_LABEL_LENGTH} and {config.MAX_LABEL_LENGTH}")
        if not label.strip():
            raise ValueError("Node label cannot be empty or whitespace")
        if level < config.MIN_LEVEL or level > config.MAX_LEVEL:
            raise ValueError(f"Node level must be between {config.MIN_LEVEL} and {config.MAX_LEVEL}")

    def __str__(self):
        return self.__label + " " + self.__level

    def add_linked_node(self, node: 'Node') -> None:
        """
        Add a linked node to this node's connections.
        
        Args:
            node: Node to link to this node
        """
        self.__linked_nodes.add(node)

    def get_linked_nodes(self) -> List['Node']:
        """Return linked nodes as a list."""
        return list(self.__linked_nodes)
    
    def get_id(self) -> str:
        """Return the ID of the node."""
        return self.__id
    
    def get_label(self) -> str:
        """Return the label of the node."""
        return self.__label
    
    def get_level(self) -> str:
        """Return the level of the node."""
        return self.__level
    
    def has_linked_node(self, node:'Node') -> bool:
        "Return True if nodes are linked, False otherwise"
        return node in self.__linked_nodes

    def get_degree(self) -> int:
        "Return the number of linked nodes"
        return len(self.__linked_nodes)