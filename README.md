# 🚀 Générateur RSS Universel Multi-Sources

Un système de génération de flux RSS **générique et configurable** qui s'adapte à n'importe quel site web sans modification de code. Ajoutez de nouvelles sources simplement en créant un fichier de configuration YAML !

[![Generate RSS Feeds](https://github.com/YOUR_USERNAME/rss-feed/actions/workflows/generate_feeds.yml/badge.svg)](https://github.com/YOUR_USERNAME/rss-feed/actions/workflows/generate_feeds.yml)

## ✨ Fonctionnalités Clés

- **🔧 Configuration par fichier YAML** : Aucun code à modifier pour ajouter une source
- **🌐 Scraping universel** : S'adapte à n'importe quelle structure HTML via sélecteurs CSS
- **🔀 Fusion multi-sources** : Combine plusieurs flux RSS en un seul flux unifié
- **⚙️ Automatisation GitHub Actions** : Mise à jour automatique toutes les heures
- **🛡️ Robustesse maximale** : Continue de fonctionner même si certaines sources échouent
- **📊 Fallbacks intelligents** : Sélecteurs CSS multiples avec système de secours

## 📋 Table des Matières

- [Sources Disponibles](#-sources-disponibles)
- [Installation Rapide](#-installation-rapide)
- [Utilisation](#-utilisation)
- [Architecture](#-architecture)
- [Ajouter une Nouvelle Source](#-ajouter-une-nouvelle-source)
- [Configuration GitHub Actions](#-configuration-github-actions)
- [Personnalisation](#-personnalisation)
- [Dépannage](#-dépannage)

## 🎯 Sources Disponibles

| Source | Description | Articles | Flux RSS |
|--------|-------------|----------|----------|
| **Mistral AI** | News, recherche et releases | ~10 | [mistral_rss.xml](output/mistral_rss.xml) |
| **Anthropic Engineering** | Blog technique et ingénierie | ~10 | [anthropic_rss.xml](output/anthropic_rss.xml) |
| **Anthropic News** | Actualités et annonces officielles | ~50 | [anthropic_news_rss.xml](output/anthropic_news_rss.xml) |
| **🔀 Flux Fusionné** | Tous les flux combinés | ~70 | [merged_feed.xml](output/merged_feed.xml) |

### URLs des Flux (GitHub Raw)

```
# Sources individuelles
https://raw.githubusercontent.com/YOUR_USERNAME/rss-feed/main/output/mistral_rss.xml
https://raw.githubusercontent.com/YOUR_USERNAME/rss-feed/main/output/anthropic_rss.xml
https://raw.githubusercontent.com/YOUR_USERNAME/rss-feed/main/output/anthropic_news_rss.xml

# Flux fusionné (recommandé)
https://raw.githubusercontent.com/YOUR_USERNAME/rss-feed/main/output/merged_feed.xml
```

> **Note** : Remplacez `YOUR_USERNAME` par votre nom d'utilisateur GitHub
>
> **Astuce** : Le flux fusionné combine tous les articles et les trie par date de publication

## 🚀 Installation Rapide

### 1. Forker le Projet

Cliquez sur le bouton "Fork" en haut à droite de cette page.

### 2. Cloner Votre Fork

```bash
git clone https://github.com/YOUR_USERNAME/rss-feed.git
cd rss-feed
```

### 3. Installer les Dépendances

```bash
# Créer un environnement virtuel (optionnel mais recommandé)
python -m venv .venv
source .venv/bin/activate  # Sur Windows: .venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Installer le navigateur Playwright
playwright install chromium
```

### 4. Tester Localement

```bash
# Générer tous les flux actifs
python generate_feeds.py

# Vérifier les flux générés
ls output/
```

### 5. Configurer GitHub Actions

1. Allez dans **Settings** → **Actions** → **General**
2. Sous "Workflow permissions", sélectionnez **Read and write permissions**
3. Cliquez sur **Save**

Les flux se mettront à jour automatiquement toutes les heures !

## 📖 Utilisation

### Lecture des Flux RSS

#### Dans un Lecteur RSS

Ajoutez simplement l'URL du flux dans votre lecteur RSS favori :
- [Feedly](https://feedly.com/)
- [Inoreader](https://www.inoreader.com/)
- [NewsBlur](https://newsblur.com/)
- [Thunderbird](https://www.thunderbird.net/)

#### En Ligne de Commande

```bash
# Toutes les sources actives
python generate_feeds.py

# Une source spécifique
python generate_feeds.py --source mistral

# Sans fusion des flux
python generate_feeds.py --no-merge

# Mode debug
python generate_feeds.py --log-level DEBUG
```

### Valider une Configuration

```bash
# Valider un fichier de config
python validate_config.py config/mistral.yaml

# Valider toutes les configs
python validate_config.py config/*.yaml
```

## 🏗️ Architecture

```
rss-feed/
├── config/                      # Configurations YAML des sources
│   ├── sources.yaml             # Liste des sources actives + config fusion
│   ├── mistral.yaml             # Config Mistral AI (actif)
│   ├── anthropic.yaml           # Config Anthropic Engineering (actif)
│   ├── anthropic_news.yaml      # Config Anthropic News (actif)
│   ├── openai.yaml              # Exemple OpenAI (désactivé)
│   └── huggingface.yaml         # Exemple Hugging Face (désactivé)
│
├── src/                         # Code source du générateur
│   ├── __init__.py              # Module principal
│   ├── scraper.py               # Scraper générique piloté par config
│   ├── rss_generator.py         # Générateur de flux RSS
│   ├── merger.py                # Fusionneur de flux multiples
│   └── utils.py                 # Fonctions utilitaires
│
├── output/                      # Flux RSS générés
│   ├── mistral_rss.xml          # ~10 articles Mistral AI
│   ├── anthropic_rss.xml        # ~10 articles Engineering
│   ├── anthropic_news_rss.xml   # ~50 articles News
│   └── merged_feed.xml          # ~70 articles combinés
│
├── .github/workflows/
│   └── generate_feeds.yml   # Automatisation GitHub Actions
│
├── generate_feeds.py        # Script principal
├── validate_config.py       # Validation des configurations
├── requirements.txt         # Dépendances Python
└── README.md
```

### Principe : Configuration over Code

**Un utilisateur ne doit JAMAIS modifier le code Python pour ajouter une source.**

Tout passe par les fichiers YAML :
1. Créer un fichier `config/nouvelle_source.yaml`
2. L'ajouter dans `config/sources.yaml`
3. C'est tout ! Le système s'adapte automatiquement.

## ➕ Ajouter une Nouvelle Source

Consultez le guide détaillé : **[HOW_TO_ADD_SOURCE.md](HOW_TO_ADD_SOURCE.md)**

### Processus Rapide

1. **Analyser le site** : Inspecter la structure HTML
2. **Créer la config** : Copier le template et adapter les sélecteurs CSS
3. **Tester** : Valider avec `validate_config.py`
4. **Activer** : Ajouter dans `sources.yaml`
5. **Générer** : Lancer `generate_feeds.py`

### Exemple Minimal

```yaml
# config/example.yaml
source:
  name: "Example"
  url: "https://example.com/blog"
  description: "Example blog posts"

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
      attribute: "href"
    date:
      primary: "time"
      attribute: "datetime"

  url_handling:
    make_absolute: true
    base_url: "https://example.com"

rss:
  output_file: "example_rss.xml"
  title: "Example Blog"
  link: "https://example.com/blog"
```

## ⚙️ Configuration GitHub Actions

### Permissions Requises

1. Allez dans **Settings** → **Actions** → **General**
2. Sous "Workflow permissions" :
   - ✅ **Read and write permissions**
3. Cliquez sur **Save**

### Fréquence de Mise à Jour

Par défaut, les flux se mettent à jour **toutes les heures**.

Pour changer la fréquence, éditez `.github/workflows/generate_feeds.yml` :

```yaml
on:
  schedule:
    # Toutes les 6 heures
    - cron: '0 */6 * * *'

    # Deux fois par jour (6h et 18h UTC)
    - cron: '0 6,18 * * *'

    # Une fois par jour à 9h UTC
    - cron: '0 9 * * *'
```

### Déclenchement Manuel

1. Allez dans l'onglet **Actions**
2. Sélectionnez "Generate RSS Feeds"
3. Cliquez sur **Run workflow**

## 🎨 Personnalisation

### Nombre Maximum d'Articles

Dans `config/sources.yaml` :

```yaml
merge:
  max_items: 50  # Limite du flux fusionné

# Dans chaque source (ex: config/mistral.yaml)
rss:
  max_items: 50  # Limite de la source
```

### Préfixe de Source

Activer/désactiver `[Source]` devant les titres :

```yaml
merge:
  add_source_prefix: true  # [Mistral AI] Article Title
```

### Formats de Date

Ajouter des formats de date personnalisés :

```yaml
scraping:
  date_formats:
    - "%d/%m/%Y"           # 26/02/2025
    - "%Y-%m-%d %H:%M:%S"  # 2025-02-26 14:30:00
```

## 🔧 Dépannage

### Problème : Aucun article trouvé

**Cause** : Les sélecteurs CSS ne correspondent pas à la structure du site.

**Solution** :
1. Inspecter le site avec les DevTools du navigateur (F12)
2. Vérifier les sélecteurs dans la console : `document.querySelectorAll("votre-selecteur")`
3. Ajuster les sélecteurs dans le fichier YAML
4. Tester avec `python generate_feeds.py --source nom_source --log-level DEBUG`

### Problème : Erreur de parsing de date

**Cause** : Le format de date n'est pas reconnu.

**Solution** :
1. Identifier le format exact de la date sur le site
2. Ajouter le format dans `scraping.date_formats`
3. Référence des formats : [strftime.org](https://strftime.org/)

### Problème : GitHub Actions échoue

**Causes possibles** :
- Permissions insuffisantes → Vérifier "Read and write permissions"
- Quota GitHub Actions dépassé → Réduire la fréquence du cron
- Site source inaccessible → Vérifier manuellement l'accès au site

**Solution** :
1. Consulter les logs dans l'onglet **Actions**
2. Tester localement : `python generate_feeds.py --log-level DEBUG`
3. Vérifier les permissions dans **Settings** → **Actions**

### Problème : URLs relatives non converties

**Cause** : `make_absolute: false` ou `base_url` incorrect.

**Solution** :

```yaml
scraping:
  url_handling:
    make_absolute: true
    base_url: "https://example.com"  # URL complète du site
```

### Problème : Flux XML invalide

**Cause** : Caractères spéciaux non échappés.

**Solution** :
Le générateur échappe automatiquement les caractères. Si le problème persiste :
1. Valider le XML : [validator.w3.org/feed](https://validator.w3.org/feed/)
2. Vérifier les logs pour identifier la source du problème

## 📚 Documentation Complète

- **[HOW_TO_ADD_SOURCE.md](HOW_TO_ADD_SOURCE.md)** : Guide détaillé pour ajouter une source
- **[CONFIGURATION.md](CONFIGURATION.md)** : Documentation de référence des configurations
- **Code source** : Tous les fichiers Python sont commentés et documentés

## 🤝 Contribuer

Les contributions sont les bienvenues !

1. Forkez le projet
2. Créez une branche pour votre fonctionnalité (`git checkout -b feature/amazing-feature`)
3. Committez vos changements (`git commit -m 'Add amazing feature'`)
4. Poussez vers la branche (`git push origin feature/amazing-feature`)
5. Ouvrez une Pull Request

### Exemples de Configurations

Si vous créez une configuration pour une nouvelle source populaire (ex: Google AI, Hugging Face), n'hésitez pas à la partager via une PR !

## 📄 Licence

Ce projet est sous licence MIT. Voir [LICENSE](LICENSE) pour plus de détails.

## 🙏 Remerciements

- [Playwright](https://playwright.dev/) pour le scraping web robuste
- [feedgen](https://github.com/lkiesow/python-feedgen) pour la génération de flux RSS
- Inspiré du projet [anthropic-engineering-rss-feed](https://github.com/conoro/anthropic-engineering-rss-feed) de Conor O'Neill

---

**🌟 Si ce projet vous est utile, n'hésitez pas à lui donner une étoile !**