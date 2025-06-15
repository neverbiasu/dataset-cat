"""Main entry point for Dataset Cat.

This module provides the command-line interface and launches the application.
"""

import argparse
import sys
from typing import List, Optional

from dataset_cat import __version__
from dataset_cat.core.utils import setup_logging
from dataset_cat.webui import launch_webui


def parse_arguments(args: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command line arguments.

    Args:
        args: Command line arguments (defaults to sys.argv[1:])

    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Dataset Cat - A tool for fetching and organizing anime datasets for training",
    )

    parser.add_argument("--version", action="version", version=f"Dataset Cat v{__version__}")

    parser.add_argument("-p", "--port", type=int, default=7860, help="Port to run the web UI on (default: 7860)")

    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind the web UI to (default: 0.0.0.0)")

    parser.add_argument("--debug", action="store_true", help="Enable debug mode")

    parser.add_argument("--share", action="store_true", help="Share the web UI publicly (using Gradio sharing)")

    return parser.parse_args(args)


def main(args: Optional[List[str]] = None) -> None:
    """Main entry point for the application.

    Args:
        args: Command line arguments (defaults to sys.argv[1:])
    """
    parsed_args = parse_arguments(args)

    # Setup logging based on debug flag
    logger = setup_logging()
    logger.info(f"Dataset Cat v{__version__} starting...")

    # Launch web UI
    print(f"Launching Dataset Cat WebUI on port {parsed_args.port}...")
    launch_webui(
        host=parsed_args.host,
        port=parsed_args.port,
        debug=parsed_args.debug,
        share=parsed_args.share,
    )


if __name__ == "__main__":
    main()
