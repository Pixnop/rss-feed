"""
Fusionneur de flux RSS multiples
Combine plusieurs flux RSS en un seul flux unifié
"""
from typing import List, Dict, Any
from pathlib import Path
from feedgen.feed import FeedGenerator
from datetime import datetime
import xml.etree.ElementTree as ET
import logging

from .utils import load_yaml_config

logger = logging.getLogger(__name__)


class RSSMerger:
    """
    Fusionne plusieurs flux RSS en un seul
    """

    def __init__(self, merge_config: Dict[str, Any]):
        """
        Initialise le fusionneur

        Args:
            merge_config: Configuration de la fusion depuis sources.yaml
        """
        self.merge_config = merge_config

    def parse_rss_file(self, rss_file: str) -> List[Dict[str, Any]]:
        """
        Parse un fichier RSS et extrait les articles

        Args:
            rss_file: Chemin vers le fichier RSS

        Returns:
            Liste d'articles avec leurs métadonnées
        """
        articles = []
        file_path = Path(rss_file)

        if not file_path.exists():
            logger.warning(f"RSS file not found: {rss_file}")
            return articles

        try:
            tree = ET.parse(file_path)
            root = tree.getroot()

            # Trouver le channel
            channel = root.find('channel')
            if channel is None:
                logger.error(f"No channel found in {rss_file}")
                return articles

            # Extraire le nom de la source depuis le titre du channel
            source_title = channel.find('title')
            source_name = source_title.text if source_title is not None else "Unknown"

            # Parser chaque item
            for item in channel.findall('item'):
                try:
                    title_elem = item.find('title')
                    link_elem = item.find('link')
                    pubdate_elem = item.find('pubDate')
                    description_elem = item.find('description')
                    guid_elem = item.find('guid')

                    if title_elem is None or link_elem is None:
                        continue

                    title = title_elem.text or ""
                    link = link_elem.text or ""

                    # Parser la date
                    pub_date = None
                    if pubdate_elem is not None and pubdate_elem.text:
                        try:
                            # Format RFC 822 utilisé dans RSS
                            from email.utils import parsedate_to_datetime
                            pub_date = parsedate_to_datetime(pubdate_elem.text)
                        except Exception as e:
                            logger.debug(f"Failed to parse date '{pubdate_elem.text}': {e}")

                    article = {
                        'title': title,
                        'link': link,
                        'date': pub_date or datetime.now(),
                        'description': description_elem.text if description_elem is not None else title,
                        'guid': guid_elem.text if guid_elem is not None else link,
                        'source': source_name
                    }

                    articles.append(article)

                except Exception as e:
                    logger.error(f"Error parsing item in {rss_file}: {e}")
                    continue

            logger.info(f"Parsed {len(articles)} articles from {rss_file}")

        except Exception as e:
            logger.error(f"Error parsing RSS file {rss_file}: {e}", exc_info=True)

        return articles

    def merge_feeds(self, rss_files: List[str]) -> List[Dict[str, Any]]:
        """
        Fusionne plusieurs fichiers RSS

        Args:
            rss_files: Liste des chemins de fichiers RSS à fusionner

        Returns:
            Liste combinée d'articles
        """
        all_articles = []

        for rss_file in rss_files:
            articles = self.parse_rss_file(rss_file)
            all_articles.extend(articles)

        # Trier par date si configuré
        if self.merge_config.get('sort_by_date', True):
            all_articles.sort(key=lambda x: x['date'], reverse=True)

        # Limiter le nombre d'articles
        max_items = self.merge_config.get('max_items', 100)
        all_articles = all_articles[:max_items]

        logger.info(f"Merged {len(all_articles)} articles from {len(rss_files)} feeds")

        return all_articles

    def create_merged_feed(self, articles: List[Dict[str, Any]], output_file: str) -> bool:
        """
        Crée le flux RSS fusionné

        Args:
            articles: Liste des articles à inclure
            output_file: Chemin du fichier de sortie

        Returns:
            True si succès, False sinon
        """
        try:
            feed = FeedGenerator()

            # Métadonnées du flux fusionné
            feed.title(self.merge_config.get('title', 'Merged RSS Feed'))
            feed.link(href=self.merge_config.get('link', ''), rel='alternate')
            feed.description(self.merge_config.get('description', 'Combined RSS feeds'))
            feed.language(self.merge_config.get('language', 'en'))

            # Ajouter préfixe de source si configuré
            add_prefix = self.merge_config.get('add_source_prefix', True)

            for article in articles:
                try:
                    entry = feed.add_entry()

                    # Titre avec préfixe optionnel
                    title = article['title']
                    if add_prefix and 'source' in article:
                        title = f"[{article['source']}] {title}"

                    entry.title(title)
                    entry.link(href=article['link'])
                    entry.pubDate(article['date'])
                    entry.description(article['description'])
                    entry.guid(article['guid'], permalink=True)

                except Exception as e:
                    logger.error(f"Error adding article to merged feed: {e}")
                    continue

            # Générer le XML
            rss_content = feed.rss_str(pretty=True)

            # Écrire le fichier
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'wb') as f:
                f.write(rss_content)

            logger.info(f"Merged RSS feed generated successfully: {output_file}")
            return True

        except Exception as e:
            logger.error(f"Failed to create merged feed: {e}", exc_info=True)
            return False


def merge_feeds(source_files: List[str], config: Dict[str, Any], output_file: str) -> bool:
    """
    Fonction principale pour fusionner des flux RSS

    Args:
        source_files: Liste des fichiers RSS à fusionner
        config: Configuration de la fusion
        output_file: Chemin du fichier de sortie

    Returns:
        True si succès, False sinon
    """
    try:
        merger = RSSMerger(config)
        articles = merger.merge_feeds(source_files)
        return merger.create_merged_feed(articles, output_file)
    except Exception as e:
        logger.error(f"Failed to merge feeds: {e}", exc_info=True)
        return False


def merge_from_sources_config(sources_config_file: str = "config/sources.yaml") -> bool:
    """
    Fusionne les flux RSS selon la configuration sources.yaml

    Args:
        sources_config_file: Chemin vers le fichier sources.yaml

    Returns:
        True si succès, False sinon
    """
    try:
        config = load_yaml_config(sources_config_file)
        merge_config = config.get('merge', {})

        if not merge_config.get('enabled', False):
            logger.info("Merge is disabled in configuration")
            return True

        # Construire la liste des fichiers RSS à fusionner
        active_sources = config.get('active_sources', [])
        rss_files = []

        for source_name in active_sources:
            # Charger la config de la source pour trouver son output_file
            source_config_file = f"config/{source_name}.yaml"
            try:
                source_config = load_yaml_config(source_config_file)
                output_file = source_config['rss']['output_file']
                rss_file = Path('output') / output_file
                if rss_file.exists():
                    rss_files.append(str(rss_file))
                else:
                    logger.warning(f"RSS file not found for source '{source_name}': {rss_file}")
            except Exception as e:
                logger.error(f"Failed to load config for source '{source_name}': {e}")
                continue

        if not rss_files:
            logger.warning("No RSS files found to merge")
            return False

        # Fusionner
        output_file = Path('output') / merge_config.get('output_file', 'merged_feed.xml')
        return merge_feeds(rss_files, merge_config, str(output_file))

    except Exception as e:
        logger.error(f"Failed to merge from sources config: {e}", exc_info=True)
        return False