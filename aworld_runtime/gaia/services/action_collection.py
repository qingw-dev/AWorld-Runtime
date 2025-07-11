import logging
import os
from pathlib import Path
from typing import Any, Literal

from aworld.logs.util import Color
from mcp.server import FastMCP
from pydantic import BaseModel, Field

from ...logging_utils import color_log, setup_logger


class ActionArguments(BaseModel):
    """Protocol: MCP Action Arguments"""

    name: str = Field(description="The name of the action")
    transport: Literal["stdio", "sse"] = Field(default="stdio", description="The transport of the action")
    port: int = Field(default=8000, description="The port for the SSE server")
    workspace: str | None = Field(
        default=None,
        description="The workspace of the action. If not specified, it falls back to AWORLD_WORKSPACE env or home dir.",
    )
    unittest: bool = Field(default=False, description="Whether to run in unittest mode")


class ActionResponse(BaseModel):
    """Protocol: MCP Action Response"""

    success: bool = Field(default=False, description="Whether the action is successfully executed")
    message: Any = Field(default=None, description="The execution result of the action")
    metadata: dict[str, Any] = Field(default_factory=dict, description="The metadata of the action")


class ActionCollection:
    """Base class for all ActionCollection."""

    server: FastMCP
    logger: logging.Logger

    def __init__(self, arguments: ActionArguments) -> None:
        self.unittest = arguments.unittest
        self.transport = arguments.transport
        self.port = arguments.port
        self.supported_extensions: set[str] = set()

        self.workspace: Path = self._obtain_valid_workspace(arguments.workspace)

        self.logger: logging.Logger = setup_logger(self.__class__.__name__, str(self.workspace))

        self.server = FastMCP(arguments.name)
        for tool_name in dir(self):
            if tool_name.startswith("mcp_") and callable(getattr(self, tool_name)):
                tool = getattr(self, tool_name)
                self.server.add_tool(tool, description=tool.__doc__)

    def run(self) -> None:
        """Run the MCP server based on the specified transport."""
        if self.unittest:
            return

        if self.transport == "stdio":
            self.server.run(transport="stdio")
        elif self.transport == "sse":
            self.server.run(transport="sse", port=self.port)

    def _color_log(self, value: str, color: Color | None = None, level: str = "info") -> None:
        color_log(self.logger, value, color, level=level)

    def _obtain_valid_workspace(self, workspace: str | None) -> Path:
        """
        Obtain a valid workspace path, checking user input, environment variables, and home directory.
        """
        path_str = workspace or os.getenv("AWORLD_WORKSPACE")
        if path_str:
            path = Path(path_str).expanduser().resolve()
            if path.is_dir():
                return path

        self._color_log("Invalid or no workspace specified, using home directory.", Color.yellow)
        return Path.home().expanduser().resolve()

    def _validate_file_path(self, file_path: str) -> Path:
        """Validate and resolve a file path, ensuring it exists and has a supported extension."""
        path = Path(file_path).expanduser()
        if not path.is_absolute():
            path = self.workspace / path

        if not path.exists():
            raise FileNotFoundError(f"The file does not exist: {path}")

        if path.suffix.lower() not in self.supported_extensions:
            raise ValueError(
                f"Unsupported file type: '{path.suffix}'. Supported types are: {', '.join(self.supported_extensions)}."
            )

        return path
