# Documentation Complète - Script to Desktop App Converter

## 📖 Table des Matières

1. [Vue d'Ensemble](#vue-densemble)
2. [Installation et Configuration](#installation-et-configuration)
3. [Interface Utilisateur](#interface-utilisateur)
4. [Workflow de Conversion](#workflow-de-conversion)
5. [Options de Configuration](#options-de-configuration)
6. [Templates Disponibles](#templates-disponibles)
7. [Analyse de Code](#analyse-de-code)
8. [Build et Exécutable](#build-et-exécutable)
9. [Gestion des Projets](#gestion-des-projets)
10. [API Endpoints](#api-endpoints)

---

## Vue d'Ensemble

Le **Script to Desktop App Converter** est une application web Flask qui automatise la conversion de scripts Python en applications de bureau exécutables. Elle combine l'analyse statique de code, la génération de templates et PyInstaller pour créer des applications autonomes.

### Caractéristiques Principales

- **Analyse Intelligente** : Utilise l'AST Python pour analyser le code
- **Templates Multiples** : Support Tkinter, PyQt5/6, Flask, Console
- **Interface Web** : Interface moderne avec Bootstrap 5
- **Persistance** : Base de données SQLite pour les projets
- **Build Automatique** : Intégration PyInstaller complète

---

## Installation et Configuration

### Prérequis

```bash
# Python 3.7 ou supérieur
python --version

# Pip pour l'installation des packages
pip --version
```

### Installation

1. **Dépendances Python**
```bash
pip install flask
pip install pyinstaller
# sqlite3 est inclus avec Python
# ast est inclus avec Python
```

2. **Structure des Dossiers**
```bash
# Créer la structure si nécessaire
mkdir -p script_converter/templates
mkdir -p script_converter/static/css
mkdir -p script_converter/static/js
mkdir -p script_converter/examples
```

3. **Lancement**
```bash
cd script_converter
python app.py
```

### Configuration Initiale

L'application crée automatiquement :
- Base de données SQLite (`projects.db`)
- Dossiers temporaires pour les builds
- Configuration par défaut

---

## Interface Utilisateur

### Page d'Accueil (`/`)

**Fonctionnalités :**
- Liste des projets récents
- Statistiques de conversion
- Accès rapide aux fonctions principales

**Éléments d'Interface :**
```html
<!-- Navigation principale -->
<nav class="navbar navbar-expand-lg navbar-dark bg-primary">
  <!-- Logo et menu -->
</nav>

<!-- Dashboard des projets -->
<div class="container mt-4">
  <!-- Cartes de projets récents -->
  <!-- Boutons d'action rapide -->
</div>
```

### Page Upload (`/upload`)

**Fonctionnalités :**
- Upload de fichiers Python (.py)
- Validation en temps réel
- Prévisualisation du code

**Validation JavaScript :**
```javascript
function validateFile(file) {
    if (!file.name.endsWith('.py')) {
        showError('Seuls les fichiers .py sont acceptés');
        return false;
    }
    if (file.size > 10 * 1024 * 1024) { // 10MB
        showError('Fichier trop volumineux (max 10MB)');
        return false;
    }
    return true;
}
```

### Page Configuration (`/project/<id>`)

**Sections Principales :**
1. **Informations Projet** : Nom, description, type
2. **Options Build** : PyInstaller, console/windowed, icône
3. **Dépendances** : Liste auto-détectée et manuelle
4. **Aperçu Code** : Code généré selon le template

---

## Workflow de Conversion

### 1. Upload et Analyse

```python
# Processus d'analyse automatique
def analyze_uploaded_file(file_path):
    analyzer = CodeAnalyzer()
    
    # Analyse AST
    ast_info = analyzer.analyze_file(file_path)
    
    # Détection dépendances
    dependencies = analyzer.extract_dependencies(file_path)
    
    # Validation syntaxe
    syntax_valid = analyzer.validate_syntax(file_path)
    
    return {
        'ast_info': ast_info,
        'dependencies': dependencies,
        'valid': syntax_valid
    }
```

### 2. Sélection Template

**Types Disponibles :**
- **Console** : Applications en ligne de commande
- **Tkinter** : Interface graphique native
- **PyQt5/PyQt6** : Interface graphique avancée
- **Flask** : Applications web

### 3. Configuration Projet

**Paramètres Essentiels :**
```json
{
  "project_name": "Mon Application",
  "template_type": "tkinter",
  "build_options": {
    "console": false,
    "onedir": false,
    "icon": "app_icon.ico",
    "additional_files": []
  },
  "dependencies": ["tkinter", "json", "os"]
}
```

### 4. Génération Code

Le générateur crée un code structuré selon le template choisi :

```python
# Exemple génération Tkinter
def generate_tkinter_template(original_code, config):
    template = f'''
import tkinter as tk
from tkinter import ttk, messagebox
import {', '.join(config['dependencies'])}

class {config['class_name']}:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("{config['app_name']}")
        self.setup_ui()
        
        # Code original intégré
        {self.integrate_original_code(original_code)}
    
    def setup_ui(self):
        # Interface utilisateur générée
        pass
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = {config['class_name']}()
    app.run()
'''
    return template
```

### 5. Build Exécutable

```python
# Configuration PyInstaller
def create_pyinstaller_spec(project_config):
    spec_content = f'''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['{project_config['main_file']}'],
    pathex=[],
    binaries=[],
    datas={project_config.get('data_files', [])},
    hiddenimports={project_config.get('hidden_imports', [])},
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{project_config['exe_name']}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console={str(project_config.get('console', True)).lower()},
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='{project_config.get('icon_path', '')}',
)
'''
    return spec_content
```

---

## Options de Configuration

### Options de Build

| Option | Description | Valeur par défaut |
|--------|-------------|-------------------|
| `console` | Afficher console | `True` |
| `onedir` | Dossier ou fichier unique | `False` |
| `icon` | Chemin vers icône .ico | `None` |
| `name` | Nom de l'exécutable | Script original |
| `paths` | Chemins additionnels | `[]` |

### Options Template

**Tkinter :**
```python
tkinter_options = {
    'window_size': '800x600',
    'resizable': True,
    'theme': 'clam',
    'menu_bar': True
}
```

**PyQt5/6 :**
```python
pyqt_options = {
    'style': 'Fusion',
    'window_flags': 'Qt.Window',
    'layout_type': 'QVBoxLayout'
}
```

**Flask :**
```python
flask_options = {
    'host': '0.0.0.0',
    'port': 5000,
    'debug': False,
    'templates_folder': 'templates'
}
```

---

## Templates Disponibles

### 1. Template Console

**Structure :**
```python
class ConsoleApp:
    def __init__(self):
        self.running = True
        
    def show_menu(self):
        # Menu principal
        
    def handle_input(self):
        # Gestion entrées utilisateur
        
    def run(self):
        # Boucle principale
```

### 2. Template Tkinter

**Structure :**
```python
class TkinterApp:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_ui()
        
    def setup_ui(self):
        # Configuration interface
        
    def create_menu(self):
        # Barre de menu
        
    def run(self):
        self.root.mainloop()
```

### 3. Template PyQt

**Structure :**
```python
class PyQtApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        # Configuration interface
        
    def create_actions(self):
        # Actions et menus
```

### 4. Template Flask

**Structure :**
```python
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run()
```

---

## Analyse de Code

### Analyseur AST

```python
class CodeAnalyzer:
    def analyze_file(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        tree = ast.parse(content)
        
        analysis = {
            'functions': self.extract_functions(tree),
            'classes': self.extract_classes(tree),
            'imports': self.extract_imports(tree),
            'globals': self.extract_globals(tree)
        }
        
        return analysis
```

### Détection Dépendances

**Imports Standards :**
```python
def extract_dependencies(self, file_path):
    dependencies = set()
    
    # Analyse imports
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                dependencies.add(alias.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                dependencies.add(node.module.split('.')[0])
    
    return list(dependencies)
```

### Validation Syntaxe

```python
def validate_syntax(self, file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            compile(f.read(), file_path, 'exec')
        return True, None
    except SyntaxError as e:
        return False, str(e)
```

---

## Build et Exécutable

### Processus PyInstaller

1. **Génération Spec**
2. **Analysis des dépendances**
3. **Compilation**
4. **Packaging**

### Commandes Build

```bash
# Build onefile
pyinstaller --onefile --noconsole script.py

# Build avec icône
pyinstaller --onefile --noconsole --icon=app.ico script.py

# Build avec données
pyinstaller --onefile --add-data "data;data" script.py
```

### Optimisation Taille

**Exclusions communes :**
```python
excludes = [
    'matplotlib', 'numpy', 'scipy',  # Si non utilisés
    'tkinter',  # Si PyQt utilisé
    'PyQt5',  # Si Tkinter utilisé
]
```

---

## Gestion des Projets

### Base de Données

**Schema SQLite :**
```sql
CREATE TABLE projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    template_type TEXT NOT NULL,
    file_path TEXT NOT NULL,
    config TEXT NOT NULL,  -- JSON config
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE build_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER,
    build_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    success BOOLEAN,
    output_path TEXT,
    error_message TEXT,
    FOREIGN KEY (project_id) REFERENCES projects (id)
);
```

### Operations CRUD

```python
class DatabaseManager:
    def create_project(self, name, template_type, file_path, config):
        # Création nouveau projet
        
    def get_project(self, project_id):
        # Récupération projet
        
    def update_project(self, project_id, **kwargs):
        # Mise à jour projet
        
    def delete_project(self, project_id):
        # Suppression projet
        
    def list_projects(self):
        # Liste tous projets
```

---

## API Endpoints

### Routes Principales

| Méthode | Route | Description |
|---------|-------|-------------|
| `GET` | `/` | Page d'accueil |
| `GET/POST` | `/upload` | Upload de fichier |
| `GET` | `/project/<id>` | Configuration projet |
| `POST` | `/api/analyze` | Analyse de code |
| `POST` | `/api/build` | Build exécutable |
| `GET` | `/api/projects` | Liste projets |
| `DELETE` | `/api/project/<id>` | Suppression projet |

### API Responses

**Analyse Code :**
```json
{
  "success": true,
  "data": {
    "functions": ["main", "calculate", "display"],
    "classes": ["Calculator"],
    "imports": ["math", "os", "sys"],
    "dependencies": ["math", "os", "sys"],
    "syntax_valid": true
  }
}
```

**Build Status :**
```json
{
  "success": true,
  "build_id": "build_123",
  "status": "completed",
  "output_path": "/builds/MyApp.exe",
  "size": "5.2 MB",
  "duration": "45 seconds"
}
```

---

## Exemples d'Utilisation

### Conversion Script Simple

1. **Upload** `simple_calculator.py`
2. **Template** : Console
3. **Build** : OneFile, No Console
4. **Résultat** : `calculator.exe` (3.5 MB)

### Conversion Application GUI

1. **Upload** `tkinter_todo_app.py`
2. **Template** : Tkinter (détecté automatiquement)
3. **Options** : Icône personnalisée, No Console
4. **Résultat** : `TodoManager.exe` (8.2 MB)

### Conversion App Web

1. **Upload** `flask_web_app.py`
2. **Template** : Flask (détecté automatiquement)
3. **Données** : Templates HTML intégrés
4. **Résultat** : `WebBlog.exe` (12.8 MB)

---

Cette documentation couvre tous les aspects de l'utilisation du **Script to Desktop App Converter**. Pour des guides spécifiques par exemple, consultez [examples_guide.md](examples_guide.md).
