"""Utility functions for dataset operations.

This module provides helper functions for common tasks across the application.
"""

import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Union

import numpy as np
from PIL import Image


def setup_logging(level: int = logging.INFO) -> logging.Logger:
    """Set up the logging configuration for the application.

    Args:
        level: The logging level (default: logging.INFO)

    Returns:
        The configured logger instance
    """
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    return logging.getLogger("dataset_cat")


def ensure_directory(directory_path: str) -> str:
    """Ensure a directory exists, creating it if necessary.

    Args:
        directory_path: Path to the directory

    Returns:
        The absolute path to the directory
    """
    path = Path(directory_path).expanduser().resolve()
    os.makedirs(path, exist_ok=True)
    return str(path)


def list_image_files(directory_path: str) -> List[str]:
    """List all image files in a directory.

    Args:
        directory_path: Path to the directory

    Returns:
        List of image file paths
    """
    valid_extensions = (".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tiff", ".gif")
    result = []

    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.lower().endswith(valid_extensions):
                result.append(os.path.join(root, file))

    return result


def calculate_image_statistics(image_paths: List[str]) -> dict:
    """Calculate statistics for a list of images.

    Args:
        image_paths: List of paths to image files

    Returns:
        Dictionary containing statistics (min/max/avg dimensions, file sizes)
    """
    if not image_paths:
        return {
            "count": 0,
            "avg_width": 0,
            "avg_height": 0,
            "min_width": 0,
            "min_height": 0,
            "max_width": 0,
            "max_height": 0,
            "avg_file_size_mb": 0,
            "min_file_size_mb": 0,
            "max_file_size_mb": 0,
        }

    widths = []
    heights = []
    file_sizes = []

    for path in image_paths:
        try:
            with Image.open(path) as img:
                widths.append(img.width)
                heights.append(img.height)

            file_sizes.append(os.path.getsize(path) / (1024 * 1024))  # Size in MB
        except Exception:
            # Skip files that can't be processed
            pass

    if not widths:  # All files failed to process
        return {
            "count": 0,
            "avg_width": 0,
            "avg_height": 0,
            "min_width": 0,
            "min_height": 0,
            "max_width": 0,
            "max_height": 0,
            "avg_file_size_mb": 0,
            "min_file_size_mb": 0,
            "max_file_size_mb": 0,
        }

    return {
        "count": len(widths),
        "avg_width": np.mean(widths),
        "avg_height": np.mean(heights),
        "min_width": min(widths),
        "min_height": min(heights),
        "max_width": max(widths),
        "max_height": max(heights),
        "avg_file_size_mb": np.mean(file_sizes),
        "min_file_size_mb": min(file_sizes),
        "max_file_size_mb": max(file_sizes),
    }


def format_time_elapsed(seconds: float) -> str:
    """Format seconds into human-readable time string.

    Args:
        seconds: Time in seconds

    Returns:
        Formatted time string (e.g. "2h 30m 45s")
    """
    hours, remainder = divmod(int(seconds), 3600)
    minutes, seconds = divmod(remainder, 60)

    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0 or hours > 0:
        parts.append(f"{minutes}m")
    parts.append(f"{seconds}s")

    return " ".join(parts)


def convert_tag_for_source(
    tag: Union[str, List[str]],
    source: str,
    zh2en_dict: Optional[Dict[str, str]] = None,
) -> List[str]:
    """Convert input tag(s) to the appropriate search keywords for a given imageboard source.

    This function standardizes tags for different booru sources (e.g., danbooru, safebooru, e621).
    It also supports basic Chinese-to-English tag translation (can be extended with a dictionary or API).

    Args:
        tag: The input tag or list of tags (can be English or Chinese)
        source: The target source name (e.g., 'danbooru', 'safebooru', 'e621')
        zh2en_dict: Optional dictionary for Chinese-to-English tag translation

    Returns:
        List of tags/keywords suitable for the target source

    Raises:
        ValueError: If the source is not supported
    """
    # Always work with a list of tags
    if isinstance(tag, str):
        tags = [tag]
    else:
        tags = tag

    # Step 1: Translate Chinese tags to English if needed
    def zh2en(single_tag: str) -> str:
        # Simple dictionary-based translation; can be replaced with API or more advanced logic
        if zh2en_dict and single_tag in zh2en_dict:
            return zh2en_dict[single_tag]
        # TODO: Integrate with a real translation service or expand dictionary
        return single_tag

    tags = [zh2en(t) for t in tags]

    # Step 2: Source-specific tag adaptation
    source = source.lower()
    if source in {"danbooru", "safebooru", "yandere", "konachan", "lolibooru"}:
        # Danbooru-like: tags are space-separated, lowercase, underscores for spaces
        return [t.replace(" ", "_").lower() for t in tags]
    elif source in {"e621", "e926"}:
        # e621: tags are also space-separated, lowercase, underscores for spaces
        return [t.replace(" ", "_").lower() for t in tags]
    else:
        raise ValueError(f"Unsupported source: {source}")


__all__ = [
    "setup_logging",
    "ensure_directory",
    "list_image_files",
    "calculate_image_statistics",
    "format_time_elapsed",
    "convert_tag_for_source",
]
