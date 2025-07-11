"""
Download MCP Server

This module provides MCP server functionality for downloading files from URLs.
It supports HTTP/HTTPS downloads with configurable options and returns LLM-friendly formatted results.

Key features:
- Download files from HTTP/HTTPS URLs
- Configurable timeout and overwrite options
- Custom headers support for authentication
- LLM-optimized output formatting
- Comprehensive error handling and logging
- Path validation and directory creation

Main functions:
- mcp_download_file: Download files from URLs with comprehensive options
- mcp_get_download_capabilities: Get download service capabilities
"""

import os
import shutil
import time
import traceback
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlparse

import requests
from pydantic import BaseModel, Field

from ..action_collection import ActionArguments, ActionCollection, ActionResponse


class DownloadResult(BaseModel):
    """Structured result for a single download operation."""

    url: str
    file_path: str
    success: bool
    file_size_bytes: int | None = None
    duration_seconds: float
    timestamp: str
    status_code: int | None = None
    content_type: str | None = None
    error_message: str | None = None
    error_type: str | None = None


class DownloadMetadata(BaseModel):
    """Metadata for download operation results."""

    url: str
    output_path: str
    timeout_seconds: int
    overwrite_enabled: bool
    execution_time: float | None = None
    file_size_bytes: int | None = None
    content_type: str | None = None
    status_code: int | None = None
    error_type: str | None = None
    headers_used: bool = False


