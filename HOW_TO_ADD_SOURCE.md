# 📘 Guide : Ajouter une Nouvelle Source RSS

Ce guide vous explique **pas-à-pas** comment ajouter une nouvelle source de flux RSS au générateur. Suivez ces étapes et vous pourrez ajouter n'importe quel site web en moins de 10 minutes !

## 🎯 Vue d'Ensemble

Pour ajouter une source, vous devez :
1. Analyser la structure HTML du site cible
2. Créer un fichier de configuration YAML
3. Tester les sélecteurs CSS
4. Activer la source dans `sources.yaml`
5. Vérifier que tout fonctionne

**Aucune modification de code Python n'est nécessaire !**

## 📋 Étape 1 : Analyser le Site Cible

### 1.1 Ouvrir le Site avec les DevTools

1. Ouvrez le site web dans votre navigateur (Chrome, Firefox, Edge...)
2. Appuyez sur **F12** pour ouvrir les DevTools
3. Cliquez sur l'onglet **Elements** (ou **Inspecteur**)

### 1.2 Identifier les Éléments à Scraper

Vous devez trouver les **sélecteurs CSS** pour :

| Élément | Description | Exemple |
|---------|-------------|---------|
| **Container** | L'élément qui englobe chaque article | `article`, `.blog-post`, `[class*='card']` |
| **Titre** | Le titre de l'article | `h2`, `h3`, `.title` |
| **Lien** | L'URL de l'article | `a`, `[href]` |
| **Date** | La date de publication | `time`, `.date`, `[datetime]` |
| **Description** (optionnel) | Résumé/extrait de l'article | `p`, `.excerpt` |

### 1.3 Tester les Sélecteurs dans la Console

Ouvrez la console du navigateur (onglet **Console** dans DevTools) et testez vos sélecteurs :

```javascript
// Tester le container
document.querySelectorAll("article")

// Tester le titre (dans le premier container)
document.querySelector("article h2")

// Tester le lien
document.querySelector("article a").href

// Tester la date
document.querySelector("article time").textContent
```

**Conseils** :
- Si un sélecteur ne fonctionne pas, essayez des alternatives
- Les classes CSS générées dynamiquement (ex: `ArticleList_item__abc123`) peuvent changer → utilisez `[class*='ArticleList_item']`
- Préférez les sélecteurs structurels (`article`, `time`) aux classes spécifiques

### 1.4 Exemple Pratique : Mistral AI

Analysons https://mistral.ai/news :

```html
<article>
  <h2>Mistral AI announces new model</h2>
  <a href="/news/article-slug">Read more</a>
  <time datetime="2025-02-26">February 26, 2025</time>
  <p>Description of the article...</p>
</article>
```

Sélecteurs identifiés :
- Container : `article`
- Titre : `h2`
- Lien : `a`
- Date : `time` avec attribut `datetime`
- Description : `p`

## 📝 Étape 2 : Créer le Fichier de Configuration

### 2.1 Créer le Fichier YAML

Créez un nouveau fichier dans `config/` avec le nom de votre source :

```bash
touch config/ma_source.yaml
```

### 2.2 Template Complet

Copiez ce template et adaptez-le :

