# Guide d'Installation - Script to Desktop App Converter

Guide détaillé pour installer et configurer le Script to Desktop App Converter sur différents systèmes d'exploitation.

## 📚 Table des Matières

1. [Prérequis Système](#-prérequis-système)
2. [Installation Rapide](#-installation-rapide)
3. [Installation Détaillée](#-installation-détaillée)
4. [Configuration Post-Installation](#-configuration-post-installation)
5. [Dépendances Optionnelles](#-dépendances-optionnelles)
6. [Vérification de l'Installation](#-vérification-de-linstallation)
7. [Dépannage](#-dépannage)
8. [Mise à Jour](#-mise-à-jour)
9. [Désinstallation](#-désinstallation)

## 💻 Prérequis Système

### Systèmes d'Exploitation Supportés

| OS | Version Minimale | Recommandée | Architecture |
|---|---|---|---|
| **Windows** | Windows 7 SP1 | Windows 10/11 | x64, x86 |
| **macOS** | macOS 10.14 | macOS 12+ | x64, ARM64 |
| **Linux** | Ubuntu 18.04 | Ubuntu 20.04+ | x64, ARM64 |
| | Debian 10 | Debian 11+ | x64, ARM64 |
| | CentOS 7 | CentOS 8+ | x64 |
| | Fedora 30 | Fedora 35+ | x64 |

### Configuration Matérielle Recommandée

| Composant | Minimum | Recommandé |
|---|---|---|
| **CPU** | Dual-core 2 GHz | Quad-core 3 GHz+ |
| **RAM** | 4 GB | 8 GB+ |
| **Stockage** | 2 GB libre | 5 GB+ libre |
| **Réseau** | Connexion Internet | Haut débit |

### Python et Dépendances

#### Python
- **Version requise**: Python 3.7 ou supérieur
- **Version recommandée**: Python 3.9 ou 3.10
- **Python 3.11+**: Supporté avec limitations mineures

#### Modules Python Requis
```
tkinter          # Interface graphique (généralement inclus)
flask>=2.0.0     # Interface web
sqlite3          # Base de données (inclus)
pathlib          # Gestion des chemins (inclus)
dataclasses      # Classes de données (inclus avec Python 3.7+)
typing           # Annotations de types (inclus)
```

#### Modules Optionnels
```
pyinstaller>=5.0  # Construction d'exécutables
PyQt5>=5.15.0     # Interface PyQt5 (optionnel)
PyQt6>=6.3.0      # Interface PyQt6 (optionnel)
requests>=2.25.0  # Requêtes HTTP
pandas>=1.3.0     # Analyse de données
numpy>=1.21.0     # Calcul numérique
```

## 🚀 Installation Rapide

### Windows

```bash
# 1. Vérifier Python
python --version

# 2. Télécharger le projet
git clone https://github.com/votre-username/script-to-desktop-converter.git
cd script-to-desktop-converter

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Lancer l'application
python Script_to_code_DesktopApp_and_to_exe.py --gui
```

### macOS

```bash
# 1. Installer Python avec Homebrew (si nécessaire)
brew install python@3.9

# 2. Télécharger le projet
git clone https://github.com/votre-username/script-to-desktop-converter.git
cd script-to-desktop-converter

# 3. Créer un environnement virtuel
python3 -m venv venv
source venv/bin/activate

# 4. Installer les dépendances
pip install -r requirements.txt

# 5. Lancer l'application
python Script_to_code_DesktopApp_and_to_exe.py --gui
```

### Linux (Ubuntu/Debian)

```bash
# 1. Installer Python et pip
sudo apt update
sudo apt install python3 python3-pip python3-venv python3-tk git

# 2. Télécharger le projet
git clone https://github.com/votre-username/script-to-desktop-converter.git
cd script-to-desktop-converter

# 3. Créer un environnement virtuel
python3 -m venv venv
source venv/bin/activate

# 4. Installer les dépendances
pip install -r requirements.txt

# 5. Lancer l'application
python Script_to_code_DesktopApp_and_to_exe.py --gui
```

## 🔧 Installation Détaillée

### Étape 1: Vérification de Python

#### Windows
```cmd
# Ouvrir l'Invite de commandes (cmd) ou PowerShell
python --version
# ou si python n'est pas reconnu:
py --version

# Vérifier pip
python -m pip --version
```

Si Python n'est pas installé:
1. Télécharger depuis [python.org](https://www.python.org/downloads/)
2. **Important**: Cocher "Add Python to PATH" pendant l'installation
3. Redémarrer l'invite de commandes

#### macOS
```bash
# Vérifier la version système
python3 --version

# Si absent, installer avec Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install python@3.9
```

#### Linux
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv

# CentOS/RHEL/Fedora
sudo yum install python3 python3-pip  # CentOS 7
sudo dnf install python3 python3-pip  # Fedora/CentOS 8+

# Vérification
python3 --version
pip3 --version
```

### Étape 2: Téléchargement du Projet

#### Méthode 1: Git (Recommandée)
```bash
# Installer Git si nécessaire
# Windows: https://git-scm.com/download/win
# macOS: brew install git
# Linux: sudo apt install git

# Cloner le repository
git clone https://github.com/votre-username/script-to-desktop-converter.git
cd script-to-desktop-converter

# Vérifier le contenu
ls -la  # Linux/macOS
dir     # Windows
```

#### Méthode 2: Téléchargement ZIP
1. Aller sur https://github.com/votre-username/script-to-desktop-converter
2. Cliquer sur "Code" → "Download ZIP"
3. Extraire l'archive
4. Ouvrir un terminal dans le dossier extrait

### Étape 3: Environnement Virtuel (Recommandé)

#### Pourquoi un environnement virtuel?
- Isolation des dépendances
- Évite les conflits entre projets
- Facilite la gestion des versions

#### Création de l'environnement
```bash
# Tous les systèmes
python -m venv venv

# Ou sur Linux/macOS si python pointe vers Python 2
python3 -m venv venv
```

#### Activation de l'environnement

**Windows (cmd):**
```cmd
venv\Scripts\activate
```

**Windows (PowerShell):**
```powershell
venv\Scripts\Activate.ps1
# Si erreur de politique d'exécution:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Linux/macOS:**
```bash
source venv/bin/activate
```

**Vérification de l'activation:**
```bash
# Le prompt doit afficher (venv)
(venv) $ which python  # Linux/macOS
(venv) > where python  # Windows
```

### Étape 4: Installation des Dépendances

#### Fichier requirements.txt
Créer ou vérifier le fichier `requirements.txt`:

```txt
# === DÉPENDANCES PRINCIPALES ===
flask>=2.0.0
werkzeug>=2.0.0

# === CONSTRUCTION D'EXÉCUTABLES ===
pyinstaller>=5.0

# === INTERFACES OPTIONNELLES ===
# PyQt5>=5.15.0  # Décommenter si souhaité
# PyQt6>=6.3.0   # Décommenter si souhaité

# === UTILITAIRES ===
requests>=2.25.0
pathvalidate>=2.5.0

# === DÉVELOPPEMENT (OPTIONNEL) ===
# pytest>=6.0.0
# black>=21.0.0
# flake8>=3.9.0
```

#### Installation
```bash
# Activation de l'environnement virtuel
# (voir étape précédente)

# Mise à jour de pip
python -m pip install --upgrade pip

# Installation des dépendances
pip install -r requirements.txt

# Vérification
pip list
```

#### Installation manuelle (si requirements.txt absent)
```bash
# Dépendances essentielles
pip install flask pyinstaller requests

# Interfaces optionnelles (choisir selon besoins)
pip install PyQt5  # ou PyQt6

# Utilitaires supplémentaires
pip install pathvalidate
```

### Étape 5: Vérification de Tkinter

Tkinter est généralement inclus avec Python, mais parfois absent sur Linux:

#### Test de Tkinter
```python
# Test simple
python -c "import tkinter; print('Tkinter disponible')"
```

#### Installation Tkinter (Linux)
```bash
# Ubuntu/Debian
sudo apt install python3-tk

# CentOS/RHEL
sudo yum install tkinter
# ou
sudo dnf install python3-tkinter

# Fedora
sudo dnf install python3-tkinter
```

## ⚙️ Configuration Post-Installation

### Structure des Répertoires

Après installation, votre projet doit avoir cette structure:

```
script-to-desktop-converter/
├── Script_to_code_DesktopApp_and_to_exe.py  # Script principal
├── requirements.txt                          # Dépendances
├── README.md                                # Documentation
├── config.json                              # Configuration (optionnel)
├── venv/                                    # Environnement virtuel
├── uploads/                                 # Scripts uploadés (créé auto)
├── output/                                  # Exécutables générés (créé auto)
├── templates/                               # Templates Flask (créé auto)
├── static/                                  # Fichiers statiques (créé auto)
├── converter.db                             # Base de données (créé auto)
└── converter.log                            # Logs (créé auto)
```

### Configuration Initiale

#### Fichier config.json (Optionnel)
```json
{
    "default_settings": {
        "framework": "tkinter",
        "theme": "modern",
        "auto_detect_gui": true,
        "include_console": false,
        "one_file": true,
        "debug_mode": false
    },
    "paths": {
        "upload_folder": "uploads",
        "output_folder": "output",
        "templates_folder": "templates"
    },
    "web_interface": {
        "host": "127.0.0.1",
        "port": 5000,
        "debug": false
    },
    "logging": {
        "level": "INFO",
        "file": "converter.log"
    }
}
```

#### Variables d'Environnement (Optionnel)

**Windows (Invite de commandes):**
```cmd
set CONVERTER_UPLOAD_DIR=C:\MonProjetConverter\uploads
set CONVERTER_OUTPUT_DIR=C:\MonProjetConverter\output
set CONVERTER_LOG_LEVEL=DEBUG
```

**Windows (PowerShell):**
```powershell
$env:CONVERTER_UPLOAD_DIR="C:\MonProjetConverter\uploads"
$env:CONVERTER_OUTPUT_DIR="C:\MonProjetConverter\output"
$env:CONVERTER_LOG_LEVEL="DEBUG"
```

**Linux/macOS (.bashrc ou .zshrc):**
```bash
export CONVERTER_UPLOAD_DIR="$HOME/converter/uploads"
export CONVERTER_OUTPUT_DIR="$HOME/converter/output"
export CONVERTER_LOG_LEVEL="INFO"
```

### Permissions et Sécurité

#### Windows
```cmd
# Vérifier les permissions du dossier
icacls script-to-desktop-converter

# Donner les permissions complètes si nécessaire
icacls script-to-desktop-converter /grant %USERNAME%:F /T
```

#### Linux/macOS
```bash
# Permissions appropriées
chmod 755 Script_to_code_DesktopApp_and_to_exe.py
chmod -R 755 ./

# Créer les répertoires avec bonnes permissions
mkdir -p uploads output templates static
chmod 755 uploads output templates static
```

## 🔌 Dépendances Optionnelles

### PyInstaller (Construction d'Exécutables)

**Installation:**
```bash
pip install pyinstaller
```

**Test:**
```bash
pyinstaller --version
```

**Problèmes courants:**
- **Windows**: Antivirus peut bloquer PyInstaller
- **macOS**: Peut nécessiter les outils de développement Xcode
- **Linux**: Peut nécessiter des bibliothèques de développement

### UPX (Compression)

UPX permet de réduire la taille des exécutables générés.

#### Windows
```bash
# Avec Chocolatey
choco install upx

# Ou téléchargement manuel depuis https://upx.github.io/
# Extraire dans un dossier et ajouter au PATH
```

#### macOS
```bash
# Avec Homebrew
brew install upx
```

#### Linux
```bash
# Ubuntu/Debian
sudo apt install upx-ucl

# CentOS/Fedora
sudo yum install upx  # CentOS
sudo dnf install upx  # Fedora
```

**Vérification:**
```bash
upx --version
```

### PyQt5/PyQt6 (Interfaces Avancées)

#### PyQt5
```bash
# Installation
pip install PyQt5

# Test
python -c "from PyQt5.QtWidgets import QApplication; print('PyQt5 OK')"
```

#### PyQt6
```bash
# Installation
pip install PyQt6

# Test
python -c "from PyQt6.QtWidgets import QApplication; print('PyQt6 OK')"
```

**Note:** PyQt5 et PyQt6 peuvent coexister, mais le convertisseur détectera automatiquement lequel utiliser.

### Dépendances de Développement (Optionnel)

```bash
# Outils de test et qualité de code
pip install pytest black flake8 mypy

# Outils de documentation
pip install sphinx sphinx-rtd-theme

# Outils de débogage
pip install pdb++ ipython
```

## ✅ Vérification de l'Installation

### Script de Vérification Automatique

Créer un fichier `test_installation.py`:

```python
#!/usr/bin/env python3
"""
Script de vérification de l'installation
"""

import sys
import os
import importlib
from pathlib import Path

def test_python_version():
    """Test de la version Python"""
    version = sys.version_info
    print(f"Python {version.major}.{version.minor}.{version.micro}")
    
    if version < (3, 7):
        print("❌ Python 3.7+ requis")
        return False
    else:
        print("✅ Version Python OK")
        return True

def test_module(name, optional=False):
    """Test d'un module Python"""
    try:
        module = importlib.import_module(name)
        version = getattr(module, '__version__', 'inconnue')
        print(f"✅ {name} {version}")
        return True
    except ImportError:
        if optional:
            print(f"⚠️  {name} (optionnel) - non installé")
            return True
        else:
            print(f"❌ {name} - REQUIS mais non installé")
            return False

def test_tkinter():
    """Test spécial pour Tkinter"""
    try:
        import tkinter as tk
        # Test création fenêtre
        root = tk.Tk()
        root.withdraw()  # Cacher la fenêtre
        root.destroy()
        print("✅ tkinter OK")
        return True
    except ImportError:
        print("❌ tkinter - Interface graphique non disponible")
        return False
    except Exception as e:
        print(f"⚠️  tkinter - Problème d'affichage: {e}")
        return True  # Peut fonctionner en mode serveur

def test_file_structure():
    """Test de la structure des fichiers"""
    required_files = [
        "Script_to_code_DesktopApp_and_to_exe.py",
        "requirements.txt"
    ]
    
    all_ok = True
    for file in required_files:
        if Path(file).exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - MANQUANT")
            all_ok = False
    
    return all_ok

def test_directories():
    """Test des répertoires"""
    dirs = ['uploads', 'output', 'templates', 'static']
    
    for dir_name in dirs:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"✅ {dir_name}/ existe")
        else:
            print(f"ℹ️  {dir_name}/ - sera créé automatiquement")

def test_permissions():
    """Test des permissions"""
    try:
        # Test écriture
        test_file = Path("test_permissions.tmp")
        test_file.write_text("test")
        test_file.unlink()
        print("✅ Permissions d'écriture OK")
        return True
    except Exception as e:
        print(f"❌ Permissions d'écriture: {e}")
        return False

def main():
    """Test principal"""
    print("🔍 VÉRIFICATION DE L'INSTALLATION")
    print("=" * 50)
    
    tests = []
    
    # Tests essentiels
    print("\n📋 Tests essentiels:")
    tests.append(test_python_version())
    tests.append(test_tkinter())
    tests.append(test_module('flask'))
    tests.append(test_module('sqlite3'))
    tests.append(test_file_structure())
    tests.append(test_permissions())
    
    # Tests optionnels
    print("\n🔧 Tests optionnels:")
    test_module('pyinstaller', optional=True)
    test_module('PyQt5', optional=True)
    test_module('PyQt6', optional=True)
    test_module('requests', optional=True)
    
    # Structure
    print("\n📁 Structure des répertoires:")
    test_directories()
    
    # Résultat final
    print("\n" + "=" * 50)
    if all(tests):
        print("🎉 INSTALLATION COMPLÈTE ET FONCTIONNELLE!")
        print("\nCommandes pour démarrer:")
        print("  Interface graphique: python Script_to_code_DesktopApp_and_to_exe.py --gui")
        print("  Interface web:       python Script_to_code_DesktopApp_and_to_exe.py --web")
        print("  Aide complète:       python Script_to_code_DesktopApp_and_to_exe.py --help")
        return 0
    else:
        print("❌ INSTALLATION INCOMPLÈTE")
        print("\nVeuillez résoudre les problèmes mentionnés ci-dessus.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

### Exécution du Test
```bash
python test_installation.py
```

### Tests Manuels

#### Test Interface Graphique
```bash
python Script_to_code_DesktopApp_and_to_exe.py --gui
```
- Une fenêtre Tkinter doit s'ouvrir
- Tous les onglets doivent être accessibles
- Pas d'erreur dans la console

#### Test Interface Web
```bash
python Script_to_code_DesktopApp_and_to_exe.py --web
```
- Le serveur doit démarrer sur http://localhost:5000
- La page d'accueil doit s'afficher correctement
- L'upload de fichiers doit fonctionner

#### Test Ligne de Commande
```bash
python Script_to_code_DesktopApp_and_to_exe.py --help
```
- L'aide complète doit s'afficher
- Toutes les options doivent être listées

## 🔧 Dépannage

### Problèmes Courants

#### 1. "python n'est pas reconnu" (Windows)

**Erreur:**
```
'python' n'est pas reconnu en tant que commande interne ou externe
```

**Solutions:**
1. **Réinstaller Python** avec "Add to PATH" coché
2. **Ajouter manuellement au PATH**:
   - Ouvrir "Variables d'environnement système"
   - Ajouter `C:\Users\VotreNom\AppData\Local\Programs\Python\Python39\`
   - Ajouter `C:\Users\VotreNom\AppData\Local\Programs\Python\Python39\Scripts\`
3. **Utiliser `py` au lieu de `python`**:
   ```cmd
   py --version
   py -m pip install -r requirements.txt
   ```

#### 2. Erreur Tkinter Linux

**Erreur:**
```
ImportError: No module named '_tkinter'
```

**Solution:**
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# CentOS/RHEL
sudo yum install tkinter

# Fedora
sudo dnf install python3-tkinter
```

#### 3. Erreur Permissions (Windows)

**Erreur:**
```
[Errno 13] Permission denied
```

**Solutions:**
1. **Exécuter en tant qu'administrateur**
2. **Désactiver temporairement l'antivirus**
3. **Ajouter une exception antivirus** pour le dossier du projet
4. **Modifier les permissions**:
   ```cmd
   icacls . /grant %USERNAME%:F /T
   ```

#### 4. PyInstaller Bloqué par Antivirus

**Problème:** L'antivirus détecte PyInstaller comme malware

**Solutions:**
1. **Ajouter exception** pour PyInstaller dans l'antivirus
2. **Ajouter exception** pour le dossier de sortie
3. **Utiliser Windows Defender** exclusivement (désactiver autres antivirus)
4. **Compiler sur une machine propre** sans antivirus trop agressif

#### 5. Erreur d'Import Flask

**Erreur:**
```
ModuleNotFoundError: No module named 'flask'
```

**Solutions:**
1. **Vérifier l'environnement virtuel**:
   ```bash
   # Activer l'environnement
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   
   # Vérifier
   which python
   ```

2. **Réinstaller Flask**:
   ```bash
   pip uninstall flask
   pip install flask
   ```

#### 6. Port 5000 Occupé (Interface Web)

**Erreur:**
```
OSError: [Errno 98] Address already in use
```

**Solutions:**
1. **Changer de port**:
   ```bash
   python Script_to_code_DesktopApp_and_to_exe.py --web --port 8080
   ```

2. **Trouver et arrêter le processus**:
   ```bash
   # Linux/macOS
   lsof -ti:5000 | xargs kill
   
   # Windows
   netstat -ano | findstr :5000
   taskkill /PID <PID> /F
   ```

#### 7. Erreur Base de Données SQLite

**Erreur:**
```
sqlite3.OperationalError: database is locked
```

**Solutions:**
1. **Fermer toutes les instances** de l'application
2. **Supprimer le fichier de verrou**:
   ```bash
   rm converter.db-journal
   ```
3. **Sauvegarder et recréer la base**:
   ```bash
   cp converter.db converter.db.backup
   rm converter.db
   # Relancer l'application (recrée la base)
   ```

### Diagnostic Avancé

#### Logs Détaillés
```bash
# Activer les logs détaillés
python Script_to_code_DesktopApp_and_to_exe.py --verbose --log-file debug.log

# Consulter les logs
tail -f debug.log     # Linux/macOS
type debug.log        # Windows
```

#### Test de l'Environnement Python
```python
import sys
print("Python executable:", sys.executable)
print("Python path:", sys.path)
print("Platform:", sys.platform)

# Test des modules
modules = ['tkinter', 'flask', 'sqlite3', 'pathlib']
for module in modules:
    try:
        __import__(module)
        print(f"✅ {module}")
    except ImportError as e:
        print(f"❌ {module}: {e}")
```

#### Nettoyage Complet
```bash
# Supprimer l'environnement virtuel
rm -rf venv/          # Linux/macOS
rmdir /s venv\        # Windows

# Supprimer les fichiers temporaires
rm -rf __pycache__/ *.pyc *.pyo
rm -rf build/ dist/ *.spec

# Recréer l'environnement
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

## 🔄 Mise à Jour

### Mise à Jour du Code Source

#### Via Git
```bash
# Sauvegarder la configuration locale
cp config.json config.json.backup 2>/dev/null || true
cp converter.db converter.db.backup 2>/dev/null || true

# Mettre à jour le code
git fetch origin
git pull origin main

# Restaurer la configuration
cp config.json.backup config.json 2>/dev/null || true
cp converter.db.backup converter.db 2>/dev/null || true
```

#### Téléchargement Manuel
1. Télécharger la nouvelle version ZIP
2. Sauvegarder vos fichiers de configuration
3. Extraire dans un nouveau dossier
4. Copier vos fichiers de configuration sauvegardés
5. Réinstaller les dépendances

### Mise à Jour des Dépendances

```bash
# Activer l'environnement virtuel
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Mettre à jour pip
python -m pip install --upgrade pip

# Mettre à jour toutes les dépendances
pip install -r requirements.txt --upgrade

# Ou mise à jour sélective
pip install --upgrade flask pyinstaller

# Vérifier les versions
pip list --outdated
```

### Migration entre Versions

#### Sauvegarde avant Mise à Jour
```bash
# Créer un dossier de sauvegarde
mkdir backup_$(date +%Y%m%d)

# Sauvegarder les fichiers importants
cp converter.db backup_*/
cp config.json backup_*/ 2>/dev/null || true
cp -r uploads/ backup_*/ 2>/dev/null || true
cp -r output/ backup_*/ 2>/dev/null || true
```

#### Après Mise à Jour
1. **Tester l'application** avec quelques projets simples
2. **Vérifier la base de données** - les projets doivent être présents
3. **Tester toutes interfaces** (GUI, Web, CLI)
4. **Supprimer les sauvegardes** si tout fonctionne

## 🗑️ Désinstallation

### Désinstallation Complète

#### 1. Sauvegarder les Données (Optionnel)
```bash
# Exporter les projets
python Script_to_code_DesktopApp_and_to_exe.py --list-projects
# Sauvegarder manuellement les projets importants

# Copier les fichiers de sortie importants
cp -r output/ ~/mes_executables_sauvegardes/
```

#### 2. Supprimer l'Environnement Virtuel
```bash
# Désactiver l'environnement
deactivate

# Supprimer le dossier
rm -rf venv/          # Linux/macOS
rmdir /s venv\        # Windows
```

#### 3. Supprimer le Projet
```bash
# Supprimer tout le dossier du projet
cd ..
rm -rf script-to-desktop-converter/    # Linux/macOS
rmdir /s script-to-desktop-converter\  # Windows
```

#### 4. Nettoyage Variables d'Environnement
Supprimer les variables d'environnement créées:
- `CONVERTER_UPLOAD_DIR`
- `CONVERTER_OUTPUT_DIR`
- `CONVERTER_LOG_LEVEL`
- etc.

### Désinstallation Partielle (Garder les Données)

```bash
# Garder seulement les données
mkdir mes_donnees_converter
cp converter.db mes_donnees_converter/
cp -r uploads/ mes_donnees_converter/
cp -r output/ mes_donnees_converter/

# Supprimer le reste
rm -rf venv/ templates/ static/ *.py *.log
```

### Vérification de la Désinstallation

```bash
# Vérifier qu'aucun processus ne tourne
ps aux | grep -i converter    # Linux/macOS
tasklist | findstr converter  # Windows

# Vérifier les ports
netstat -an | grep :5000

# Supprimer les fichiers temporaires système
rm -rf ~/.cache/pyinstaller   # Linux/macOS
# Windows: %LocalAppData%\pyinstaller
```

---

## 🎯 Résumé des Commandes Essentielles

### Installation Complète (Copier-Coller)

**Windows:**
```cmd
git clone https://github.com/votre-username/script-to-desktop-converter.git
cd script-to-desktop-converter
python -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python test_installation.py
```

**Linux/macOS:**
```bash
git clone https://github.com/votre-username/script-to-desktop-converter.git
cd script-to-desktop-converter
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python test_installation.py
```

### Lancement Rapide
```bash
# Interface graphique
python Script_to_code_DesktopApp_and_to_exe.py --gui

# Interface web
python Script_to_code_DesktopApp_and_to_exe.py --web

# Aide
python Script_to_code_DesktopApp_and_to_exe.py --help
```

L'installation est maintenant terminée! Consultez le [Guide d'Utilisation](HOW_TO_USE.md) pour commencer à convertir vos scripts.
