"""
Scraper générique piloté par configuration YAML
Utilise Playwright pour extraire les articles de n'importe quel site web
"""
import asyncio
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from playwright.async_api import async_playwright, Page
from dateutil import parser as date_parser
import logging

from .utils import load_yaml_config, make_absolute_url, get_selector_value

logger = logging.getLogger(__name__)


class GenericScraper:
    """
    Scraper générique configurable via YAML
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialise le scraper avec une configuration

        Args:
            config: Configuration chargée depuis un fichier YAML
        """
        self.config = config
        self.source_config = config['source']
        self.scraping_config = config['scraping']
        self.selectors = self.scraping_config['selectors']

    def parse_date(self, date_text: str) -> datetime:
        """
        Parse une date depuis du texte en essayant plusieurs formats

        Args:
            date_text: Texte contenant la date

        Returns:
            datetime object avec timezone UTC
        """
        if not date_text:
            logger.warning("Empty date text, using current time")
            return datetime.now(timezone.utc)

        date_text = date_text.strip()

        # Essayer d'abord le parser automatique de dateutil
        try:
            parsed_date = date_parser.parse(date_text)
            if parsed_date.tzinfo is None:
                parsed_date = parsed_date.replace(tzinfo=timezone.utc)
            logger.debug(f"dateutil parsed '{date_text}' → {parsed_date.strftime('%Y-%m-%d %H:%M:%S %Z')}")
            return parsed_date
        except Exception as e:
            logger.debug(f"dateutil parser failed for '{date_text}': {e}")

        # Essayer les formats configurés
        date_formats = self.scraping_config.get('date_formats', [])
        for date_format in date_formats:
            try:
                parsed_date = datetime.strptime(date_text, date_format)
                if parsed_date.tzinfo is None:
                    parsed_date = parsed_date.replace(tzinfo=timezone.utc)
                logger.debug(f"Format '{date_format}' parsed '{date_text}' → {parsed_date.strftime('%Y-%m-%d %H:%M:%S %Z')}")
                return parsed_date
            except ValueError:
                continue

        # Fallback selon la configuration
        fallback = self.scraping_config.get('fallback', 'now')
        if fallback == 'now':
            logger.warning(f"Failed to parse date '{date_text}', using current time")
            return datetime.now(timezone.utc)

        logger.error(f"Failed to parse date '{date_text}' and no valid fallback")
        return datetime.now(timezone.utc)

    async def try_selectors(self, element: Any, selectors_config: Dict[str, Any]) -> Optional[str]:
        """
        Essaie plusieurs sélecteurs CSS jusqu'à trouver un élément

        Args:
            element: Élément Playwright dans lequel chercher
            selectors_config: Configuration des sélecteurs (primary, fallback, attribute, optional)

        Returns:
            Texte ou attribut trouvé, ou None si rien trouvé et optional=True
        """
        selectors = get_selector_value(selectors_config)
        attribute = selectors_config.get('attribute')
        optional = selectors_config.get('optional', False)

        for selector in selectors:
            try:
                # Cas spécial : sélecteur vide ou "." signifie l'élément lui-même
                if selector == "" or selector == ".":
                    if attribute:
                        value = await element.get_attribute(attribute)
                    else:
                        value = await element.text_content()

                    if value:
                        return value.strip()
                    continue

                found_element = await element.query_selector(selector)
                if found_element:
                    if attribute:
                        value = await found_element.get_attribute(attribute)
                    else:
                        value = await found_element.text_content()

                    if value:
                        return value.strip()
            except Exception as e:
                logger.debug(f"Selector '{selector}' failed: {e}")
                continue

        if not optional:
            logger.warning(f"No element found for selectors: {selectors}")

        return None

    async def scrape_article(self, article_element: Any) -> Optional[Dict[str, Any]]:
        """
        Extrait les données d'un seul article

        Args:
            article_element: Élément Playwright représentant un article

        Returns:
            Dictionnaire avec les données de l'article ou None si erreur
        """
        try:
            # Extraire le titre
            title = await self.try_selectors(article_element, self.selectors['title'])
            if not title:
                logger.warning("Article without title, skipping")
                return None

            # Extraire le lien
            link = await self.try_selectors(article_element, self.selectors['link'])
            if not link:
                logger.warning(f"Article '{title}' without link, skipping")
                return None

            # Convertir en URL absolue si nécessaire
            url_handling = self.scraping_config.get('url_handling', {})
            if url_handling.get('make_absolute', True):
                base_url = url_handling.get('base_url', self.source_config['url'])
                link = make_absolute_url(link, base_url)

            # Extraire la date
            date_text = await self.try_selectors(article_element, self.selectors['date'])
            parsed_date = self.parse_date(date_text) if date_text else datetime.now(timezone.utc)

            # Extraire la description (optionnel)
            description = None
            if 'description' in self.selectors:
                description = await self.try_selectors(article_element, self.selectors['description'])

            article_data = {
                'title': title,
                'link': link,
                'date': parsed_date,
                'date_text': date_text or '',
                'description': description or title,  # Fallback au titre si pas de description
                'source': self.source_config['name']
            }

            logger.info(f"Found: {title} - {date_text} → parsed as {parsed_date.strftime('%Y-%m-%d')}")
            return article_data

        except Exception as e:
            logger.error(f"Error scraping article: {e}", exc_info=True)
            return None

    async def scrape(self) -> List[Dict[str, Any]]:
        """
        Lance le scraping complet du site

        Returns:
            Liste de dictionnaires contenant les articles
        """
        articles_data = []

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            try:
                # Charger la page
                url = self.source_config['url']
                logger.info(f"Loading page: {url}")
                await page.goto(url)

                # Attendre selon la stratégie configurée
                wait_strategy = self.scraping_config.get('wait_strategy', 'networkidle')
                wait_time = self.scraping_config.get('wait_time', 3000)

                if wait_strategy == 'networkidle':
                    await page.wait_for_load_state('networkidle', timeout=wait_time)
                elif wait_strategy == 'load':
                    await page.wait_for_load_state('load', timeout=wait_time)
                elif wait_strategy == 'domcontentloaded':
                    await page.wait_for_load_state('domcontentloaded', timeout=wait_time)

                # Attendre aussi le container principal
                container_selector = self.selectors['container']
                logger.info(f"Waiting for container: {container_selector}")
                await page.wait_for_selector(container_selector, timeout=wait_time)

                # Récupérer tous les articles
                articles = await page.query_selector_all(container_selector)
                logger.info(f"Found {len(articles)} article containers")

                # Scraper chaque article
                for article in articles:
                    article_data = await self.scrape_article(article)
                    if article_data:
                        articles_data.append(article_data)

                # Trier par date (plus récent en premier)
                articles_data.sort(key=lambda x: x['date'], reverse=True)

                logger.info(f"Successfully scraped {len(articles_data)} articles from {self.source_config['name']}")

            except Exception as e:
                logger.error(f"Error during scraping: {e}", exc_info=True)
            finally:
                await browser.close()

        return articles_data


def scrape_source(config_file: str) -> List[Dict[str, Any]]:
    """
    Fonction principale pour scraper une source depuis un fichier de config

    Args:
        config_file: Chemin vers le fichier de configuration YAML

    Returns:
        Liste d'articles scrapés
    """
    try:
        config = load_yaml_config(config_file)
        scraper = GenericScraper(config)
        articles = asyncio.run(scraper.scrape())
        return articles
    except Exception as e:
        logger.error(f"Failed to scrape source {config_file}: {e}", exc_info=True)
        return []