```yaml
# Configuration du scraper pour [Nom de la Source]

source:
  name: "Nom de la Source"
  url: "https://example.com/blog"
  description: "Description de la source"
  language: "en"  # ou "fr"

scraping:
  # Temps d'attente pour le chargement JavaScript (millisecondes)
  wait_time: 3000

  # Stratégie d'attente Playwright
  # Options: "networkidle", "load", "domcontentloaded"
  wait_strategy: "networkidle"

  selectors:
    # Container : élément qui englobe chaque article
    container: "article, .post, [class*='blog-item']"

    title:
      # Sélecteur principal pour le titre
      primary: "h2"
      # Sélecteurs de secours si le principal échoue
      fallback: ["h3", "h1", "[class*='title']"]

    link:
      # Sélecteur pour trouver le lien de l'article
      primary: "a"
      fallback: ["[href]"]
      # Attribut à extraire : "href" pour les liens
      attribute: "href"

    date:
      # Sélecteur pour la date de publication
      primary: "time"
      fallback: ["[class*='date']", "[datetime]", "span"]
      # Attribut datetime si disponible, sinon null pour le texte
      attribute: "datetime"  # ou null

    description:
      # Description/extrait de l'article (optionnel)
      primary: "p"
      fallback: ["[class*='description']", "[class*='excerpt']"]
      optional: true  # Ne pas échouer si absent

  # Gestion des URLs
  url_handling:
    make_absolute: true           # Convertir les URLs relatives en absolues
    base_url: "https://example.com"

  # Formats de dates supportés (ordre de tentative)
  date_formats:
    - "%B %d, %Y"                 # "February 26, 2025"
    - "%Y-%m-%d"                  # "2025-02-26"
    - "%d/%m/%Y"                  # "26/02/2025"
    - "%b %d, %Y"                 # "Feb 26, 2025"
    - "%Y-%m-%dT%H:%M:%S%z"      # ISO format avec timezone
  fallback: "now"                 # Utiliser date actuelle si parsing échoue

# Configuration du flux RSS généré
rss:
  output_file: "ma_source_rss.xml"
  title: "Nom de la Source - Flux RSS"
  link: "https://example.com/blog"
  description: "Description du flux RSS"
  language: "en"  # ou "fr"
  max_items: 50   # Limite d'articles dans le flux
```

### 2.3 Explications des Champs Importants

#### `container`

**Rôle** : Identifie chaque article individuel dans la page.

**Exemples** :
```yaml
# Simple
container: "article"

# Avec classe
container: ".blog-post"

# Wildcard pour classes dynamiques
container: "[class*='ArticleCard']"

# Plusieurs options (essaie dans l'ordre)
container: "article, .post, [class*='card']"
```

#### `attribute`

**Rôle** : Indique si on extrait un attribut HTML ou le texte.

```yaml
# Extraire l'attribut href
link:
  primary: "a"
  attribute: "href"  # → https://example.com/article

# Extraire le texte
title:
  primary: "h2"
  attribute: null  # ou omis → "Titre de l'article"
```

#### `fallback`

**Rôle** : Liste de sélecteurs alternatifs si le principal échoue.

```yaml
title:
  primary: "h2"
  fallback: ["h3", "h1", "[class*='title']"]
  # Essaie h2 → h3 → h1 → [class*='title'] jusqu'à trouver
```

#### `optional`

**Rôle** : Permet de continuer même si l'élément n'est pas trouvé.

```yaml
description:
  primary: "p"
  optional: true  # Ne pas échouer si pas de description
```

#### Formats de Dates

