# 📖 Documentation de Référence : Configuration

Documentation complète de tous les champs et options disponibles dans les fichiers de configuration YAML.

## 📂 Structure des Fichiers

Le système utilise deux types de fichiers de configuration :

1. **`config/sources.yaml`** : Configuration centrale (sources actives + fusion)
2. **`config/SOURCE.yaml`** : Configuration individuelle de chaque source

## 🎯 config/sources.yaml

Fichier central qui contrôle quelles sources sont actives et la configuration de la fusion.

### Structure Complète

```yaml
active_sources:
  - source1
  - source2

merge:
  enabled: true
  output_file: "merged_feed.xml"
  title: "Titre du flux fusionné"
  description: "Description du flux"
  link: "https://github.com/USER/rss-feed"
  language: "en"
  max_items: 100
  add_source_prefix: true
  sort_by_date: true
```

### Champs : `active_sources`

**Type** : Liste de chaînes de caractères
**Requis** : Oui
**Description** : Liste des noms de sources à traiter

```yaml
active_sources:
  - mistral       # Fichier config/mistral.yaml
  - anthropic     # Fichier config/anthropic.yaml
  # - openai      # Désactivé (commenté)
```

**Notes** :
- Les noms doivent correspondre aux fichiers `config/{nom}.yaml`
- Commentez une ligne pour désactiver temporairement une source
- L'ordre n'a pas d'importance (les articles sont triés par date dans le flux fusionné)

### Section : `merge`

Configuration du flux RSS fusionné qui combine toutes les sources actives.

#### `merge.enabled`

**Type** : Booléen
**Requis** : Non
**Défaut** : `false`
**Description** : Active ou désactive la génération du flux fusionné

```yaml
merge:
  enabled: true  # Génère merged_feed.xml
```

#### `merge.output_file`

**Type** : Chaîne de caractères
**Requis** : Non
**Défaut** : `"merged_feed.xml"`
**Description** : Nom du fichier XML fusionné (dans `output/`)

```yaml
merge:
  output_file: "all_sources.xml"
```

#### `merge.title`

**Type** : Chaîne de caractères
**Requis** : Non
**Défaut** : `"Merged RSS Feed"`
**Description** : Titre du flux RSS fusionné

```yaml
merge:
  title: "AI News - Multi-Sources"
```

#### `merge.description`

**Type** : Chaîne de caractères
**Requis** : Non
**Défaut** : `"Combined RSS feeds"`
**Description** : Description du flux

```yaml
merge:
  description: "Actualités fusionnées de plusieurs entreprises IA"
```

#### `merge.link`

**Type** : URL
**Requis** : Non
**Défaut** : `""`
**Description** : Lien vers le site web du flux

```yaml
merge:
  link: "https://github.com/USER/rss-feed"
```

#### `merge.language`

**Type** : Code langue ISO 639-1
**Requis** : Non
**Défaut** : `"en"`
**Description** : Langue du flux (en, fr, es, etc.)

```yaml
merge:
  language: "fr"
```

#### `merge.max_items`

**Type** : Entier
**Requis** : Non
**Défaut** : `100`
**Description** : Nombre maximum d'articles dans le flux fusionné

```yaml
merge:
  max_items: 50  # Limite à 50 articles les plus récents
```

#### `merge.add_source_prefix`

**Type** : Booléen
**Requis** : Non
**Défaut** : `true`
**Description** : Ajoute `[Source]` devant les titres

```yaml
merge:
  add_source_prefix: true

# Résultat :
# [Mistral AI] New Model Release
# [Anthropic] Engineering Update
```

#### `merge.sort_by_date`

**Type** : Booléen
**Requis** : Non
**Défaut** : `true`
**Description** : Trie les articles par date (plus récent en premier)

```yaml
merge:
  sort_by_date: true  # Articles chronologiques
```

## 🔧 config/SOURCE.yaml

Configuration individuelle de chaque source RSS.

### Structure Complète

