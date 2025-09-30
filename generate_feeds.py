#!/usr/bin/env python3
"""
Script principal pour générer les flux RSS de toutes les sources actives
Usage:
    python generate_feeds.py                    # Toutes les sources actives
    python generate_feeds.py --source mistral   # Une source spécifique
    python generate_feeds.py --no-merge         # Sans fusion
    python generate_feeds.py --log-level DEBUG  # Niveau de log personnalisé
"""
import argparse
import sys
from pathlib import Path
from typing import List, Dict

from src import (
    scrape_source,
    generate_rss_from_config,
    merge_from_sources_config,
    load_yaml_config,
    setup_logging
)
import logging

logger = logging.getLogger(__name__)


def parse_arguments():
    """Parse les arguments de ligne de commande"""
    parser = argparse.ArgumentParser(
        description='Génère des flux RSS depuis plusieurs sources configurables',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  %(prog)s                          # Générer tous les flux actifs
  %(prog)s --source mistral         # Générer uniquement Mistral AI
  %(prog)s --no-merge               # Générer sans fusionner
  %(prog)s --log-level DEBUG        # Mode debug détaillé
        """
    )

    parser.add_argument(
        '--source',
        type=str,
        help='Nom de la source spécifique à traiter (ex: mistral, anthropic)'
    )

    parser.add_argument(
        '--no-merge',
        action='store_true',
        help='Désactiver la fusion des flux RSS'
    )

    parser.add_argument(
        '--log-level',
        type=str,
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Niveau de log (défaut: INFO)'
    )

    parser.add_argument(
        '--config',
        type=str,
        default='config/sources.yaml',
        help='Chemin vers le fichier de configuration sources.yaml'
    )

    return parser.parse_args()


def process_source(source_name: str) -> bool:
    """
    Traite une source RSS : scraping + génération du flux

    Args:
        source_name: Nom de la source (ex: 'mistral')

    Returns:
        True si succès, False sinon
    """
    config_file = f"config/{source_name}.yaml"
    config_path = Path(config_file)

    if not config_path.exists():
        logger.error(f"❌ Configuration file not found: {config_file}")
        return False

    try:
        logger.info(f"📥 Processing source: {source_name}")

        # 1. Scraper les articles
        logger.info(f"  🔍 Scraping {source_name}...")
        articles = scrape_source(config_file)

        if not articles:
            logger.warning(f"  ⚠️  No articles found for {source_name}")
            return False

        logger.info(f"  ✓ Found {len(articles)} articles")

        # 2. Générer le flux RSS
        logger.info(f"  📝 Generating RSS feed...")
        success = generate_rss_from_config(config_file, articles)

        if success:
            config = load_yaml_config(config_file)
            output_file = config['rss']['output_file']
            logger.info(f"  ✅ RSS feed generated: output/{output_file}")
            return True
        else:
            logger.error(f"  ❌ Failed to generate RSS feed for {source_name}")
            return False

    except Exception as e:
        logger.error(f"  ❌ Error processing {source_name}: {e}", exc_info=True)
        return False


def main():
    """Fonction principale"""
    args = parse_arguments()

    # Configuration du logging
    setup_logging(args.log_level)

    logger.info("=" * 60)
    logger.info("🚀 RSS Feed Generator - Multi-Sources")
    logger.info("=" * 60)

    # Charger la configuration centrale
    try:
        sources_config = load_yaml_config(args.config)
    except Exception as e:
        logger.error(f"❌ Failed to load sources config: {e}")
        sys.exit(1)

    # Déterminer les sources à traiter
    if args.source:
        # Source spécifique
        sources_to_process = [args.source]
        logger.info(f"📌 Processing single source: {args.source}")
    else:
        # Toutes les sources actives
        sources_to_process = sources_config.get('active_sources', [])
        logger.info(f"📌 Processing {len(sources_to_process)} active sources")

    if not sources_to_process:
        logger.error("❌ No sources to process")
        sys.exit(1)

    # Traiter chaque source
    results: Dict[str, bool] = {}
    successful_count = 0

    for source_name in sources_to_process:
        success = process_source(source_name)
        results[source_name] = success
        if success:
            successful_count += 1

    # Afficher le résumé
    logger.info("")
    logger.info("=" * 60)
    logger.info("📊 Summary")
    logger.info("=" * 60)

    for source_name, success in results.items():
        status = "✅ Success" if success else "❌ Failed"
        logger.info(f"  {source_name}: {status}")

    logger.info(f"\n  Total: {successful_count}/{len(sources_to_process)} successful")

    # Fusion des flux (si activée)
    if not args.no_merge and successful_count > 0:
        merge_config = sources_config.get('merge', {})
        if merge_config.get('enabled', False):
            logger.info("")
            logger.info("=" * 60)
            logger.info("🔀 Merging RSS feeds")
            logger.info("=" * 60)

            try:
                success = merge_from_sources_config(args.config)
                if success:
                    output_file = merge_config.get('output_file', 'merged_feed.xml')
                    logger.info(f"✅ Merged feed generated: output/{output_file}")
                else:
                    logger.error("❌ Failed to merge feeds")
            except Exception as e:
                logger.error(f"❌ Error during merge: {e}", exc_info=True)
        else:
            logger.info("\n⏭️  Merge is disabled in configuration")

    # Code de sortie
    if successful_count == 0:
        logger.error("\n❌ All sources failed")
        sys.exit(1)
    elif successful_count < len(sources_to_process):
        logger.warning(f"\n⚠️  Some sources failed ({len(sources_to_process) - successful_count})")
        sys.exit(0)  # Ne pas échouer si au moins une source a réussi
    else:
        logger.info("\n✅ All feeds generated successfully!")
        sys.exit(0)


if __name__ == "__main__":
    main()