class DownloadCollection(ActionCollection):
    """MCP service for secure and robust file download operations."""

    def __init__(self, arguments: ActionArguments) -> None:
        super().__init__(arguments)

        # Configuration
        self.default_timeout = 60 * 3  # 3 minutes
        self.max_file_size = 1024 * 1024 * 1024  # 1GB limit
        self.supported_schemes = {"http", "https"}

        self.base_headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/91.0.4472.124 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
        }

        self.logger.info("Download service initialized.")
        self.logger.debug(f"Workspace: {self.workspace}")

    def _validate_url(self, url: str) -> tuple[bool, str | None]:
        """Validate URL format and scheme.

        Args:
            url: URL to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            parsed = urlparse(url)

            if not parsed.scheme:
                return False, "URL must include a scheme (http:// or https://)"

            if parsed.scheme.lower() not in self.supported_schemes:
                return False, f"Unsupported URL scheme: {parsed.scheme}. Supported: {', '.join(self.supported_schemes)}"

            if not parsed.netloc:
                return False, "URL must include a valid domain"

            return True, None

        except Exception as e:
            self.logger.warning(f"URL validation failed for '{url}': {e}")
            return False, f"Invalid URL format: {str(e)}"

    def _resolve_output_path(self, output_path: str) -> Path | None:
        """Resolve, validate, and secure the output file path."""
        try:
            # Prevent absolute paths outside the workspace from being used directly
            if os.path.isabs(output_path):
                self.logger.warning(
                    f"Absolute path specified: '{output_path}'. It will be treated as relative to the workspace."
                )
                # Sanitize by removing leading slashes to treat it as relative
                output_path = output_path.lstrip("/\\ ")

            # Join with workspace and resolve (e.g., handles '..')
            resolved_path = (self.workspace / output_path).resolve()

            # Security check: ensure the final path is within the workspace
            if self.workspace.resolve() not in resolved_path.parents and resolved_path != self.workspace.resolve():
                self.logger.error(
                    f"Path traversal attempt blocked: '{output_path}' resolved to '{resolved_path}' which is outside the workspace."
                )
                return None

            # Ensure parent directory exists
            resolved_path.parent.mkdir(parents=True, exist_ok=True)
            return resolved_path
        except Exception as e:
            self.logger.error(f"Error resolving output path '{output_path}': {e}")
            return None

    def _format_download_output(self, result: DownloadResult, output_format: str = "markdown") -> str:
        """Format download results for LLM consumption.

        Args:
            result: Download execution result
            output_format: Format type ('markdown', 'json', 'text')

        Returns:
            Formatted string suitable for LLM consumption
        """
        if output_format == "json":
            return result.model_dump_json(indent=2)

        elif output_format == "text":
            output_parts = [
                f"URL: {result.url}",
                f"File Path: {result.file_path}",
                f"Status: {'SUCCESS' if result.success else 'FAILED'}",
                f"Duration: {result.duration_seconds:.2f}s",
                f"Timestamp: {result.timestamp}",
            ]

            if result.file_size_bytes is not None:
                output_parts.append(f"File Size: {result.file_size_bytes:,} bytes")

            if result.error_message:
                output_parts.append(f"Error: {result.error_message}")

            return "\n".join(output_parts)

        else:  # markdown (default)
            status_emoji = "✅" if result.success else "❌"

            output_parts = [
                f"# File Download {status_emoji}",
                f"**URL:** `{result.url}`",
                f"**File Path:** `{result.file_path}`",
                f"**Status:** {'SUCCESS' if result.success else 'FAILED'}",
                f"**Duration:** {result.duration_seconds:.2f}s",
                f"**Timestamp:** {result.timestamp}",
            ]

            if result.file_size_bytes is not None:
                size_mb = result.file_size_bytes / (1024 * 1024)
                output_parts.append(f"**File Size:** {result.file_size_bytes:,} bytes ({size_mb:.2f} MB)")

            if result.error_message:
                output_parts.extend(
                    [
                        "\n## Error Details",
                        f"**Type:** `{result.error_type}`" if result.error_type else "",
                        f"```\n{result.error_message}\n```",
                    ]
                )

            return "\n".join(filter(None, output_parts))

    async def _download_file_async(
        self, url: str, output_path: Path, timeout: int, headers: dict[str, str]
    ) -> DownloadResult:
        """Download a file with pre-flight checks and detailed error handling."""
        start_time = time.monotonic()

        try:
            with requests.get(url, headers=headers, stream=True, timeout=timeout) as response:
                # Check for Content-Length to fail early for large files
                content_length_str = response.headers.get("Content-Length")
                if content_length_str and int(content_length_str) > self.max_file_size:
                    raise ValueError(
                        f"File size ({int(content_length_str) / 1e6:.2f} MB) exceeds the maximum limit of {self.max_file_size / 1e6:.2f} MB."
                    )

                response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

                # Download in chunks
                file_size = 0
                temp_file_path = output_path.with_suffix(f"{output_path.suffix}.tmp")
                with open(temp_file_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        file_size += len(chunk)
                        if file_size > self.max_file_size:
                            os.remove(temp_file_path)
                            raise ValueError(
                                f"File download exceeded the maximum size limit of {self.max_file_size / 1e6:.2f} MB."
                            )
                        f.write(chunk)

                # Move temporary file to final destination
                shutil.move(temp_file_path, output_path)

                return DownloadResult(
                    url=url,
                    file_path=str(output_path),
                    success=True,
                    file_size_bytes=file_size,
                    duration_seconds=time.monotonic() - start_time,
                    timestamp=datetime.now(UTC).isoformat(),
                    status_code=response.status_code,
                    content_type=response.headers.get("Content-Type"),
                )

        except requests.exceptions.RequestException as e:
            error_type = e.__class__.__name__
            error_message = f"Network or HTTP error: {e}"
        except OSError as e:
            error_type = e.__class__.__name__
            error_message = f"File system error: {e}"
        except ValueError as e:
            error_type = e.__class__.__name__
            error_message = str(e)
        except Exception as e:
            error_type = e.__class__.__name__
            error_message = f"An unexpected error occurred: {e}"
            self.logger.error(f"Unexpected download error for {url}:\n{traceback.format_exc()}")

        return DownloadResult(
            url=url,
            file_path=str(output_path),
            success=False,
            duration_seconds=time.monotonic() - start_time,
            timestamp=datetime.now(UTC).isoformat(),
            error_message=error_message,
            error_type=error_type,
        )

    async def mcp_download_file(
        self,
        url: str = Field(description="URL of the file to download."),
        output_path: str = Field(description="File path to save the download. Can be relative to the workspace."),
        timeout: int | None = Field(default=None, description="Download timeout in seconds."),
        overwrite: bool = Field(default=False, description="Overwrite the file if it already exists."),
        headers: dict[str, str] | None = Field(default=None, description="Custom headers for the download request."),
        output_format: str = Field(default="markdown", description="Output format ('markdown', 'json', 'text')."),
    ) -> ActionResponse:
        """Download a file from a URL with options for timeout, overwrite, and custom headers."""
        self.logger.info(f"Initiating download for URL: {url}")

        is_valid, error = self._validate_url(url)
        if not is_valid:
            return ActionResponse(success=False, message=f"Invalid URL: {error}")

        final_path = self._resolve_output_path(output_path)
        if not final_path:
            return ActionResponse(success=False, message="Invalid output path specified.")

        if final_path.exists() and not overwrite:
            message = f"File already exists at '{final_path}'. Use overwrite=True to replace it."
            self.logger.warning(message)
            return ActionResponse(success=False, message=message)

        # Prepare headers
        request_headers = self.base_headers.copy()
        if headers:
            request_headers.update(headers)

        # Execute download
        download_timeout = timeout if timeout is not None else self.default_timeout
        result = await self._download_file_async(url, final_path, download_timeout, request_headers)

        # Format and return response
        formatted_output = self._format_download_output(result, output_format)
        return ActionResponse(
            success=result.success,
            message="Download completed." if result.success else "Download failed.",
            result=result.model_dump_json(indent=2),
            formatted_output=formatted_output,
        )

    async def mcp_get_download_capabilities(self) -> ActionResponse:
        """Get information about download service capabilities and configuration.

        Returns:
            ActionResponse with download service capabilities and current configuration
        """
        capabilities = {
            "requests_available": requests is not None,
            "supported_schemes": list(self.supported_schemes),
            "supported_features": [
                "HTTP/HTTPS URL downloads",
                "Configurable timeout controls",
                "Custom headers support",
                "Path validation and directory creation",
                "File size limits and safety checks",
                "Multiple output formats (markdown, json, text)",
                "LLM-optimized result formatting",
                "Comprehensive error handling",
            ],
            "supported_formats": ["markdown", "json", "text"],
            "configuration": {
                "default_timeout": self.default_timeout,
                "max_file_size_bytes": self.max_file_size,
                "workspace": str(self.workspace),
            },
            "safety_features": [
                "URL validation",
                "File size limits",
                "Timeout controls",
                "Path validation",
                "Overwrite protection",
                "Error handling and logging",
            ],
        }

        max_size_mb = self.max_file_size / (1024 * 1024)
        formatted_info = f"""# Download Service Capabilities

        ## Status
        - **Workspace:** `{self.workspace}`

        ## Supported Features
        {chr(10).join(f"- {feature}" for feature in capabilities["supported_features"])}

        ## Supported URL Schemes
        {chr(10).join(f"- {scheme}://" for scheme in capabilities["supported_schemes"])}

        ## Supported Output Formats
        {chr(10).join(f"- {fmt}" for fmt in capabilities["supported_formats"])}

        ## Configuration
        - **Default Timeout:** {capabilities["configuration"]["default_timeout"]} seconds
        - **Max File Size:** {self.max_file_size:,} bytes ({max_size_mb:.1f} MB)

        ## Safety Features
        {chr(10).join(f"- {feature}" for feature in capabilities["safety_features"])}
        """

        return ActionResponse(
            success=True,
            message=formatted_info,
            metadata=capabilities,
        )


# Default arguments for testing
if __name__ == "__main__":
    arguments = ActionArguments(
        name="download",
        transport="stdio",
        workspace=os.getenv("AWORLD_WORKSPACE", "~"),
    )
    try:
        service = DownloadCollection(arguments)
        service.run()
    except Exception as e:
        print(f"An error occurred: {e}: {traceback.format_exc()}")
