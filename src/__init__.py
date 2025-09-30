"""
Générateur RSS Universel Multi-Sources
Configuration over Code - Fail Gracefully - Document Everything
"""

__version__ = "1.0.0"

from .scraper import scrape_source, GenericScraper
from .rss_generator import generate_rss, generate_rss_from_config, RSSGenerator
from .merger import merge_feeds, merge_from_sources_config, RSSMerger
from .utils import load_yaml_config, make_absolute_url, setup_logging

__all__ = [
    'scrape_source',
    'GenericScraper',
    'generate_rss',
    'generate_rss_from_config',
    'RSSGenerator',
    'merge_feeds',
    'merge_from_sources_config',
    'RSSMerger',
    'load_yaml_config',
    'make_absolute_url',
    'setup_logging',
]