# Guide d'Utilisation - Script to Desktop App Converter

Ce guide vous explique comment utiliser le Script to Desktop App Converter pour transformer vos scripts Python en applications de bureau professionnelles.

## 📚 Table des Matières

1. [Démarrage Rapide](#-démarrage-rapide)
2. [Interface Graphique Tkinter](#-interface-graphique-tkinter)
3. [Interface Web Flask](#-interface-web-flask)
4. [Ligne de Commande](#-ligne-de-commande)
5. [Gestion des Projets](#-gestion-des-projets)
6. [Configuration Avancée](#-configuration-avancée)
7. [Construction d'Exécutables](#-construction-dexécutables)
8. [Exemples Pratiques](#-exemples-pratiques)
9. [Dépannage](#-dépannage)

## 🚀 Démarrage Rapide

### Étape 1: Lancement de l'Application

```bash
# Interface graphique (recommandée pour débutants)
python Script_to_code_DesktopApp_and_to_exe.py --gui

# Interface web (idéale pour collaboration)
python Script_to_code_DesktopApp_and_to_exe.py --web

# Ligne de commande (parfait pour automation)
python Script_to_code_DesktopApp_and_to_exe.py mon_script.py
```

### Étape 2: Processus de Conversion

1. **Chargement du Script**: Importez votre fichier Python
2. **Analyse Automatique**: Le système détecte le framework GUI approprié  
3. **Configuration**: Personnalisez les paramètres du projet
4. **Prévisualisation**: Vérifiez le code GUI généré
5. **Construction**: Créez l'exécutable final

## 🖥️ Interface Graphique Tkinter

### Première Utilisation

![Interface Tkinter](docs/images/tkinter-main.png)

#### Lancement
```bash
python Script_to_code_DesktopApp_and_to_exe.py --gui
```

#### Navigation dans l'Interface

**Barre d'Outils Principale**
- **📁 Ouvrir Script**: Charger un fichier Python existant
- **💾 Sauvegarder Projet**: Enregistrer la configuration actuelle
- **📋 Charger Projet**: Reprendre un projet sauvegardé
- **🔧 Construire**: Lancer la construction de l'exécutable

**Onglets Principaux**

### 📝 Onglet Code Source

Cet onglet vous permet de visualiser et modifier le code source de votre script.

![Code Source Tab](docs/images/source-tab.png)

**Fonctionnalités:**
- **Éditeur de Code**: Syntaxe highlighting intégré
- **Numérotation des Lignes**: Navigation facilitée
- **Analyse en Temps Réel**: Détection automatique des imports et frameworks
- **Validation**: Vérification de la syntaxe Python

**Actions Disponibles:**
```
📁 Charger    : Ouvrir un nouveau fichier
💾 Sauvegarder : Exporter le code modifié
🔍 Analyser   : Lancer l'analyse du code
```

**Zone d'Analyse**
L'analyse affiche:
- Framework GUI détecté
- Nombre de lignes de code
- Complexité cyclomatique
- Liste des imports
- Fonctions et classes trouvées

### ⚙️ Onglet Configuration

Configuration complète de votre projet avec toutes les options disponibles.

![Configuration Tab](docs/images/config-tab.png)

#### Informations Générales

**Métadonnées du Projet**
- **Nom**: Nom de l'application (utilisé pour l'exécutable)
- **Description**: Description courte du projet
- **Auteur**: Votre nom ou organisation
- **Version**: Numéro de version (format: X.Y.Z)

```
Exemple:
Nom: Calculateur Scientifique
Description: Calculateur avec fonctions avancées
Auteur: Jean Dupont
Version: 1.2.0
```

#### Interface Graphique

**Framework GUI**
- **Tkinter**: Interface native Python (recommandé pour la compatibilité)
- **PyQt5**: Interface moderne (nécessite installation séparée)
- **PyQt6**: Dernière version PyQt (nécessite installation séparée)
- **Flask**: Application web (accessible via navigateur)
- **Console**: Interface texte/terminal

**Thèmes Disponibles**
- **default**: Thème standard du système
- **dark**: Mode sombre moderne
- **light**: Mode clair optimisé
- **modern**: Design contemporain
- **classic**: Style traditionnel

**Icône Personnalisée**
- Support des formats: `.ico`, `.png`, `.jpg`
- Taille recommandée: 256x256 pixels
- L'icône apparaîtra dans l'exécutable et la barre des tâches

#### Options de Construction

![Build Options](docs/images/build-options.png)

**Architecture Cible**
- **x64**: 64-bit (recommandé pour les systèmes modernes)
- **x86**: 32-bit (compatibilité avec anciens systèmes)
- **auto**: Détection automatique

**Options Avancées**
- ✅ **Fichier Unique**: Créer un seul fichier .exe (plus lent au démarrage)
- ✅ **Inclure Console**: Garder la fenêtre console (utile pour debug)
- ✅ **Compression UPX**: Réduire la taille du fichier (nécessite UPX)
- ✅ **Mode Debug**: Informations détaillées pour dépannage

#### Gestion des Dépendances

**Détection Automatique**
```
🔍 Auto-détecter : Analyse automatique des imports
➕ Ajouter       : Ajouter manuellement un module
➖ Supprimer     : Retirer une dépendance
```

**Modules Couramment Détectés**
- numpy, pandas (calcul scientifique)
- requests (requêtes HTTP)
- matplotlib (graphiques)
- pillow (traitement d'images)
- sqlalchemy (base de données)

### 👁️ Onglet Prévisualisation

Visualisez le code GUI qui sera généré avant la construction.

![Preview Tab](docs/images/preview-tab.png)

**Fonctionnalités:**
- **Code Généré**: Affichage du code Python complet
- **Coloration Syntaxique**: Lecture facilitée
- **Export**: Sauvegarde du code GUI dans un fichier
- **Actualisation**: Mise à jour en temps réel des modifications

**Structure du Code Généré:**
```python
# En-tête avec métadonnées
# Imports nécessaires pour le framework choisi
# Classe principale de l'application
# Interface utilisateur complète
# Intégration du code original
# Point d'entrée principal
```

### 🔧 Onglet Construction

Suivi en temps réel de la création de l'exécutable.

![Build Tab](docs/images/build-tab.png)

**Contrôles de Construction**
- **🚀 Construire**: Lancer le processus de build
- **❌ Annuler**: Interrompre la construction en cours
- **Barre de Progression**: Indicateur visuel du progrès

**Journal de Construction**
- Affichage en temps réel des étapes PyInstaller
- Messages d'erreur détaillés
- Confirmation de réussite avec chemin du fichier
- Statistiques de performance

**États Possibles:**
```
⏳ Préparation    : Génération du code GUI
🔄 Analyse        : Détection des dépendances  
📦 Compilation    : Construction avec PyInstaller
✅ Terminé        : Exécutable créé avec succès
❌ Erreur         : Problème durant la construction
```

### 📁 Onglet Projets

Gestion complète de vos projets sauvegardés.

![Projects Tab](docs/images/projects-tab.png)

**Fonctionnalités:**
- **Liste des Projets**: Affichage tabulaire avec dates
- **Chargement Rapide**: Double-clic pour ouvrir un projet
- **Suppression**: Nettoyage des projets obsolètes
- **Tri et Filtrage**: Organisation de vos projets

**Informations Affichées:**
- Nom du projet
- Date de création
- Dernière modification
- Actions disponibles (Charger/Supprimer)

## 🌐 Interface Web Flask

### Accès à l'Interface Web

```bash
# Démarrage du serveur web
python Script_to_code_DesktopApp_and_to_exe.py --web

# Par défaut accessible sur:
# http://localhost:5000
```

**Configuration Personnalisée:**
```bash
# Changement du port
python Script_to_code_DesktopApp_and_to_exe.py --web --port 8080

# Accès réseau (attention à la sécurité)
python Script_to_code_DesktopApp_and_to_exe.py --web --host 0.0.0.0
```

### Navigation Web

![Web Interface](docs/images/web-main.png)

#### Page d'Accueil
- **Vue d'ensemble**: Présentation des fonctionnalités
- **Projets Récents**: Accès rapide aux derniers projets
- **Statistiques**: Nombre de projets, conversions réalisées

#### Upload de Script

![Web Upload](docs/images/web-upload.png)

**Processus d'Upload:**
1. **Sélection du Fichier**: Glisser-déposer ou navigation
2. **Validation**: Vérification du format et de la taille
3. **Analyse Automatique**: Détection du framework GUI
4. **Redirection**: Vers la page de configuration

**Formats Supportés:**
- `.py` : Scripts Python standard
- `.pyw` : Scripts Python sans console (Windows)
- Taille max: 50 MB par fichier

#### Configuration Web

![Web Configuration](docs/images/web-config.png)

**Interface Responsive:**
- Adaptation automatique mobile/desktop
- Formulaires interactifs avec validation
- Prévisualisation en temps réel
- Sauvegarde automatique des modifications

**Fonctionnalités Spécifiques Web:**
- **Drag & Drop**: Import de fichiers par glisser-déposer
- **Prévisualisation Modale**: Code affiché dans une popup
- **Construction Asynchrone**: Suivi en temps réel via WebSocket
- **Téléchargement Direct**: Récupération de l'exécutable généré

## ⚡ Ligne de Commande

### Syntaxe Générale

```bash
python Script_to_code_DesktopApp_and_to_exe.py [OPTIONS] [SCRIPT]
```

### Commandes de Base

#### Conversion Simple
```bash
# Conversion avec détection automatique
python Script_to_code_DesktopApp_and_to_exe.py mon_script.py

# Spécification du framework
python Script_to_code_DesktopApp_and_to_exe.py mon_script.py --framework tkinter
```

#### Configuration Complète
```bash
python Script_to_code_DesktopApp_and_to_exe.py mon_script.py \
    --name "Mon Application" \
    --description "Application de démonstration" \
    --author "Votre Nom" \
    --version "1.0.0" \
    --framework tkinter \
    --theme modern \
    --icon icon.ico \
    --build \
    --onefile \
    --no-console
```

### Options Détaillées

#### Métadonnées du Projet
```bash
--name "Nom"              # Nom de l'application
--description "Desc"      # Description du projet  
--author "Auteur"         # Nom de l'auteur
--version "1.0.0"         # Version du projet
```

#### Framework et Interface
```bash
--framework tkinter       # tkinter|PyQt5|PyQt6|flask|console
--theme modern           # default|dark|light|modern|classic
--icon chemin/icon.ico   # Chemin vers l'icône
```

#### Options de Construction
```bash
--build                  # Construire l'exécutable
--output /chemin/sortie  # Dossier de sortie personnalisé
--onefile               # Créer un fichier unique
--onedir                # Créer un dossier (défaut)
--console               # Inclure la console
--no-console            # Masquer la console (défaut)
--debug                 # Mode debug activé
--upx                   # Compression UPX
--arch x64              # Architecture (x86|x64|auto)
```

#### Gestion des Projets
```bash
--save "NomProjet"       # Sauvegarder le projet
--load "NomProjet"       # Charger un projet existant
--list-projects          # Lister tous les projets
--delete-project "Nom"   # Supprimer un projet
```

#### Actions Spécifiques
```bash
--analyze               # Analyser seulement le code
--preview               # Afficher la prévisualisation
--export fichier.py     # Exporter le code GUI
```

### Exemples Pratiques CLI

#### Exemple 1: Conversion Basique
```bash
# Script simple vers Tkinter
python Script_to_code_DesktopApp_and_to_exe.py calculator.py \
    --name "Calculateur" \
    --build
```

#### Exemple 2: Application Complète
```bash
# Configuration complète avec construction
python Script_to_code_DesktopApp_and_to_exe.py data_analyzer.py \
    --name "Analyseur de Données" \
    --description "Outil d'analyse de fichiers CSV" \
    --author "DataScience Team" \
    --version "2.1.0" \
    --framework tkinter \
    --theme dark \
    --icon assets/analyzer.ico \
    --build \
    --onefile \
    --no-console \
    --upx \
    --save "DataAnalyzer"
```

#### Exemple 3: Traitement par Lots
```bash
# Script de traitement multiple
for script in *.py; do
    python Script_to_code_DesktopApp_and_to_exe.py "$script" \
        --framework tkinter \
        --build \
        --output "dist/"
done
```

#### Exemple 4: Flask Web App
```bash
# Application web avec Flask
python Script_to_code_DesktopApp_and_to_exe.py api_client.py \
    --framework flask \
    --name "API Dashboard" \
    --port 8080 \
    --build
```

## 💾 Gestion des Projets

### Sauvegarde de Projets

![Project Management](docs/images/project-management.png)

#### Via l'Interface Graphique
1. Configurez votre projet dans l'onglet Configuration
2. Cliquez sur **💾 Sauvegarder Projet**
3. Saisissez un nom unique pour le projet
4. Confirmation de sauvegarde

#### Via la Ligne de Commande
```bash
# Sauvegarde avec conversion
python Script_to_code_DesktopApp_and_to_exe.py script.py \
    --name "MonApp" \
    --save "MonApp_v1"

# Sauvegarde d'un projet existant
python Script_to_code_DesktopApp_and_to_exe.py \
    --load "MonApp_v1" \
    --save "MonApp_v2"
```

### Chargement de Projets

#### Interface Graphique
1. Cliquez sur **📋 Charger Projet**
2. Sélectionnez le projet dans la liste
3. Double-clic ou bouton **Charger**
4. Le projet se charge automatiquement

#### Ligne de Commande
```bash
# Chargement et construction
python Script_to_code_DesktopApp_and_to_exe.py \
    --load "MonApp_v1" \
    --build

# Chargement et modification
python Script_to_code_DesktopApp_and_to_exe.py \
    --load "MonApp_v1" \
    --version "1.1.0" \
    --save "MonApp_v1.1"
```

### Base de Données des Projets

**Structure SQLite:**
```sql
-- Table des projets
CREATE TABLE projects (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    config TEXT NOT NULL,        -- Configuration JSON
    source_code TEXT,            -- Code source
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Table de l'historique
CREATE TABLE conversion_history (
    id INTEGER PRIMARY KEY,
    project_id INTEGER,
    status TEXT NOT NULL,
    log_output TEXT,
    output_path TEXT,
    created_at TIMESTAMP
);
```

**Localisation de la Base:**
- Défaut: `converter.db` dans le répertoire du script
- Personnalisable via variable d'environnement `CONVERTER_DB_PATH`

## ⚙️ Configuration Avancée

### Fichier de Configuration

Créez un fichier `config.json` pour personnaliser le comportement:

```json
{
    "default_settings": {
        "framework": "tkinter",
        "theme": "modern",
        "auto_detect_gui": true,
        "include_console": false,
        "one_file": true,
        "upx_compress": false,
        "debug_mode": false
    },
    "paths": {
        "upload_folder": "uploads",
        "output_folder": "output", 
        "templates_folder": "templates",
        "static_folder": "static"
    },
    "build_options": {
        "timeout": 300,
        "max_file_size": 52428800,
        "allowed_extensions": [".py", ".pyw"],
        "pyinstaller_args": [
            "--clean",
            "--noconfirm"
        ]
    },
    "web_interface": {
        "host": "127.0.0.1",
        "port": 5000,
        "debug": false,
        "secret_key": "your-secret-key-here"
    },
    "logging": {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "file": "converter.log"
    }
}
```

### Variables d'Environnement

```bash
# Chemins personnalisés
export CONVERTER_UPLOAD_DIR="/custom/uploads"
export CONVERTER_OUTPUT_DIR="/custom/output"
export CONVERTER_DB_PATH="/custom/converter.db"

# Configuration de logging
export CONVERTER_LOG_LEVEL="DEBUG"
export CONVERTER_LOG_FILE="/custom/converter.log"

# Interface web
export FLASK_HOST="0.0.0.0"
export FLASK_PORT="8080"
export FLASK_ENV="development"

# Options de construction
export PYINSTALLER_TIMEOUT="600"
export UPX_PATH="/usr/local/bin/upx"
```

### Templates Personnalisés

Créez vos propres templates dans le dossier `templates/custom/`:

```python
# templates/custom/mon_template.py
def generate_custom_template(original_code, config):
    return f'''
# Template personnalisé pour {config.name}
import tkinter as tk
from tkinter import ttk

class {config.name}App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("{config.name}")
        self.setup_ui()
    
    def setup_ui(self):
        # Interface personnalisée
        pass
    
    def run_original_code(self):
        # Code original intégré
{chr(10).join("        " + line for line in original_code.splitlines())}

if __name__ == "__main__":
    app = {config.name}App()
    app.mainloop()
'''
```

## 🔨 Construction d'Exécutables

### Processus de Construction

![Build Process](docs/images/build-process.png)

#### Étapes Automatiques
1. **Génération du Code GUI**: Création du wrapper selon le framework
2. **Analyse des Dépendances**: Détection automatique des modules requis
3. **Configuration PyInstaller**: Génération du fichier .spec si nécessaire
4. **Compilation**: Exécution de PyInstaller avec options optimisées
5. **Vérification**: Contrôle de l'exécutable généré
6. **Nettoyage**: Suppression des fichiers temporaires

#### Fichiers Générés
```
output/
├── MonApp.exe                 # Exécutable principal (--onefile)
├── MonApp/                    # Dossier application (--onedir)
│   ├── MonApp.exe
│   ├── _internal/
│   └── ...
├── build/                     # Fichiers de construction (temporaires)
└── MonApp.spec               # Fichier de configuration PyInstaller
```

### Options de Construction Détaillées

#### Fichier Unique vs Dossier

**--onefile (Recommandé)**
- ✅ Un seul fichier .exe
- ✅ Distribution simplifiée
- ❌ Démarrage plus lent
- ❌ Extraction temporaire à chaque lancement

**--onedir**
- ✅ Démarrage rapide
- ✅ Mise à jour partielle possible
- ❌ Multiples fichiers à distribuer
- ❌ Plus complexe à installer

#### Console Windows

**--console**
- Affiche une fenêtre console noire
- Utile pour le debug et les messages d'erreur
- Peut afficher les prints() du code original

**--no-console (Recommandé)**
- Interface propre sans console
- Aspect plus professionnel
- Les erreurs sont loggées dans des fichiers

#### Compression UPX

**Avantages:**
- Réduction de 30-70% de la taille du fichier
- Décompression automatique à l'exécution

**Inconvénients:**
- Temps de construction plus long
- Possible détection fausse positive par antivirus
- Nécessite l'installation d'UPX

**Installation d'UPX:**
```bash
# Windows (avec Chocolatey)
choco install upx

# Ubuntu/Debian
sudo apt-get install upx-ucl

# macOS (avec Homebrew)
brew install upx

# Manuel
# Télécharger depuis https://upx.github.io/
```

### Optimisation des Performances

#### Réduction de la Taille

**Exclusion de Modules Inutiles:**
```python
# Dans votre script, ajoutez:
# -*- pyinstaller: excludes=module1,module2 -*-

# Ou via ligne de commande:
--exclude-module module1 --exclude-module module2
```

**Optimisation des Imports:**
```python
# Évitez les imports globaux inutiles
# Au lieu de:
import numpy as np

# Préférez:
def ma_fonction():
    import numpy as np  # Import local
    return np.array([1, 2, 3])
```

#### Amélioration du Temps de Démarrage

**Cache des Modules:**
- PyInstaller met en cache les modules compilés
- Le cache est dans `%LocalAppData%/pyinstaller` (Windows)
- Supprimez le cache si vous rencontrez des problèmes

**Options d'Optimisation:**
```bash
# Construction optimisée
python Script_to_code_DesktopApp_and_to_exe.py script.py \
    --build \
    --onedir \
    --optimize 2 \
    --strip
```

### Dépannage de la Construction

#### Erreurs Courantes

**1. PyInstaller Non Trouvé**
```bash
# Solution:
pip install pyinstaller

# Vérification:
pyinstaller --version
```

**2. Module Non Trouvé**
```bash
# Erreur: ModuleNotFoundError: No module named 'mon_module'
# Solution: Ajout manuel de la dépendance
--hidden-import mon_module
```

**3. Erreur de Permissions (Windows)**
```bash
# Solution: Exécuter en tant qu'administrateur
# Ou désactiver temporairement l'antivirus
```

**4. Fichier Trop Volumineux**
```bash
# Solutions:
# 1. Utiliser --onedir au lieu de --onefile
# 2. Activer la compression UPX
# 3. Exclure les modules inutiles
```

**5. Erreur DLL Windows**
```bash
# Erreur: api-ms-win-*.dll manquant
# Solution: Installer Visual C++ Redistributable
# https://aka.ms/vs/17/release/vc_redist.x64.exe
```

## 📋 Exemples Pratiques

### Exemple 1: Calculateur Simple

**Code Original (calculator.py):**
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import math

def calculer():
    print("=== Calculateur Simple ===")
    
    while True:
        try:
            print("\nOpérations disponibles:")
            print("1. Addition (+)")
            print("2. Soustraction (-)")
            print("3. Multiplication (*)")
            print("4. Division (/)")
            print("5. Puissance (**)")
            print("6. Racine carrée (sqrt)")
            print("7. Quitter")
            
            choix = input("\nChoix (1-7): ")
            
            if choix == "7":
                print("Au revoir!")
                break
            
            if choix in ["1", "2", "3", "4", "5"]:
                a = float(input("Premier nombre: "))
                b = float(input("Deuxième nombre: "))
                
                if choix == "1":
                    resultat = a + b
                    print(f"Résultat: {a} + {b} = {resultat}")
                elif choix == "2":
                    resultat = a - b
                    print(f"Résultat: {a} - {b} = {resultat}")
                elif choix == "3":
                    resultat = a * b
                    print(f"Résultat: {a} × {b} = {resultat}")
                elif choix == "4":
                    if b != 0:
                        resultat = a / b
                        print(f"Résultat: {a} ÷ {b} = {resultat}")
                    else:
                        print("Erreur: Division par zéro!")
                elif choix == "5":
                    resultat = a ** b
                    print(f"Résultat: {a}^{b} = {resultat}")
            
            elif choix == "6":
                a = float(input("Nombre: "))
                if a >= 0:
                    resultat = math.sqrt(a)
                    print(f"Résultat: √{a} = {resultat}")
                else:
                    print("Erreur: Racine carrée d'un nombre négatif!")
            
            else:
                print("Choix invalide!")
        
        except ValueError:
            print("Erreur: Veuillez saisir un nombre valide!")
        except Exception as e:
            print(f"Erreur inattendue: {e}")

if __name__ == "__main__":
    calculer()
```

**Conversion:**
```bash
# Interface graphique
python Script_to_code_DesktopApp_and_to_exe.py --gui
# Puis charger calculator.py

# Ligne de commande
python Script_to_code_DesktopApp_and_to_exe.py calculator.py \
    --name "Calculateur Simple" \
    --description "Calculateur avec opérations de base" \
    --author "Votre Nom" \
    --version "1.0.0" \
    --framework tkinter \
    --theme modern \
    --build \
    --onefile \
    --no-console
```

**Résultat:** Application Tkinter avec interface graphique complète intégrant toutes les fonctions de calcul.

### Exemple 2: Gestionnaire de Fichiers

**Code Original (file_manager.py):**
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
from pathlib import Path
from datetime import datetime

class FileManager:
    def __init__(self):
        self.current_dir = Path.cwd()
    
    def lister_fichiers(self, chemin=None):
        """Liste les fichiers d'un répertoire"""
        if chemin is None:
            chemin = self.current_dir
        else:
            chemin = Path(chemin)
        
        if not chemin.exists():
            return "Répertoire inexistant"
        
        fichiers = []
        for item in chemin.iterdir():
            stats = item.stat()
            taille = stats.st_size
            modif = datetime.fromtimestamp(stats.st_mtime)
            
            fichiers.append({
                'nom': item.name,
                'type': 'Dossier' if item.is_dir() else 'Fichier',
                'taille': taille,
                'modification': modif.strftime('%Y-%m-%d %H:%M')
            })
        
        return sorted(fichiers, key=lambda x: x['nom'])
    
    def copier_fichier(self, source, destination):
        """Copie un fichier"""
        try:
            shutil.copy2(source, destination)
            return f"Fichier copié: {source} → {destination}"
        except Exception as e:
            return f"Erreur copie: {e}"
    
    def deplacer_fichier(self, source, destination):
        """Déplace un fichier"""
        try:
            shutil.move(source, destination)
            return f"Fichier déplacé: {source} → {destination}"
        except Exception as e:
            return f"Erreur déplacement: {e}"
    
    def supprimer_fichier(self, chemin):
        """Supprime un fichier ou dossier"""
        try:
            chemin = Path(chemin)
            if chemin.is_file():
                chemin.unlink()
                return f"Fichier supprimé: {chemin}"
            elif chemin.is_dir():
                shutil.rmtree(chemin)
                return f"Dossier supprimé: {chemin}"
        except Exception as e:
            return f"Erreur suppression: {e}"
    
    def creer_dossier(self, nom):
        """Crée un nouveau dossier"""
        try:
            nouveau_dossier = self.current_dir / nom
            nouveau_dossier.mkdir(exist_ok=True)
            return f"Dossier créé: {nouveau_dossier}"
        except Exception as e:
            return f"Erreur création: {e}"
    
    def changer_repertoire(self, nouveau_chemin):
        """Change le répertoire courant"""
        try:
            nouveau_chemin = Path(nouveau_chemin)
            if nouveau_chemin.exists() and nouveau_chemin.is_dir():
                self.current_dir = nouveau_chemin
                return f"Répertoire changé: {self.current_dir}"
            else:
                return "Répertoire invalide"
        except Exception as e:
            return f"Erreur changement: {e}"

def main():
    fm = FileManager()
    
    print("=== Gestionnaire de Fichiers ===")
    print(f"Répertoire courant: {fm.current_dir}")
    
    while True:
        print("\nCommandes disponibles:")
        print("1. Lister fichiers")
        print("2. Copier fichier")
        print("3. Déplacer fichier")
        print("4. Supprimer fichier")
        print("5. Créer dossier")
        print("6. Changer répertoire")
        print("7. Quitter")
        
        choix = input("\nChoix (1-7): ")
        
        if choix == "1":
            fichiers = fm.lister_fichiers()
            print(f"\nContenu de {fm.current_dir}:")
            for f in fichiers:
                print(f"{f['type']:8} {f['nom']:30} {f['taille']:>10} bytes {f['modification']}")
        
        elif choix == "2":
            source = input("Fichier source: ")
            dest = input("Destination: ")
            print(fm.copier_fichier(source, dest))
        
        elif choix == "3":
            source = input("Fichier source: ")
            dest = input("Destination: ")
            print(fm.deplacer_fichier(source, dest))
        
        elif choix == "4":
            chemin = input("Fichier/dossier à supprimer: ")
            print(fm.supprimer_fichier(chemin))
        
        elif choix == "5":
            nom = input("Nom du nouveau dossier: ")
            print(fm.creer_dossier(nom))
        
        elif choix == "6":
            chemin = input("Nouveau répertoire: ")
            print(fm.changer_repertoire(chemin))
        
        elif choix == "7":
            print("Au revoir!")
            break
        
        else:
            print("Choix invalide!")

if __name__ == "__main__":
    main()
```

**Conversion avec Interface Web:**
```bash
# Conversion vers Flask pour interface web
python Script_to_code_DesktopApp_and_to_exe.py file_manager.py \
    --name "Gestionnaire de Fichiers Web" \
    --framework flask \
    --description "Interface web pour gestion de fichiers" \
    --author "Votre Nom" \
    --version "2.0.0" \
    --build \
    --onefile
```

### Exemple 3: Analyseur de Données CSV

**Code Original (csv_analyzer.py):**
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import json
from pathlib import Path
from collections import Counter
import statistics

class CSVAnalyzer:
    def __init__(self):
        self.data = []
        self.headers = []
        self.filename = ""
    
    def charger_csv(self, fichier):
        """Charge un fichier CSV"""
        try:
            self.filename = fichier
            with open(fichier, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                self.headers = reader.fieldnames
                self.data = list(reader)
            
            return f"CSV chargé: {len(self.data)} lignes, {len(self.headers)} colonnes"
        
        except Exception as e:
            return f"Erreur chargement: {e}"
    
    def analyser_colonnes(self):
        """Analyse les colonnes du CSV"""
        if not self.data:
            return "Aucune donnée chargée"
        
        analyses = {}
        
        for col in self.headers:
            valeurs = [row[col] for row in self.data if row[col]]
            
            # Statistiques de base
            analyses[col] = {
                'total': len(self.data),
                'non_vides': len(valeurs),
                'vides': len(self.data) - len(valeurs),
                'uniques': len(set(valeurs)),
                'type_detecte': self.detecter_type(valeurs)
            }
            
            # Statistiques numériques
            if analyses[col]['type_detecte'] == 'numerique':
                try:
                    nums = [float(v) for v in valeurs if v]
                    analyses[col].update({
                        'min': min(nums),
                        'max': max(nums),
                        'moyenne': statistics.mean(nums),
                        'mediane': statistics.median(nums)
                    })
                except:
                    pass
            
            # Valeurs les plus fréquentes
            if valeurs:
                counter = Counter(valeurs)
                analyses[col]['top_valeurs'] = counter.most_common(5)
        
        return analyses
    
    def detecter_type(self, valeurs):
        """Détecte le type d'une colonne"""
        if not valeurs:
            return 'vide'
        
        # Test numérique
        nums = 0
        for val in valeurs[:100]:  # Test sur 100 premières valeurs
            try:
                float(val)
                nums += 1
            except ValueError:
                pass
        
        if nums / len(valeurs[:100]) > 0.8:
            return 'numerique'
        
        # Test date
        dates = 0
        for val in valeurs[:100]:
            if any(sep in val for sep in ['-', '/', ':']):
                dates += 1
        
        if dates / len(valeurs[:100]) > 0.5:
            return 'date'
        
        return 'texte'
    
    def exporter_rapport(self, format='json'):
        """Exporte l'analyse en JSON ou TXT"""
        if not self.data:
            return "Aucune donnée à exporter"
        
        analyses = self.analyser_colonnes()
        
        # Rapport général
        rapport = {
            'fichier': self.filename,
            'resume': {
                'lignes': len(self.data),
                'colonnes': len(self.headers),
                'colonnes_list': self.headers
            },
            'analyses_colonnes': analyses
        }
        
        if format == 'json':
            nom_rapport = f"rapport_{Path(self.filename).stem}.json"
            with open(nom_rapport, 'w', encoding='utf-8') as f:
                json.dump(rapport, f, indent=2, ensure_ascii=False)
            return f"Rapport JSON sauvegardé: {nom_rapport}"
        
        elif format == 'txt':
            nom_rapport = f"rapport_{Path(self.filename).stem}.txt"
            with open(nom_rapport, 'w', encoding='utf-8') as f:
                f.write(f"RAPPORT D'ANALYSE CSV\n")
                f.write(f"Fichier: {self.filename}\n")
                f.write(f"Lignes: {len(self.data)}\n")
                f.write(f"Colonnes: {len(self.headers)}\n\n")
                
                for col, stats in analyses.items():
                    f.write(f"COLONNE: {col}\n")
                    f.write(f"  Type détecté: {stats['type_detecte']}\n")
                    f.write(f"  Valeurs non vides: {stats['non_vides']}\n")
                    f.write(f"  Valeurs uniques: {stats['uniques']}\n")
                    
                    if 'moyenne' in stats:
                        f.write(f"  Moyenne: {stats['moyenne']:.2f}\n")
                        f.write(f"  Min: {stats['min']}, Max: {stats['max']}\n")
                    
                    f.write(f"  Top valeurs: {stats['top_valeurs'][:3]}\n\n")
            
            return f"Rapport TXT sauvegardé: {nom_rapport}"

def main():
    analyzer = CSVAnalyzer()
    
    print("=== Analyseur CSV ===")
    
    while True:
        print("\nOptions:")
        print("1. Charger fichier CSV")
        print("2. Analyser colonnes")
        print("3. Exporter rapport JSON")
        print("4. Exporter rapport TXT")
        print("5. Quitter")
        
        choix = input("\nChoix (1-5): ")
        
        if choix == "1":
            fichier = input("Chemin du fichier CSV: ")
            print(analyzer.charger_csv(fichier))
        
        elif choix == "2":
            analyses = analyzer.analyser_colonnes()
            if isinstance(analyses, dict):
                print(f"\nAnalyse de {analyzer.filename}:")
                for col, stats in analyses.items():
                    print(f"\n{col}:")
                    print(f"  Type: {stats['type_detecte']}")
                    print(f"  Valeurs: {stats['non_vides']}/{stats['total']}")
                    print(f"  Uniques: {stats['uniques']}")
                    if 'moyenne' in stats:
                        print(f"  Moyenne: {stats['moyenne']:.2f}")
            else:
                print(analyses)
        
        elif choix == "3":
            print(analyzer.exporter_rapport('json'))
        
        elif choix == "4":
            print(analyzer.exporter_rapport('txt'))
        
        elif choix == "5":
            print("Au revoir!")
            break
        
        else:
            print("Choix invalide!")

if __name__ == "__main__":
    main()
```

**Conversion Avancée:**
```bash
# Conversion avec configuration complète
python Script_to_code_DesktopApp_and_to_exe.py csv_analyzer.py \
    --name "CSV Analyzer Pro" \
    --description "Analyseur professionnel de fichiers CSV" \
    --author "Data Team" \
    --version "3.1.0" \
    --framework tkinter \
    --theme dark \
    --icon assets/csv-icon.ico \
    --build \
    --onefile \
    --no-console \
    --upx \
    --save "CSVAnalyzer_v3"
```

## 🔍 Dépannage

### Problèmes Courants

#### 1. Erreurs d'Installation

**PyInstaller non trouvé:**
```bash
# Erreur
ModuleNotFoundError: No module named 'PyInstaller'

# Solution
pip install pyinstaller

# Vérification
pip list | grep -i pyinstaller
```

**Permissions insuffisantes (Windows):**
```bash
# Erreur
[Errno 13] Permission denied

# Solutions
# 1. Exécuter en tant qu'administrateur
# 2. Ajouter exception antivirus
# 3. Modifier les permissions du dossier
```

#### 2. Erreurs de Construction

**Modules manquants:**
```bash
# Erreur
ModuleNotFoundError: No module named 'mon_module'

# Solution: Ajouter manuellement
python Script_to_code_DesktopApp_and_to_exe.py script.py \
    --hidden-import mon_module \
    --build
```

**Erreur UPX:**
```bash
# Erreur
upx is not available

# Solution
# 1. Désactiver UPX: --no-upx
# 2. Installer UPX: https://upx.github.io/
# 3. Ajouter UPX au PATH
```

#### 3. Problèmes d'Interface

**Tkinter non disponible (Linux):**
```bash
# Erreur
ImportError: No module named '_tkinter'

# Solution Ubuntu/Debian
sudo apt-get install python3-tk

# Solution CentOS/RHEL
sudo yum install tkinter
# ou
sudo dnf install python3-tkinter
```

**PyQt non trouvé:**
```bash
# Erreur
ModuleNotFoundError: No module named 'PyQt5'

# Solution
pip install PyQt5
# ou pour PyQt6
pip install PyQt6
```

#### 4. Problèmes Web (Flask)

**Port déjà utilisé:**
```bash
# Erreur
OSError: [Errno 98] Address already in use

# Solution
python Script_to_code_DesktopApp_and_to_exe.py --web --port 8080
```

**Erreur de template:**
```bash
# Erreur
TemplateNotFound: index.html

# Solution: Vérifier que le dossier templates/ existe
# Relancer avec --verbose pour plus d'infos
```

### Diagnostic Avancé

#### Mode Verbose
```bash
# Activation des logs détaillés
python Script_to_code_DesktopApp_and_to_exe.py --verbose script.py

# Logs dans un fichier
python Script_to_code_DesktopApp_and_to_exe.py --log-file debug.log script.py
```

#### Test de l'Environnement
```bash
# Vérification de l'installation
python -c "
import sys
print('Python:', sys.version)
try:
    import tkinter
    print('Tkinter: OK')
except ImportError:
    print('Tkinter: MANQUANT')

try:
    import flask
    print('Flask:', flask.__version__)
except ImportError:
    print('Flask: MANQUANT')

try:
    import PyInstaller
    print('PyInstaller:', PyInstaller.__version__)
except ImportError:
    print('PyInstaller: MANQUANT')
"
```

#### Nettoyage de l'Environnement
```bash
# Suppression des fichiers temporaires
rm -rf build/ dist/ __pycache__/ *.spec

# Nettoyage du cache PyInstaller (Windows)
rmdir /s %LocalAppData%\pyinstaller

# Nettoyage du cache PyInstaller (Linux/macOS)
rm -rf ~/.cache/pyinstaller
```

### Support et Aide

#### Ressources Officielles
- [Documentation PyInstaller](https://pyinstaller.readthedocs.io/)
- [Documentation Flask](https://flask.palletsprojects.com/)
- [Documentation Tkinter](https://docs.python.org/3/library/tkinter.html)

#### Communauté
- [Issues GitHub](https://github.com/votre-username/script-to-desktop-converter/issues)
- [Discussions](https://github.com/votre-username/script-to-desktop-converter/discussions)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/pyinstaller)

#### Logs et Débogage
```bash
# Génération d'un rapport de debug complet
python Script_to_code_DesktopApp_and_to_exe.py --debug-report

# Contenu du rapport:
# - Version Python et modules installés
# - Configuration système
# - Logs d'erreurs
# - Trace des opérations
```

---

Ce guide couvre l'utilisation complète du Script to Desktop App Converter. Pour des questions spécifiques ou des cas d'usage avancés, consultez les autres documents de la documentation ou contactez la communauté via GitHub.
