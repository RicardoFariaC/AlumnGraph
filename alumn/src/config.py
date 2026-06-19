from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict


@dataclass
class DrawingConfig:
    NODE_WIDTH: str = "15"
    SOLO_NODE_WIDTH: str = "10"
    NODE_HEIGHT: str = "2"

    NODESEP: str = "4"
    RANKSEP: str = "2.0 equally"
    MINLEN: str = "3"

    WRAP_MAX_LENGTH: int = 15
    LABEL_FONT_SIZE: str = "60"
    EDGE_FONT_SIZE: str = "40"

    DEFAULT_NODE_COLOR: str = "white"
    DEFAULT_GROUP_COLOR: str = "lightblue"
    DEFAULT_EDGE_COLOR: str = "darkblue"

    GRAPH_DIRECTION: str = "TB"
    GRAPH_CURVESTYLE: str = "ortho"
    GRAPH_SPLINES: str = "ortho"

    EDGE_ARROWSIZE: str = "2.5"
    EDGE_DECORATE: str = "true"

    CLUSTER_MARGIN: str = "10"
    CLUSTER_LABELJUST: str = "c"
    CLUSTER_RANK: str = "same"


@dataclass
class ValidationConfig:
    MIN_NODE_LEVEL: int = 0
    MAX_NODE_LEVEL: int = 10
    MIN_LABEL_LENGTH: int = 1
    MAX_LABEL_LENGTH: int = 100
    MIN_ID_LENGTH: int = 1
    MAX_ID_LENGTH: int = 50

    REQUIRED_JSON_KEYS: tuple = ("controllers", "actions")
    OPTIONAL_JSON_KEYS: tuple = ("groups",)

    REQUIRED_ACTION_KEYS: tuple = ("from", "to", "action")
    OPTIONAL_ACTION_KEYS: tuple = ("feedback",)

    REQUIRED_CONTROLLER_KEYS: tuple = ("id", "label", "level")
    REQUIRED_GROUP_KEYS: tuple = ("id", "label", "controllers_list")


@dataclass
class FileConfig:
    SUPPORTED_INPUT_FORMATS: tuple = (".json",)
    SUPPORTED_OUTPUT_FORMATS: tuple = ("svg", "png", "pdf")

    DEFAULT_OUTPUT_DIR: str = "."
    DEFAULT_OUTPUT_NAME: str = "stpa"

    MAX_JSON_FILE_SIZE: int = 10 * 1024 * 1024


class Config:
    def __init__(self):
        self.drawing = DrawingConfig()
        self.validation = ValidationConfig()
        self.file = FileConfig()

    def get_drawing_params(self) -> Dict[str, Any]:
        return {
            "node_width": self.drawing.NODE_WIDTH,
            "nodesep": self.drawing.NODESEP,
            "solo_node_width": self.drawing.SOLO_NODE_WIDTH,
            "wrap_max_length": self.drawing.WRAP_MAX_LENGTH,
            "minlen": self.drawing.MINLEN,
            "label_font_size": self.drawing.LABEL_FONT_SIZE,
            "edge_font_size": self.drawing.EDGE_FONT_SIZE,
            "ranksep": self.drawing.RANKSEP,
        }

    def validate_file_path(self, file_path: str) -> Path:
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if path.suffix.lower() not in self.file.SUPPORTED_INPUT_FORMATS:
            raise ValueError(
                f"Unsupported file format: {path.suffix}.\nSupported formats: {self.file.SUPPORTED_INPUT_FORMATS}."
            )

        if path.stat().st_size > self.file.MAX_JSON_FILE_SIZE:
            raise ValueError(f"File too large:  {path.stat().st_size}")

        return path


config = Config()
