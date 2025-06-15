"""Dataset Cat - A tool for fetching and organizing anime datasets for training.

This package provides tools to fetch, process, and publish anime-related datasets.
"""

__version__ = "0.0.5"

from dataset_cat.crawler import Crawler
from dataset_cat.webui import launch_webui

__all__ = ["Crawler", "launch_webui"]