```yaml
source:
  name: "Nom de la Source"
  url: "https://example.com/blog"
  description: "Description"
  language: "en"

scraping:
  wait_time: 3000
  wait_strategy: "networkidle"

  selectors:
    container: "article"
    title:
      primary: "h2"
      fallback: ["h3", "h1"]
    link:
      primary: "a"
      fallback: ["[href]"]
      attribute: "href"
    date:
      primary: "time"
      fallback: ["[class*='date']"]
      attribute: "datetime"
    description:
      primary: "p"
      fallback: [".excerpt"]
      optional: true

  url_handling:
    make_absolute: true
    base_url: "https://example.com"

  date_formats:
    - "%B %d, %Y"
    - "%Y-%m-%d"
  fallback: "now"

rss:
  output_file: "source_rss.xml"
  title: "Titre du Flux"
  link: "https://example.com/blog"
  description: "Description du flux"
  language: "en"
  max_items: 50
```

## Section : `source`

Métadonnées de la source.

### `source.name`

**Type** : Chaîne de caractères
**Requis** : Oui
**Description** : Nom affiché de la source

```yaml
source:
  name: "Mistral AI"
```

### `source.url`

**Type** : URL
**Requis** : Oui
**Description** : URL de la page à scraper

```yaml
source:
  url: "https://mistral.ai/news"
```

### `source.description`

**Type** : Chaîne de caractères
**Requis** : Oui
**Description** : Description de la source

```yaml
source:
  description: "Latest news and research from Mistral AI"
```

### `source.language`

**Type** : Code langue ISO 639-1
**Requis** : Non
**Défaut** : `"en"`
**Description** : Langue du contenu

```yaml
source:
  language: "fr"
```

## Section : `scraping`

Configuration du comportement de scraping.

### `scraping.wait_time`

**Type** : Entier (millisecondes)
**Requis** : Non
**Défaut** : `3000`
**Description** : Temps d'attente maximum pour le chargement

```yaml
scraping:
  wait_time: 5000  # 5 secondes pour sites lents
```

### `scraping.wait_strategy`

**Type** : Enum
**Requis** : Non
**Défaut** : `"networkidle"`
**Description** : Stratégie d'attente Playwright

**Valeurs possibles** :
- `"networkidle"` : Attend que le réseau soit inactif (recommandé)
- `"load"` : Attend l'événement `load`
- `"domcontentloaded"` : Attend l'événement `DOMContentLoaded`

```yaml
scraping:
  wait_strategy: "networkidle"  # Pour sites avec JS
```

**Quand utiliser quoi** :
- **`networkidle`** : Sites modernes avec chargement JavaScript
- **`load`** : Sites statiques ou légers
- **`domcontentloaded`** : Maximum de vitesse, contenu peut être incomplet

## Sous-section : `scraping.selectors`

Sélecteurs CSS pour extraire les données.

### `selectors.container`

**Type** : Chaîne de caractères (sélecteur CSS)
**Requis** : Oui
**Description** : Sélecteur identifiant chaque article

```yaml
selectors:
  # Simple
  container: "article"

  # Avec classe
  container: ".blog-post"

  # Wildcard pour classes dynamiques
  container: "[class*='ArticleCard']"

  # Plusieurs options (essaie dans l'ordre)
  container: "article, .post, [class*='card']"
```

### Format de Sélecteur Standard

Chaque sélecteur (sauf `container`) utilise ce format :

```yaml
element_name:
  primary: "selector"        # Sélecteur principal
  fallback: ["sel1", "sel2"] # Sélecteurs de secours
  attribute: "attr"          # Attribut à extraire (ou null)
  optional: true             # Autoriser l'absence (défaut: false)
```

### `selectors.title`

**Type** : Objet de sélecteur
**Requis** : Oui
**Description** : Extrait le titre de l'article

```yaml
title:
  primary: "h2"
  fallback: ["h3", "h1", "[class*='title']"]
  # attribute: null (implicite - extrait le texte)
```

### `selectors.link`

**Type** : Objet de sélecteur
**Requis** : Oui
**Description** : Extrait l'URL de l'article

```yaml
link:
  primary: "a"
  fallback: ["[href]"]
  attribute: "href"  # Toujours "href" pour les liens
```

### `selectors.date`

**Type** : Objet de sélecteur
**Requis** : Oui
**Description** : Extrait la date de publication

```yaml
# Avec attribut datetime
date:
  primary: "time"
  fallback: ["[datetime]"]
  attribute: "datetime"

# Sans attribut (texte brut)
date:
  primary: ".date"
  fallback: ["time", "span"]
  attribute: null  # Extrait le texte
```

### `selectors.description`

**Type** : Objet de sélecteur
**Requis** : Non
**Description** : Extrait la description/extrait de l'article

```yaml
description:
  primary: "p"
  fallback: [".excerpt", ".summary"]
  optional: true  # Ne pas échouer si absent
```

**Note** : Si absent ou `optional: true` et non trouvé, le titre sera utilisé comme description.

### Attribut `attribute`

**Type** : Chaîne de caractères ou `null`
**Description** : Détermine ce qui est extrait

```yaml
# Extraire un attribut HTML
link:
  primary: "a"
  attribute: "href"  # Extrait <a href="...">

# Extraire le texte
title:
  primary: "h2"
  attribute: null  # Ou omis - Extrait le texte
```

### Attribut `optional`

**Type** : Booléen
**Défaut** : `false`
**Description** : Autorise l'absence de l'élément

```yaml
description:
  primary: "p"
  optional: true  # Continue si pas trouvé
```

**Quand utiliser** :
- ✅ Pour `description` (souvent absent)
- ❌ Jamais pour `title`, `link`, `date` (requis)

## Sous-section : `scraping.url_handling`

Configuration de la gestion des URLs.

### `url_handling.make_absolute`

**Type** : Booléen
**Requis** : Non
**Défaut** : `true`
**Description** : Convertit les URLs relatives en absolues

```yaml
url_handling:
  make_absolute: true
  base_url: "https://example.com"

# /blog/article → https://example.com/blog/article
```

### `url_handling.base_url`

**Type** : URL
**Requis** : Si `make_absolute: true`
**Description** : URL de base pour les URLs relatives

```yaml
url_handling:
  base_url: "https://example.com"
```

**Note** : Si omis, utilise `source.url` par défaut.

## Sous-section : `scraping.date_formats`

Liste des formats de dates à essayer pour le parsing.

### `date_formats`

**Type** : Liste de chaînes de caractères
**Requis** : Non
**Défaut** : Parsing automatique avec dateutil
**Description** : Formats de dates à essayer dans l'ordre

```yaml
date_formats:
  - "%B %d, %Y"          # February 26, 2025
  - "%Y-%m-%d"           # 2025-02-26
  - "%d/%m/%Y"           # 26/02/2025
  - "%b %d, %Y"          # Feb 26, 2025
  - "%Y-%m-%dT%H:%M:%S"  # 2025-02-26T14:30:00
```

