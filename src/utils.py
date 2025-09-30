"""
Fonctions utilitaires pour le générateur RSS
"""
import yaml
from typing import Dict, Any, Optional, List
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def load_yaml_config(config_path: str) -> Dict[str, Any]:
    """
    Charge un fichier de configuration YAML

    Args:
        config_path: Chemin vers le fichier YAML

    Returns:
        Dictionnaire avec la configuration

    Raises:
        FileNotFoundError: Si le fichier n'existe pas
        yaml.YAMLError: Si le fichier YAML est invalide
    """
    config_file = Path(config_path)

    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return config
    except yaml.YAMLError as e:
        logger.error(f"Error parsing YAML file {config_path}: {e}")
        raise


def make_absolute_url(url: str, base_url: str) -> str:
    """
    Convertit une URL relative en URL absolue

    Args:
        url: URL à convertir (peut être relative ou absolue)
        base_url: URL de base pour la conversion

    Returns:
        URL absolue
    """
    if not url:
        return base_url

    # Déjà une URL absolue
    if url.startswith('http://') or url.startswith('https://'):
        return url

    # URL relative commençant par /
    if url.startswith('/'):
        return base_url.rstrip('/') + url

    # URL relative sans /
    return base_url.rstrip('/') + '/' + url


def get_selector_value(selectors: Dict[str, Any]) -> List[str]:
    """
    Extrait la liste des sélecteurs CSS depuis une configuration

    Args:
        selectors: Configuration de sélecteurs avec 'primary' et 'fallback'

    Returns:
        Liste de sélecteurs CSS à essayer dans l'ordre
    """
    result = []

    # Ajouter le sélecteur principal
    if 'primary' in selectors:
        result.append(selectors['primary'])

    # Ajouter les sélecteurs de secours
    if 'fallback' in selectors and isinstance(selectors['fallback'], list):
        result.extend(selectors['fallback'])

    return result


def setup_logging(level: str = "INFO") -> None:
    """
    Configure le système de logging

    Args:
        level: Niveau de log (DEBUG, INFO, WARNING, ERROR)
    """
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )