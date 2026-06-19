import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass

from alumn.src.graph.node import Node
from alumn.src.config import config

@dataclass
class ControlAction:
    from_node: Optional[Node]
    to_node: Optional[Node]
    action: str
    feedback: str = ''

class GraphHandler:
    def __init__(self, json_file: str) -> None:
        """
        Inicializa o objeto de gerenciamento de grafo.

        Args:
            json_file (str): Caminho para o arquivo JSON contendo as definições de grafo.
        """
        self.controllers: List[Dict[str, Any]] = []
        self.groups: List[Dict[str, Any]] = []
        self.nodes: Dict[str, Node] = {}
        self.control_actions: List[ControlAction] = []

        self.load_json(json_file=json_file)
        self._validate_graph_integrity()

    def load_json(self, json_file):
        """
        Carrega um arquivo JSON e realiza a leitura de seu conteúdo em uma
        estrutura de grafo.
        Args:
            json_file (str): O caminho do arquivo JSON a ser carregado.
        Raises:
            Exception: Se o arquivo não pode ser carregado ou lido, uma exceção é chamada
                com uma mensagem de erro.
        Notas:
            - Espera-se que o arquivo JSON tenha os seguintes itens:
                - 'controllers': Lista de controladores.
                - 'groups': Lista de grupos.
                - 'actions': Lista de ações de controle (control actions), 
                  onde cada ação contém chaves 'from' e 'to'.
            - As chaves 'to' e 'from' são substituídas pelas respectivas instâncias de 'Node'.
            - Niveis adicionais ('from_level' e 'to_level') 
              são criados baseados em cada ação dos nós.
        """
        try:
            json_path = config.validate_file_path(json_file)

            with open(json_path) as f:
                data = json.load(f)
                
                self._validate_json_structure(data)

                self.controllers = self._validate_controllers(data['controllers'])
                self.groups = self._validate_groups(data.get('groups', []))

                self._create_nodes()
                self._process_control_actions(data['actions'])

        except FileNotFoundError as e:
            logging.error(f"Error while loading file: {e}")
            raise
        except json.JSONDecodeError as e:
            logging.error(f"Error while decoding JSON: {e}")
            raise
        except KeyError as e:
            logging.error(f"Error on JSON structure: {e}")
            raise
        except ValueError as e:
            logging.error(f"Validation error: {e}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error while loading JSON: {e}")
            raise

    def _validate_json_structure(self, data: Dict[str, Any]) -> None:
        missing_keys = [key for key in config.validation.REQUIRED_JSON_KEYS if key not in data]
        if missing_keys:
            raise KeyError(f"Missing required keys in JSON: {missing_keys}")
        
        if not isinstance(data['controllers'], list):
            raise ValueError("'controllers' must be a list")
        if not isinstance(data['actions'], list):
            raise ValueError("'actions' must be a list")
        if 'groups' in data and not isinstance(data['groups'], list):
            raise ValueError("'groups' must be a list")

    def _validate_controllers(self, controllers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not controllers:
            raise ValueError("At least one controller is required")
        
        controllers_id: Set[str] = set()

        for i, controller in enumerate(controllers):
            missing_keys = [key for key in config.validation.REQUIRED_CONTROLLER_KEYS if key not in controller]
            if missing_keys:
                raise ValueError(f"Controller {i}: Missing required keys: {missing_keys}")

            controller_id = controller['id']
            if controller_id in controllers_id:
                raise ValueError(f'Duplicate controller ID: {controller_id}')
            controllers_id.add(controller_id)

            if not isinstance(controller['label'], str):
                raise ValueError(f"Controller {i}: 'label' must be a string")
            if not isinstance(controller['level'], int):
                raise ValueError(f"Controller {i}: 'level' must be an integer")
            if controller['level'] < config.validation.MIN_NODE_LEVEL or controller['level'] > config.validation.MAX_NODE_LEVEL:
                raise ValueError(f"Controller {i}: 'level' must be between {config.validation.MIN_NODE_LEVEL} and {config.validation.MAX_NODE_LEVEL}")

        return controllers

    def _validate_groups(self, groups: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        group_ids: Set[str] = set()

        for i, group in enumerate(groups):
            missing_keys = [key for key in config.validation.REQUIRED_GROUP_KEYS if key not in group]
            if missing_keys:
                raise ValueError(f"Group {i}: Missing required keys: {missing_keys}")

            group_id = group['id']
            if group_id in group_ids:
                raise ValueError(f'Duplicate group ID: {group_id}')
            group_ids.add(group_id)
        
            controllers_list = group.get('controllers_list', [])
            if not isinstance(controllers_list, list):
                raise ValueError(f"Group {i}: 'controllers_list' must be a list")

        return groups

    def _create_nodes(self) -> None:
        try:
            for controller in self.controllers:
                node = Node(
                    id=controller['id'],
                    label=controller['label'],
                    level=controller['level']
                )
                self.nodes[node.get_id()] = node
        except Exception as e:
            raise ValueError(f"Failed to create nodes: {e}")

    def _process_control_actions(self, actions: List[Dict[str, Any]]) -> None:
        for i, action in enumerate(actions):
            missing_keys = [key for key in config.validation.REQUIRED_ACTION_KEYS if key not in action]
            if missing_keys:
                raise ValueError(f"Action {i}: Missing required keys: {missing_keys}")

            from_id = action['from']
            to_id = action['to']

            if from_id not in self.nodes:
                raise ValueError(f"Action {i}: 'from' node '{from_id}' not found in controllers")
            if to_id not in self.nodes:
                raise ValueError(f"Action {i}: 'to' node '{to_id}' not found in controllers")

            control_action = ControlAction(
                from_node=self.nodes[from_id],
                to_node=self.nodes[to_id],
                action=action['action'],
                feedback=action.get('feedback', ''),
            )
            self.control_actions.append(control_action)
            self.nodes[from_id].add_linked_node(self.nodes[to_id])

    def _validate_graph_integrity(self) -> None:
        connected_nodes: Set[str] = set()
        for action in self.control_actions:
            if action.from_node:
                connected_nodes.add(action.from_node.get_id())
            if action.to_node:
                connected_nodes.add(action.to_node.get_id())
        
        isolated_nodes = set(self.nodes.keys()) - connected_nodes
        if isolated_nodes:
            logging.warning(f"Isolated nodes found: {isolated_nodes}")

        self._check_for_cycles()

    def _check_for_cycles(self) -> None:
        visited = set()
        rec_stack = set()

        def has_cycle_util(node_id: str, current_level: int) -> bool:
            if node_id in rec_stack:
                return True
            if node_id in visited:
                return False

            visited.add(node_id)
            rec_stack.add(node_id)
        
            node = self.nodes.get(node_id)
            if node:
                for linked_node in node.get_linked_nodes():
                    linked_node_id = linked_node.get_id()
                    linked_node_level = linked_node.get_level()

                    if linked_node_level == current_level:
                        continue

                    if has_cycle_util(linked_node_id, linked_node_level):
                        return True
            rec_stack.remove(node_id)
            return False
        
        for node_id in self.nodes:
            node = self.nodes.get(node_id)
            if node:
                level = node.get_level()
                if has_cycle_util(node_id, level):
                    raise ValueError(f"Cross-level cycle detected in graph starting from node: {node_id} (level {level})")

    def get_control_action(self, json_dump: bool = False) -> List[Dict[str, Any]] | str:
        """
        ### PT:

        Recupera uma lista de ações de controle válidas.

        Args:
            json_dump (bool, optional): Se True, retorna as ações de controle como uma string JSON.
                                        Padrão é False.

        Returns:
            list or str: Uma lista de control actions válidas se if `json_dump` is False,
                         senão uma string em formato JSON representando as control actions.

        ### EN:
        Retrieves a list of valid control actions.

        Args:
            json_dump (bool, optional): If True, returns the control actions as a JSON-formatted string.
                                        Defaults to False.

        Returns:
            list or str: A list of valid control actions if `json_dump` is False,
                         otherwise a JSON-formatted string representing the control actions.
        """
        actions_data = []
        for action in self.control_actions:
            action_dict = {
                'from': action.from_node.get_id() if action.from_node else None,
                'to': action.to_node.get_id() if action.to_node else None,
                'action': action.action,
                'feedback': action.feedback,
            }
            actions_data.append(action_dict)

        if json_dump:
            return json.dumps(actions_data, indent=2)
        return actions_data
    
    def get_max_level(self) -> int:
        """Query for the maximum level available."""
        if not self.controllers:
            return 0
        return max(controller["level"] for controller in self.controllers)
        
    def get_node_level(self, node_id: str) -> int:
        """Get the level of a node by its ID."""
        node = self.nodes.get(node_id)
        return node.get_level()
    
    def get_node_by_id(self, node_id: str) -> Optional[Node]:
        return self.nodes.get(node_id)
    
    def get_all_nodes(self) -> List[Node]:
        return list(self.nodes.values())

    def get_nodes_by_level(self, level: int) -> List[Node]:
        return [node for node in self.nodes.values if node.get_level() == level]
