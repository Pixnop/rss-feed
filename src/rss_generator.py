"""
Générateur de flux RSS à partir de données d'articles
"""
from typing import List, Dict, Any
from pathlib import Path
from feedgen.feed import FeedGenerator
import logging

from .utils import load_yaml_config

logger = logging.getLogger(__name__)


class RSSGenerator:
    """
    Génère des flux RSS conformes au standard RSS 2.0
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialise le générateur RSS

        Args:
            config: Configuration complète du flux (source + rss)
        """
        self.config = config
        self.source_config = config.get('source', {})
        self.rss_config = config.get('rss', {})

    def create_feed(self) -> FeedGenerator:
        """
        Crée une instance FeedGenerator avec les métadonnées du flux

        Returns:
            Instance FeedGenerator configurée
        """
        feed = FeedGenerator()

        # Métadonnées principales
        feed.title(self.rss_config.get('title', self.source_config.get('name', 'RSS Feed')))
        feed.link(href=self.rss_config.get('link', self.source_config.get('url', '')), rel='alternate')
        feed.description(self.rss_config.get('description', self.source_config.get('description', '')))

        # Langue
        language = self.rss_config.get('language', self.source_config.get('language', 'en'))
        feed.language(language)

        return feed

    def add_articles(self, feed: FeedGenerator, articles: List[Dict[str, Any]]) -> None:
        """
        Ajoute les articles au flux RSS

        Args:
            feed: Instance FeedGenerator
            articles: Liste d'articles à ajouter
        """
        max_items = self.rss_config.get('max_items', 50)

        for i, article in enumerate(articles[:max_items]):
            try:
                entry = feed.add_entry()

                # Titre
                entry.title(article['title'])

                # Lien
                entry.link(href=article['link'])

                # Date de publication
                entry.pubDate(article['date'])

                # Description
                description = article.get('description', article['title'])
                entry.description(description)

                # GUID (identifiant unique) basé sur l'URL
                entry.guid(article['link'], permalink=True)

                # Auteur (optionnel)
                if 'author' in article:
                    entry.author(name=article['author'])

            except Exception as e:
                logger.error(f"Error adding article '{article.get('title', 'unknown')}' to feed: {e}")
                continue

        logger.info(f"Added {min(len(articles), max_items)} articles to feed")

    def generate(self, articles: List[Dict[str, Any]], output_file: str) -> bool:
        """
        Génère le fichier RSS complet

        Args:
            articles: Liste des articles à inclure
            output_file: Chemin du fichier de sortie

        Returns:
            True si succès, False sinon
        """
        try:
            # Créer le flux
            feed = self.create_feed()

            # Ajouter les articles
            self.add_articles(feed, articles)

            # Générer le XML
            rss_content = feed.rss_str(pretty=True)

            # Écrire dans le fichier
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'wb') as f:
                f.write(rss_content)

            logger.info(f"RSS feed generated successfully: {output_file}")
            return True

        except Exception as e:
            logger.error(f"Failed to generate RSS feed: {e}", exc_info=True)
            return False


def generate_rss(articles: List[Dict[str, Any]], config: Dict[str, Any], output_file: str) -> bool:
    """
    Fonction principale pour générer un flux RSS

    Args:
        articles: Liste des articles
        config: Configuration complète (source + rss)
        output_file: Chemin du fichier de sortie

    Returns:
        True si succès, False sinon
    """
    try:
        generator = RSSGenerator(config)
        return generator.generate(articles, output_file)
    except Exception as e:
        logger.error(f"Failed to generate RSS: {e}", exc_info=True)
        return False


def generate_rss_from_config(config_file: str, articles: List[Dict[str, Any]]) -> bool:
    """
    Génère un flux RSS depuis un fichier de configuration

    Args:
        config_file: Chemin vers le fichier de configuration YAML
        articles: Liste des articles à inclure

    Returns:
        True si succès, False sinon
    """
    try:
        config = load_yaml_config(config_file)
        output_file = Path('output') / config['rss']['output_file']
        return generate_rss(articles, config, str(output_file))
    except Exception as e:
        logger.error(f"Failed to generate RSS from config {config_file}: {e}", exc_info=True)
        return False