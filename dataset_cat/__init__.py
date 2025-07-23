"""Dataset Cat - A tool for fetching and organizing anime datasets for training.

This package provides tools to fetch, process, and publish anime-related datasets.
"""

__version__ = "0.0.5"

from dataset_cat.crawler import Crawler
from dataset_cat.tag_translator import TagTranslator, translate_and_format
from dataset_cat.tag_translator_api import TagTranslatorAPI, translate_tag_request, get_supported_sources

__all__ = ["Crawler", "TagTranslator", "translate_and_format", "TagTranslatorAPI", "translate_tag_request", "get_supported_sources"]