Référence complète : [strftime.org](https://strftime.org/)

```yaml
date_formats:
  - "%B %d, %Y"          # February 26, 2025
  - "%Y-%m-%d"           # 2025-02-26
  - "%d/%m/%Y"           # 26/02/2025
  - "%b %d, %Y"          # Feb 26, 2025
  - "%Y-%m-%dT%H:%M:%S"  # 2025-02-26T14:30:00
```

## 🧪 Étape 3 : Tester les Sélecteurs

### 3.1 Valider la Configuration

```bash
python validate_config.py config/ma_source.yaml
```

Cela vérifie :
- ✓ Syntaxe YAML correcte
- ✓ Tous les champs requis présents
- ✓ URLs valides
- ✓ Sélecteurs CSS basiques

### 3.2 Tester le Scraping

```bash
# Tester avec logs détaillés
python generate_feeds.py --source ma_source --log-level DEBUG
```

**Que vérifier** :
- Le nombre d'articles trouvés
- Les titres extraits
- Les URLs des articles
- Les dates parsées

**Si ça ne fonctionne pas** :
1. Vérifiez les logs pour identifier quel sélecteur échoue
2. Retournez dans les DevTools pour trouver un meilleur sélecteur
3. Ajustez la configuration
4. Re-testez

### 3.3 Exemple de Debug

```bash
$ python generate_feeds.py --source mistral --log-level DEBUG

📥 Processing source: mistral
  🔍 Scraping mistral...
DEBUG - Loading page: https://mistral.ai/news
DEBUG - Waiting for container: article
DEBUG - Found 12 article containers
DEBUG - Found: Mistral AI announces... - February 26, 2025
DEBUG - Found: New research paper... - February 20, 2025
...
  ✓ Found 12 articles
  📝 Generating RSS feed...
  ✅ RSS feed generated: output/mistral_rss.xml
```

## ✅ Étape 4 : Activer la Source

### 4.1 Ajouter dans sources.yaml

Éditez `config/sources.yaml` et ajoutez votre source :

```yaml
active_sources:
  - mistral
  - anthropic
  - ma_source  # ← Votre nouvelle source
```

### 4.2 Vérifier la Fusion

Si la fusion est activée, testez-la :

```bash
python generate_feeds.py
```

Vérifiez que le fichier `output/merged_feed.xml` contient les articles de toutes les sources.

## 🚀 Étape 5 : Déployer sur GitHub

### 5.1 Commiter les Changements

```bash
git add config/ma_source.yaml config/sources.yaml
git commit -m "Add new source: Ma Source"
git push
```

### 5.2 Vérifier GitHub Actions

1. Allez dans l'onglet **Actions** de votre repo
2. Le workflow devrait se déclencher automatiquement
3. Vérifiez les logs pour voir si le scraping fonctionne
4. Les flux XML seront committes automatiquement dans `output/`

## 📚 Exemples Concrets

### Exemple 1 : Anthropic Engineering Blog

**Site** : https://www.anthropic.com/engineering

**Particularités** :
- Classes CSS générées dynamiquement
- Structure : `div[class*='ArticleList'] > div > article`

**Configuration** :

```yaml
source:
  name: "Anthropic Engineering"
  url: "https://www.anthropic.com/engineering"
  description: "Latest engineering posts from Anthropic"

scraping:
  wait_time: 3000
  wait_strategy: "networkidle"

  selectors:
    # Wildcard pour classes dynamiques
    container: "div[class*='ArticleList_articles__'] > div > article"

    title:
      # Chemin complet vers le titre
      primary: "a > div[class*='ArticleList_content__'] > h3"
      fallback: ["h3", "h2"]

    link:
      primary: "a"
      attribute: "href"

    date:
      # La date est dans un div sans classe spécifique
      primary: "a > div[class*='ArticleList_content__'] > div"
      fallback: ["time", "[class*='date']"]
      attribute: null  # Texte brut, pas d'attribut

  url_handling:
    make_absolute: true
    base_url: "https://www.anthropic.com"

  date_formats:
    - "%B %d, %Y"  # February 26, 2025

rss:
  output_file: "anthropic_rss.xml"
  title: "Anthropic Engineering Blog"
  link: "https://www.anthropic.com/engineering"
```

**Leçons** :
- ✅ Utiliser `[class*='partial']` pour classes dynamiques
- ✅ Spécifier le chemin complet si nécessaire
- ✅ `attribute: null` pour extraire le texte

### Exemple 2 : Blog Simple (WordPress)

**Site** : https://example.com/blog

**Particularités** :
- Structure WordPress classique
- URLs relatives `/blog/article-slug`

**Configuration** :

```yaml
source:
  name: "Example Blog"
  url: "https://example.com/blog"
  description: "Articles from Example Blog"

scraping:
  wait_time: 2000
  wait_strategy: "load"

  selectors:
    container: "article.post"

    title:
      primary: "h2.entry-title"
      fallback: ["h2", "h3"]

    link:
      primary: "h2.entry-title a"
      fallback: ["a.permalink", "a"]
      attribute: "href"

    date:
      primary: "time.published"
      fallback: [".entry-date", "time"]
      attribute: "datetime"

    description:
      primary: ".entry-excerpt"
      fallback: [".entry-summary", "p"]
      optional: true

  url_handling:
    make_absolute: true
    base_url: "https://example.com"

  date_formats:
    - "%Y-%m-%dT%H:%M:%S%z"
    - "%B %d, %Y"

rss:
  output_file: "example_rss.xml"
  title: "Example Blog"
  link: "https://example.com/blog"
```

**Leçons** :
- ✅ Classes WordPress classiques : `.entry-title`, `.published`
- ✅ `make_absolute: true` pour URLs relatives
- ✅ Multiple formats de dates

### Exemple 3 : Site avec JavaScript Lourd

**Site** : Site moderne avec rendu côté client

**Particularités** :
- Contenu chargé en JavaScript
- Besoin d'attendre le chargement réseau

**Configuration** :

```yaml
source:
  name: "JS Heavy Site"
  url: "https://example.com"
  description: "Site with heavy JavaScript"

scraping:
  # Attendre plus longtemps
  wait_time: 5000
  # Attendre que le réseau soit inactif
  wait_strategy: "networkidle"

  selectors:
    # Les sélecteurs apparaissent après le chargement JS
    container: "[data-testid='article-card']"

    title:
      primary: "h3"
      fallback: ["h2", "[class*='title']"]

    link:
      primary: "a[data-testid='article-link']"
      fallback: ["a"]
      attribute: "href"

    date:
      primary: "[data-testid='publish-date']"
      fallback: ["time", "span"]
      attribute: null

  url_handling:
    make_absolute: true
    base_url: "https://example.com"

rss:
  output_file: "js_site_rss.xml"
  title: "JS Heavy Site"
  link: "https://example.com"
```

**Leçons** :
- ✅ `wait_time` plus long pour JS
- ✅ `wait_strategy: "networkidle"` crucial
- ✅ Utiliser `[data-testid]` si disponible

## 🔍 Astuces Avancées

### Sélecteurs CSS Multiples dans `container`

```yaml
# Essaie plusieurs sélecteurs
container: "article, .blog-post, [class*='card'], main > div"
```

### Extraire depuis un Élément Parent

Si le lien est sur un élément parent :

```html
<article>
  <a href="/article">
    <h2>Titre</h2>
    <time>Date</time>
  </a>
</article>
```

```yaml
container: "article"
link:
  primary: "a"  # Le lien parent
  attribute: "href"
title:
  primary: "a > h2"  # Le titre enfant
date:
  primary: "a > time"  # La date enfant
```

### Dates sans Attribut `datetime`

Si la date est en texte brut :

```html
<span class="date">February 26, 2025</span>
```

```yaml
date:
  primary: ".date"
  attribute: null  # ← Important !
```

### Wildcards pour Classes Dynamiques

React, Vue, etc. génèrent des classes avec hash :

```html
<div class="ArticleCard_container__a1b2c3">...</div>
```

Utilisez `[class*='partial']` :

```yaml
container: "[class*='ArticleCard_container']"
```

## ❓ FAQ

### Q : Le site bloque mon scraper, que faire ?

**R** : Playwright utilise un vrai navigateur, donc c'est rare. Si ça arrive :
- Augmentez `wait_time`
- Changez `wait_strategy`
- Vérifiez que le site est public (pas derrière un login)

### Q : Les dates ne se parsent pas, comment trouver le bon format ?

**R** :
1. Regardez exactement le texte de la date sur le site
2. Consultez [strftime.org](https://strftime.org/)
3. Testez le format :

```python
from datetime import datetime
datetime.strptime("February 26, 2025", "%B %d, %Y")
```

### Q : Le container trouve 0 articles, pourquoi ?

**R** :
- Vérifiez que vous testez le bon sélecteur dans la console du navigateur
- Augmentez `wait_time` (le contenu charge peut-être lentement)
- Essayez `wait_strategy: "networkidle"`
- Utilisez `--log-level DEBUG` pour voir ce qui se passe

### Q : Peut-on scraper plusieurs pages ?

**R** : Non, le scraper se concentre sur une seule page (la page principale du blog). C'est par design pour rester simple et rapide.

### Q : Comment gérer un site avec pagination ?

**R** : Le scraper extrait uniquement la première page. La plupart des blogs affichent 10-20 derniers articles sur la page d'accueil, ce qui suffit pour un flux RSS.

## 🎉 Félicitations !

Vous savez maintenant comment ajouter n'importe quelle source RSS au générateur. N'hésitez pas à :
- Partager vos configurations via une Pull Request
- Signaler des problèmes dans les Issues
- Améliorer ce guide

**Besoin d'aide ?** Ouvrez une issue sur GitHub avec :
- L'URL du site que vous essayez de scraper
- Votre fichier de configuration
- Les logs d'erreur complets