**Références** :
- [strftime.org](https://strftime.org/) : Cheat sheet des formats
- [Python strftime](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes)

**Codes Fréquents** :

| Code | Signification | Exemple |
|------|--------------|---------|
| `%Y` | Année (4 chiffres) | 2025 |
| `%y` | Année (2 chiffres) | 25 |
| `%m` | Mois (2 chiffres) | 02 |
| `%B` | Mois (nom complet) | February |
| `%b` | Mois (nom abrégé) | Feb |
| `%d` | Jour (2 chiffres) | 26 |
| `%H` | Heure (24h) | 14 |
| `%M` | Minutes | 30 |
| `%S` | Secondes | 00 |
| `%z` | Timezone | +0100 |

### `fallback`

**Type** : Chaîne de caractères
**Requis** : Non
**Défaut** : `"now"`
**Description** : Comportement si tous les formats échouent

```yaml
scraping:
  date_formats:
    - "%B %d, %Y"
  fallback: "now"  # Utilise la date/heure actuelle
```

**Valeurs possibles** :
- `"now"` : Date/heure actuelle (recommandé)

## Section : `rss`

Configuration du flux RSS généré.

### `rss.output_file`

**Type** : Chaîne de caractères
**Requis** : Oui
**Description** : Nom du fichier XML généré (dans `output/`)

```yaml
rss:
  output_file: "mistral_rss.xml"
  # Génère output/mistral_rss.xml
```

### `rss.title`

**Type** : Chaîne de caractères
**Requis** : Oui
**Description** : Titre du flux RSS

```yaml
rss:
  title: "Mistral AI - News & Updates"
```

### `rss.link`

**Type** : URL
**Requis** : Oui
**Description** : Lien vers le site source

```yaml
rss:
  link: "https://mistral.ai/news"
```

### `rss.description`

**Type** : Chaîne de caractères
**Requis** : Non
**Défaut** : Utilise `source.description`
**Description** : Description du flux RSS

```yaml
rss:
  description: "Latest news from Mistral AI"
```

### `rss.language`

**Type** : Code langue ISO 639-1
**Requis** : Non
**Défaut** : Utilise `source.language`
**Description** : Langue du flux

```yaml
rss:
  language: "en"
```

### `rss.max_items`

**Type** : Entier
**Requis** : Non
**Défaut** : `50`
**Description** : Nombre maximum d'articles dans le flux

```yaml
rss:
  max_items: 30  # Limite à 30 articles
```

## 🎨 Exemples Pratiques

### Configuration Simple

Pour un blog WordPress classique :

```yaml
source:
  name: "Mon Blog"
  url: "https://monblog.com"
  description: "Mes articles"

scraping:
  selectors:
    container: "article.post"
    title:
      primary: "h2.entry-title"
    link:
      primary: "a"
      attribute: "href"
    date:
      primary: "time"
      attribute: "datetime"

rss:
  output_file: "monblog_rss.xml"
  title: "Mon Blog"
  link: "https://monblog.com"
```

### Configuration Avancée

Pour un site avec JavaScript et classes dynamiques :

```yaml
source:
  name: "Site Moderne"
  url: "https://example.com/blog"
  description: "Articles techniques"
  language: "fr"

scraping:
  wait_time: 5000
  wait_strategy: "networkidle"

  selectors:
    container: "[class*='ArticleCard'], article, .post"

    title:
      primary: "[class*='ArticleCard_title']"
      fallback: ["h2", "h3", "[class*='title']"]

    link:
      primary: "a[class*='ArticleCard_link']"
      fallback: ["a"]
      attribute: "href"

    date:
      primary: "[class*='ArticleCard_date']"
      fallback: ["time", "[datetime]"]
      attribute: "datetime"

    description:
      primary: "[class*='ArticleCard_excerpt']"
      fallback: ["p", ".excerpt"]
      optional: true

  url_handling:
    make_absolute: true
    base_url: "https://example.com"

  date_formats:
    - "%d/%m/%Y"
    - "%d %B %Y"
    - "%Y-%m-%d"
  fallback: "now"

rss:
  output_file: "moderne_rss.xml"
  title: "Site Moderne - Articles"
  link: "https://example.com/blog"
  description: "Derniers articles techniques"
  language: "fr"
  max_items: 30
```

## ✅ Validation

Utilisez le script de validation pour vérifier vos configurations :

```bash
python validate_config.py config/votre_source.yaml
```

Le validateur vérifie :
- ✓ Syntaxe YAML correcte
- ✓ Présence des champs requis
- ✓ Format des URLs
- ✓ Syntaxe de base des sélecteurs CSS

## 📚 Ressources

- [CSS Selectors Reference](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Selectors)
- [Playwright Documentation](https://playwright.dev/python/)
- [strftime Format Codes](https://strftime.org/)
- [RSS 2.0 Specification](https://www.rssboard.org/rss-specification)

---

**Besoin d'aide ?** Consultez [HOW_TO_ADD_SOURCE.md](HOW_TO_ADD_SOURCE.md) pour un guide pas-à-pas.