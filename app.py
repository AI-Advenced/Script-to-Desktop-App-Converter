#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script_to_code_DesktopApp_and_to_exe.py
Convertisseur de scripts Python vers applications de bureau GUI
Système complet avec Flask, templates et conversion en .exe
Auteur: Assistant IA
Version: 2.0
"""

import os
import sys
import json
import subprocess
import shutil
import tempfile
import zipfile
import base64
import hashlib
import threading
import time
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import argparse
import logging
from dataclasses import dataclass, asdict
import importlib.util
import ast
import re
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import requests
from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for, session
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from contextlib import contextmanager

# Configuration globale
UPLOAD_FOLDER = 'uploads'
TEMPLATES_FOLDER = 'templates'
STATIC_FOLDER = 'static'
OUTPUT_FOLDER = 'output'
DATABASE_PATH = 'converter.db'
ALLOWED_EXTENSIONS = {'.py', '.pyw'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

# Configuration des logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('converter.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ProjectConfig:
    """Configuration d'un projet de conversion"""
    name: str
    description: str
    author: str
    version: str
    gui_framework: str = "tkinter"
    theme: str = "default"
    icon_path: Optional[str] = None
    requirements: List[str] = None
    entry_point: str = "main.py"
    output_type: str = "exe"
    architecture: str = "x64"
    include_console: bool = False
    one_file: bool = True
    upx_compress: bool = False
    debug_mode: bool = False
    created_at: str = ""
    
    def __post_init__(self):
        if self.requirements is None:
            self.requirements = []
        if not self.created_at:
            self.created_at = datetime.now().isoformat()

class DatabaseManager:
    """Gestionnaire de base de données SQLite"""
    
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialise la base de données"""
        with self.get_connection() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    config TEXT NOT NULL,
                    source_code TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS conversion_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER,
                    status TEXT NOT NULL,
                    log_output TEXT,
                    output_path TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES projects (id)
                );
                
                CREATE INDEX IF NOT EXISTS idx_projects_name ON projects(name);
                CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
                CREATE INDEX IF NOT EXISTS idx_conversion_history_project_id ON conversion_history(project_id);
            """)
    
    @contextmanager
    def get_connection(self):
        """Context manager pour les connexions à la base de données"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Erreur base de données: {e}")
            raise
        finally:
            conn.close()
    
    def save_project(self, config: ProjectConfig, source_code: str = "") -> int:
        """Sauvegarde un projet"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT OR REPLACE INTO projects (name, config, source_code, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            """, (config.name, json.dumps(asdict(config)), source_code))
            return cursor.lastrowid
    
    def load_project(self, name: str) -> Optional[Tuple[ProjectConfig, str]]:
        """Charge un projet"""
        with self.get_connection() as conn:
            row = conn.execute("""
                SELECT config, source_code FROM projects WHERE name = ?
            """, (name,)).fetchone()
            
            if row:
                config_dict = json.loads(row['config'])
                config = ProjectConfig(**config_dict)
                return config, row['source_code']
            return None
    
    def list_projects(self) -> List[Dict]:
        """Liste tous les projets"""
        with self.get_connection() as conn:
            rows = conn.execute("""
                SELECT name, created_at, updated_at FROM projects 
                ORDER BY updated_at DESC
            """).fetchall()
            return [dict(row) for row in rows]
    
    def delete_project(self, name: str) -> bool:
        """Supprime un projet"""
        with self.get_connection() as conn:
            cursor = conn.execute("DELETE FROM projects WHERE name = ?", (name,))
            return cursor.rowcount > 0

class CodeAnalyzer:
    """Analyseur de code Python pour extraire les informations"""
    
    def __init__(self):
        self.imports = set()
        self.functions = []
        self.classes = []
        self.variables = []
        self.gui_indicators = []
    
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Analyse un fichier Python"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            self._analyze_node(tree)
            
            return {
                'imports': list(self.imports),
                'functions': self.functions,
                'classes': self.classes,
                'variables': self.variables,
                'gui_framework': self._detect_gui_framework(),
                'complexity': self._calculate_complexity(tree),
                'lines_of_code': len(content.splitlines()),
                'gui_indicators': self.gui_indicators
            }
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse du fichier {file_path}: {e}")
            return {}
    
    def _analyze_node(self, node):
        """Analyse récursive des nœuds AST"""
        if isinstance(node, ast.Import):
            for alias in node.names:
                self.imports.add(alias.name)
        
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                self.imports.add(node.module)
                # Détection d'indicateurs GUI
                if node.module in ['tkinter', 'PyQt5', 'PyQt6', 'PySide2', 'PySide6', 'kivy']:
                    self.gui_indicators.append(node.module)
        
        elif isinstance(node, ast.FunctionDef):
            self.functions.append({
                'name': node.name,
                'line': node.lineno,
                'args': [arg.arg for arg in node.args.args],
                'decorators': [d.id if isinstance(d, ast.Name) else str(d) for d in node.decorator_list]
            })
        
        elif isinstance(node, ast.ClassDef):
            self.classes.append({
                'name': node.name,
                'line': node.lineno,
                'bases': [base.id if isinstance(base, ast.Name) else str(base) for base in node.bases],
                'methods': []
            })
        
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.variables.append({
                        'name': target.id,
                        'line': node.lineno
                    })
        
        # Récursion sur les nœuds enfants
        for child in ast.iter_child_nodes(node):
            self._analyze_node(child)
    
    def _detect_gui_framework(self) -> str:
        """Détecte le framework GUI utilisé"""
        gui_frameworks = {
            'tkinter': ['tkinter', 'Tkinter'],
            'PyQt5': ['PyQt5'],
            'PyQt6': ['PyQt6'],
            'PySide2': ['PySide2'],
            'PySide6': ['PySide6'],
            'kivy': ['kivy'],
            'wxPython': ['wx', 'wxPython'],
            'pygame': ['pygame'],
            'flask': ['flask'],
            'django': ['django'],
            'fastapi': ['fastapi']
        }
        
        for framework, modules in gui_frameworks.items():
            if any(module in self.imports for module in modules):
                return framework
        
        return "console"
    
    def _calculate_complexity(self, tree) -> int:
        """Calcule la complexité cyclomatique"""
        complexity = 1  # Base complexity
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor, ast.comprehension)):
                complexity += 1
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        
        return complexity

class TemplateGenerator:
    """Générateur de templates pour différents frameworks GUI"""
    
    def __init__(self):
        self.templates = {
            'tkinter': self._generate_tkinter_template,
            'PyQt5': self._generate_pyqt5_template,
            'PyQt6': self._generate_pyqt6_template,
            'flask': self._generate_flask_template,
            'console': self._generate_console_template
        }
    
    def generate_gui_wrapper(self, original_code: str, config: ProjectConfig) -> str:
        """Génère un wrapper GUI pour le code original"""
        framework = config.gui_framework
        if framework in self.templates:
            return self.templates[framework](original_code, config)
        else:
            return self._generate_tkinter_template(original_code, config)
    
    def _generate_tkinter_template(self, original_code: str, config: ProjectConfig) -> str:
        """Template Tkinter"""
        return f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
{config.name} - Application de bureau générée automatiquement
Généré le: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Auteur: {config.author}
Version: {config.version}
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import sys
import os
import threading
import subprocess
from io import StringIO
import traceback

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # Configuration de la fenêtre principale
        self.title("{config.name} v{config.version}")
        self.geometry("1000x700")
        self.minsize(800, 600)
        
        # Variables
        self.output_buffer = StringIO()
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        
        # Interface utilisateur
        self.setup_ui()
        self.setup_menus()
        
        # Redirection de la sortie
        self.redirect_output()
        
        # Protocole de fermeture
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_ui(self):
        """Configure l'interface utilisateur"""
        # Frame principal
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padding=10)
        
        # Notebook pour les onglets
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Onglet Exécution
        self.execution_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.execution_frame, text="Exécution")
        self.setup_execution_tab()
        
        # Onglet Code Source
        self.code_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.code_frame, text="Code Source")
        self.setup_code_tab()
        
        # Onglet Sortie
        self.output_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.output_frame, text="Sortie Console")
        self.setup_output_tab()
        
        # Onglet À propos
        self.about_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.about_frame, text="À propos")
        self.setup_about_tab()
    
    def setup_execution_tab(self):
        """Configure l'onglet d'exécution"""
        # Boutons de contrôle
        control_frame = ttk.Frame(self.execution_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.run_button = ttk.Button(control_frame, text="▶ Exécuter", 
                                   command=self.run_original_code, style="Accent.TButton")
        self.run_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.stop_button = ttk.Button(control_frame, text="⏹ Arrêter", 
                                    command=self.stop_execution, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.clear_button = ttk.Button(control_frame, text="🗑 Vider", 
                                     command=self.clear_output)
        self.clear_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Barre de progression
        self.progress = ttk.Progressbar(control_frame, mode='indeterminate')
        self.progress.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))
        
        # Zone de saisie des paramètres
        params_frame = ttk.LabelFrame(self.execution_frame, text="Paramètres d'entrée")
        params_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.params_entry = ttk.Entry(params_frame, font=("Consolas", 10))
        self.params_entry.pack(fill=tk.X, padx=5, pady=5)
        
        # Zone d'affichage des résultats
        result_frame = ttk.LabelFrame(self.execution_frame, text="Résultats")
        result_frame.pack(fill=tk.BOTH, expand=True)
        
        self.result_text = scrolledtext.ScrolledText(result_frame, wrap=tk.WORD, 
                                                   font=("Consolas", 10))
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def setup_code_tab(self):
        """Configure l'onglet du code source"""
        # Toolbar
        toolbar_frame = ttk.Frame(self.code_frame)
        toolbar_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(toolbar_frame, text="📁 Ouvrir", 
                  command=self.open_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar_frame, text="💾 Sauvegarder", 
                  command=self.save_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar_frame, text="🔄 Actualiser", 
                  command=self.refresh_code).pack(side=tk.LEFT, padx=(0, 5))
        
        # Éditeur de code
        self.code_text = scrolledtext.ScrolledText(self.code_frame, wrap=tk.NONE, 
                                                 font=("Consolas", 10))
        self.code_text.pack(fill=tk.BOTH, expand=True)
        
        # Insertion du code original
        self.code_text.insert(tk.END, self.get_original_code())
        
    def setup_output_tab(self):
        """Configure l'onglet de sortie console"""
        # Contrôles
        output_control_frame = ttk.Frame(self.output_frame)
        output_control_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(output_control_frame, text="🗑 Vider Console", 
                  command=self.clear_console).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(output_control_frame, text="💾 Sauvegarder Log", 
                  command=self.save_log).pack(side=tk.LEFT, padx=(0, 5))
        
        # Console
        self.console_text = scrolledtext.ScrolledText(self.output_frame, wrap=tk.WORD, 
                                                    font=("Consolas", 9), bg="black", fg="green")
        self.console_text.pack(fill=tk.BOTH, expand=True)
    
    def setup_about_tab(self):
        """Configure l'onglet À propos"""
        about_text = f'''
{config.name}
Version: {config.version}
Auteur: {config.author}
Description: {config.description}

Généré automatiquement par Script_to_code_DesktopApp_and_to_exe.py
Date de génération: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

Framework GUI: Tkinter
Architecture: {config.architecture}
Mode Debug: {"Activé" if config.debug_mode else "Désactivé"}

© {datetime.now().year} - Tous droits réservés
        '''
        
        about_label = tk.Label(self.about_frame, text=about_text, justify=tk.LEFT, 
                             font=("Segoe UI", 10), wraplength=600)
        about_label.pack(expand=True, padx=20, pady=20)
    
    def setup_menus(self):
        """Configure les menus"""
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        
        # Menu Fichier
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Fichier", menu=file_menu)
        file_menu.add_command(label="Nouveau", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Ouvrir...", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Sauvegarder", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Quitter", command=self.on_closing, accelerator="Ctrl+Q")
        
        # Menu Exécution
        run_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Exécution", menu=run_menu)
        run_menu.add_command(label="Exécuter", command=self.run_original_code, accelerator="F5")
        run_menu.add_command(label="Arrêter", command=self.stop_execution, accelerator="Ctrl+C")
        run_menu.add_separator()
        run_menu.add_command(label="Vider sortie", command=self.clear_output)
        
        # Menu Aide
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Aide", menu=help_menu)
        help_menu.add_command(label="Documentation", command=self.show_help)
        help_menu.add_command(label="À propos", command=self.show_about)
        
        # Raccourcis clavier
        self.bind('<Control-n>', lambda e: self.new_file())
        self.bind('<Control-o>', lambda e: self.open_file())
        self.bind('<Control-s>', lambda e: self.save_file())
        self.bind('<Control-q>', lambda e: self.on_closing())
        self.bind('<F5>', lambda e: self.run_original_code())
        self.bind('<Control-c>', lambda e: self.stop_execution())
    
    def redirect_output(self):
        """Redirige stdout et stderr vers l'interface"""
        sys.stdout = self
        sys.stderr = self
    
    def write(self, text):
        """Méthode pour rediriger la sortie"""
        self.console_text.insert(tk.END, text)
        self.console_text.see(tk.END)
        self.console_text.update()
    
    def flush(self):
        """Méthode flush pour la compatibilité"""
        pass
    
    def get_original_code(self):
        """Retourne le code original"""
        return '''# Code original intégré
{original_code}
'''
    
    def run_original_code(self):
        """Exécute le code original"""
        if hasattr(self, 'execution_thread') and self.execution_thread.is_alive():
            messagebox.showwarning("Attention", "Une exécution est déjà en cours!")
            return
        
        self.run_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.progress.start()
        
        # Lancement dans un thread séparé
        self.execution_thread = threading.Thread(target=self._execute_code, daemon=True)
        self.execution_thread.start()
    
    def _execute_code(self):
        """Exécute le code dans un thread séparé"""
        try:
            # Récupération du code à exécuter
            code = self.code_text.get(1.0, tk.END)
            
            # Paramètres d'entrée
            params = self.params_entry.get().strip()
            if params:
                sys.argv = ['main.py'] + params.split()
            
            # Redirection temporaire
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            
            # Exécution
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"=== Exécution démarrée à {{datetime.now().strftime('%H:%M:%S')}} ===\\n\\n")
            
            # Compilation et exécution
            compiled_code = compile(code, '<string>', 'exec')
            exec(compiled_code, {{'__name__': '__main__'}})
            
            self.result_text.insert(tk.END, f"\\n\\n=== Exécution terminée à {{datetime.now().strftime('%H:%M:%S')}} ===")
            
        except Exception as e:
            error_msg = f"Erreur lors de l'exécution:\\n{{str(e)}}\\n\\n{{traceback.format_exc()}}"
            self.result_text.insert(tk.END, error_msg)
            print(error_msg)
        
        finally:
            # Restauration des flux
            sys.stdout = old_stdout if 'old_stdout' in locals() else sys.stdout
            sys.stderr = old_stderr if 'old_stderr' in locals() else sys.stderr
            
            # Mise à jour de l'interface
            self.after(0, self._execution_finished)
    
    def _execution_finished(self):
        """Appelé quand l'exécution est terminée"""
        self.run_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.progress.stop()
    
    def stop_execution(self):
        """Arrête l'exécution en cours"""
        if hasattr(self, 'execution_thread') and self.execution_thread.is_alive():
            # Note: Il n'est pas possible d'arrêter proprement un thread en Python
            # Cette fonctionnalité nécessiterait une implémentation plus complexe
            messagebox.showinfo("Information", "L'arrêt forcé n'est pas implémenté.\\nVeuillez fermer l'application si nécessaire.")
        
        self._execution_finished()
    
    def clear_output(self):
        """Vide la zone de résultats"""
        self.result_text.delete(1.0, tk.END)
    
    def clear_console(self):
        """Vide la console"""
        self.console_text.delete(1.0, tk.END)
    
    def new_file(self):
        """Nouveau fichier"""
        if messagebox.askyesno("Nouveau", "Voulez-vous vraiment effacer le code actuel?"):
            self.code_text.delete(1.0, tk.END)
    
    def open_file(self):
        """Ouvre un fichier"""
        filename = filedialog.askopenfilename(
            title="Ouvrir un fichier Python",
            filetypes=[("Fichiers Python", "*.py"), ("Tous les fichiers", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self.code_text.delete(1.0, tk.END)
                self.code_text.insert(1.0, content)
                
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible d'ouvrir le fichier:\\n{{str(e)}}")
    
    def save_file(self):
        """Sauvegarde le fichier"""
        filename = filedialog.asksaveasfilename(
            title="Sauvegarder le code",
            defaultextension=".py",
            filetypes=[("Fichiers Python", "*.py"), ("Tous les fichiers", "*.*")]
        )
        
        if filename:
            try:
                content = self.code_text.get(1.0, tk.END)
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                messagebox.showinfo("Succès", f"Fichier sauvegardé: {{filename}}")
                
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible de sauvegarder le fichier:\\n{{str(e)}}")
    
    def save_log(self):
        """Sauvegarde le log de la console"""
        filename = filedialog.asksaveasfilename(
            title="Sauvegarder le log",
            defaultextension=".txt",
            filetypes=[("Fichiers texte", "*.txt"), ("Tous les fichiers", "*.*")]
        )
        
        if filename:
            try:
                content = self.console_text.get(1.0, tk.END)
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                messagebox.showinfo("Succès", f"Log sauvegardé: {{filename}}")
                
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible de sauvegarder le log:\\n{{str(e)}}")
    
    def refresh_code(self):
        """Actualise le code"""
        if messagebox.askyesno("Actualiser", "Voulez-vous restaurer le code original?"):
            self.code_text.delete(1.0, tk.END)
            self.code_text.insert(1.0, self.get_original_code())
    
    def show_help(self):
        """Affiche l'aide"""
        help_text = """
Aide - {config.name}

RACCOURCIS CLAVIER:
• Ctrl+N: Nouveau fichier
• Ctrl+O: Ouvrir un fichier
• Ctrl+S: Sauvegarder
• F5: Exécuter le code
• Ctrl+C: Arrêter l'exécution
• Ctrl+Q: Quitter

UTILISATION:
1. Modifiez le code dans l'onglet "Code Source"
2. Ajustez les paramètres d'entrée si nécessaire
3. Cliquez sur "Exécuter" pour lancer le code
4. Consultez les résultats dans l'onglet "Résultats"
5. Surveillez la console pour les messages système

CONSEILS:
• Utilisez l'onglet "Sortie Console" pour déboguer
• Sauvegardez régulièrement vos modifications
• Les paramètres d'entrée simulent sys.argv
        """
        
        help_window = tk.Toplevel(self)
        help_window.title("Aide")
        help_window.geometry("600x500")
        
        text_widget = scrolledtext.ScrolledText(help_window, wrap=tk.WORD, font=("Segoe UI", 10))
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert(1.0, help_text)
        text_widget.config(state=tk.DISABLED)
    
    def show_about(self):
        """Affiche la fenêtre À propos"""
        self.notebook.select(self.about_frame)
    
    def on_closing(self):
        """Gestionnaire de fermeture"""
        if messagebox.askokcancel("Quitter", "Voulez-vous vraiment quitter l'application?"):
            # Restauration des flux standards
            sys.stdout = self.original_stdout
            sys.stderr = self.original_stderr
            
            self.destroy()

# Code original à intégrer
original_code = """{original_code}"""

def main():
    """Point d'entrée principal"""
    try:
        app = Application()
        app.mainloop()
    except Exception as e:
        print(f"Erreur critique: {{e}}")
        import traceback
        traceback.print_exc()
        input("Appuyez sur Entrée pour fermer...")

if __name__ == "__main__":
    main()
'''
    
    def _generate_pyqt5_template(self, original_code: str, config: ProjectConfig) -> str:
        """Template PyQt5"""
        return f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
{config.name} - Application PyQt5 générée automatiquement
Généré le: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import threading
import traceback
from io import StringIO

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("{config.name} v{config.version}")
        self.setGeometry(100, 100, 1000, 700)
        
        # Interface utilisateur
        self.setup_ui()
        self.setup_menus()
    
    def setup_ui(self):
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        layout = QVBoxLayout(central_widget)
        
        # Onglets
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Onglet exécution
        self.execution_tab = QWidget()
        self.tab_widget.addTab(self.execution_tab, "Exécution")
        self.setup_execution_tab()
        
        # Onglet code
        self.code_tab = QWidget()
        self.tab_widget.addTab(self.code_tab, "Code Source")
        self.setup_code_tab()
        
        # Onglet sortie
        self.output_tab = QWidget()
        self.tab_widget.addTab(self.output_tab, "Sortie")
        self.setup_output_tab()
    
    def setup_execution_tab(self):
        layout = QVBoxLayout(self.execution_tab)
        
        # Boutons
        button_layout = QHBoxLayout()
        self.run_button = QPushButton("▶ Exécuter")
        self.run_button.clicked.connect(self.run_code)
        button_layout.addWidget(self.run_button)
        
        self.clear_button = QPushButton("🗑 Vider")
        self.clear_button.clicked.connect(self.clear_output)
        button_layout.addWidget(self.clear_button)
        
        layout.addLayout(button_layout)
        
        # Zone de résultats
        self.result_text = QTextEdit()
        self.result_text.setFont(QFont("Consolas", 10))
        layout.addWidget(self.result_text)
    
    def setup_code_tab(self):
        layout = QVBoxLayout(self.code_tab)
        
        # Éditeur de code
        self.code_editor = QTextEdit()
        self.code_editor.setFont(QFont("Consolas", 10))
        self.code_editor.setPlainText('''{original_code}''')
        layout.addWidget(self.code_editor)
    
    def setup_output_tab(self):
        layout = QVBoxLayout(self.output_tab)
        
        self.output_text = QTextEdit()
        self.output_text.setFont(QFont("Consolas", 9))
        self.output_text.setStyleSheet("background-color: black; color: green;")
        layout.addWidget(self.output_text)
    
    def setup_menus(self):
        menubar = self.menuBar()
        
        # Menu Fichier
        file_menu = menubar.addMenu('Fichier')
        
        open_action = QAction('Ouvrir', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        save_action = QAction('Sauvegarder', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Quitter', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Menu Exécution
        run_menu = menubar.addMenu('Exécution')
        
        run_action = QAction('Exécuter', self)
        run_action.setShortcut('F5')
        run_action.triggered.connect(self.run_code)
        run_menu.addAction(run_action)
    
    def run_code(self):
        """Exécute le code"""
        try:
            code = self.code_editor.toPlainText()
            
            # Redirection de sortie
            old_stdout = sys.stdout
            sys.stdout = StringIO()
            
            # Exécution
            exec(compile(code, '<string>', 'exec'))
            
            # Récupération du résultat
            output = sys.stdout.getvalue()
            sys.stdout = old_stdout
            
            self.result_text.setText(output)
            self.output_text.append(f"Exécution terminée: {{output[:100]}}")
            
        except Exception as e:
            self.result_text.setText(f"Erreur: {{str(e)}}\\n{{traceback.format_exc()}}")
            self.output_text.append(f"Erreur: {{str(e)}}")
    
    def clear_output(self):
        self.result_text.clear()
    
    def open_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Ouvrir", "", "Python Files (*.py)")
        if filename:
            with open(filename, 'r', encoding='utf-8') as f:
                self.code_editor.setPlainText(f.read())
    
    def save_file(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Sauvegarder", "", "Python Files (*.py)")
        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.code_editor.toPlainText())

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
'''
    
    def _generate_pyqt6_template(self, original_code: str, config: ProjectConfig) -> str:
        """Template PyQt6 (similaire à PyQt5 avec adaptations)"""
        return self._generate_pyqt5_template(original_code, config).replace("PyQt5", "PyQt6")
    
    def _generate_flask_template(self, original_code: str, config: ProjectConfig) -> str:
        """Template Flask pour applications web"""
        return f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
{config.name} - Application Flask générée automatiquement
Généré le: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import os
import sys
import traceback
from io import StringIO
import threading
import subprocess

app = Flask(__name__)
app.secret_key = '{hashlib.md5(config.name.encode()).hexdigest()}'

# Variables globales
execution_output = ""
execution_error = ""
original_code = """{original_code}"""

@app.route('/')
def index():
    return render_template('index.html', 
                         app_name="{config.name}",
                         version="{config.version}",
                         author="{config.author}")

@app.route('/execute', methods=['POST'])
def execute_code():
    global execution_output, execution_error
    
    try:
        code = request.form.get('code', original_code)
        
        # Redirection de sortie
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        
        stdout_capture = StringIO()
        stderr_capture = StringIO()
        
        sys.stdout = stdout_capture
        sys.stderr = stderr_capture
        
        # Exécution du code
        exec(compile(code, '<string>', 'exec'))
        
        # Récupération des sorties
        execution_output = stdout_capture.getvalue()
        execution_error = stderr_capture.getvalue()
        
        # Restauration
        sys.stdout = old_stdout
        sys.stderr = old_stderr
        
        return jsonify({{
            'success': True,
            'output': execution_output,
            'error': execution_error
        }})
        
    except Exception as e:
        sys.stdout = old_stdout if 'old_stdout' in locals() else sys.stdout
        sys.stderr = old_stderr if 'old_stderr' in locals() else sys.stderr
        
        return jsonify({{
            'success': False,
            'output': '',
            'error': f"Erreur: {{str(e)}}\\n{{traceback.format_exc()}}"
        }})

@app.route('/get_code')
def get_code():
    return jsonify({{'code': original_code}})

@app.route('/about')
def about():
    return render_template('about.html',
                         app_name="{config.name}",
                         version="{config.version}",
                         author="{config.author}",
                         description="{config.description}")

if __name__ == '__main__':
    print(f"Démarrage de {{'{config.name}'}} sur http://localhost:5000")
    print("Appuyez sur Ctrl+C pour arrêter le serveur")
    
    app.run(debug={str(config.debug_mode).lower()}, 
            host='0.0.0.0', 
            port=5000)
'''
    
    def _generate_console_template(self, original_code: str, config: ProjectConfig) -> str:
        """Template pour applications console avec interface texte"""
        return f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
{config.name} - Application console générée automatiquement
Généré le: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

import sys
import os
import traceback
import subprocess
from datetime import datetime

class ConsoleApp:
    def __init__(self):
        self.app_name = "{config.name}"
        self.version = "{config.version}"
        self.author = "{config.author}"
        self.running = True
    
    def display_header(self):
        """Affiche l'en-tête de l'application"""
        print("=" * 60)
        print(f"{{self.app_name.center(60)}}")
        print(f"Version {{self.version}} - Par {{self.author}}".center(60))
        print("=" * 60)
        print()
    
    def display_menu(self):
        """Affiche le menu principal"""
        print("\\nMENU PRINCIPAL:")
        print("1. Exécuter le code original")
        print("2. Afficher le code source")
        print("3. Exécuter du code personnalisé")
        print("4. Afficher les informations")
        print("5. Quitter")
        print("-" * 30)
    
    def execute_original_code(self):
        """Exécute le code original"""
        print("\\n=== EXÉCUTION DU CODE ORIGINAL ===")
        print(f"Démarrage à {{datetime.now().strftime('%H:%M:%S')}}")
        print("-" * 40)
        
        try:
            # Code original intégré
            original_code = '''{original_code}'''
            
            # Exécution
            exec(compile(original_code, '<string>', 'exec'))
            
            print("-" * 40)
            print(f"Terminé à {{datetime.now().strftime('%H:%M:%S')}}")
            
        except Exception as e:
            print(f"\\n❌ ERREUR: {{str(e)}}")
            print("\\nDétails:")
            print(traceback.format_exc())
        
        input("\\nAppuyez sur Entrée pour continuer...")
    
    def show_source_code(self):
        """Affiche le code source"""
        print("\\n=== CODE SOURCE ===")
        print("-" * 40)
        
        original_code = '''{original_code}'''
        
        lines = original_code.split('\\n')
        for i, line in enumerate(lines, 1):
            print(f"{{i:3d}} | {{line}}")
        
        print("-" * 40)
        print(f"Total: {{len(lines)}} lignes")
        
        input("\\nAppuyez sur Entrée pour continuer...")
    
    def execute_custom_code(self):
        """Permet d'exécuter du code personnalisé"""
        print("\\n=== EXÉCUTION DE CODE PERSONNALISÉ ===")
        print("Saisissez votre code Python (tapez 'FIN' sur une ligne vide pour terminer):")
        print("-" * 50)
        
        code_lines = []
        while True:
            try:
                line = input(">>> " if not code_lines else "... ")
                if line.strip() == "FIN":
                    break
                code_lines.append(line)
            except KeyboardInterrupt:
                print("\\n\\nAnnulé par l'utilisateur.")
                return
        
        if not code_lines:
            print("Aucun code saisi.")
            return
        
        custom_code = '\\n'.join(code_lines)
        
        print("\\n=== EXÉCUTION ===")
        try:
            exec(compile(custom_code, '<string>', 'exec'))
            print("\\n✅ Exécution terminée avec succès.")
        except Exception as e:
            print(f"\\n❌ ERREUR: {{str(e)}}")
            print("\\nDétails:")
            print(traceback.format_exc())
        
        input("\\nAppuyez sur Entrée pour continuer...")
    
    def show_info(self):
        """Affiche les informations de l'application"""
        print("\\n=== INFORMATIONS ===")
        print(f"Nom: {{self.app_name}}")
        print(f"Version: {{self.version}}")
        print(f"Auteur: {{self.author}}")
        print(f"Description: {config.description}")
        print(f"Framework: Console/Terminal")
        print(f"Architecture: {config.architecture}")
        print(f"Mode debug: {config.debug_mode}")
        print(f"Python: {{sys.version}}")
        print(f"Plateforme: {{sys.platform}}")
        print(f"Répertoire de travail: {{os.getcwd()}}")
        
        input("\\nAppuyez sur Entrée pour continuer...")
    
    def run(self):
        """Boucle principale de l'application"""
        try:
            self.display_header()
            
            while self.running:
                self.display_menu()
                
                try:
                    choice = input("Votre choix (1-5): ").strip()
                    
                    if choice == '1':
                        self.execute_original_code()
                    elif choice == '2':
                        self.show_source_code()
                    elif choice == '3':
                        self.execute_custom_code()
                    elif choice == '4':
                        self.show_info()
                    elif choice == '5':
                        print("\\nAu revoir! 👋")
                        self.running = False
                    else:
                        print("\\n❌ Choix invalide. Veuillez saisir un nombre entre 1 et 5.")
                        input("Appuyez sur Entrée pour continuer...")
                
                except KeyboardInterrupt:
                    print("\\n\\nArrêt demandé par l'utilisateur.")
                    self.running = False
                except EOFError:
                    print("\\n\\nFin d'entrée détectée.")
                    self.running = False
        
        except Exception as e:
            print(f"\\n❌ ERREUR CRITIQUE: {{str(e)}}")
            print(traceback.format_exc())
            input("\\nAppuyez sur Entrée pour fermer...")

def main():
    """Point d'entrée principal"""
    app = ConsoleApp()
    app.run()

if __name__ == "__main__":
    main()
'''

class PyInstallerBuilder:
    """Constructeur d'exécutables avec PyInstaller"""
    
    def __init__(self):
        self.temp_dir = None
        self.build_process = None
    
    def build_executable(self, source_file: str, config: ProjectConfig, 
                        output_dir: str = None) -> Tuple[bool, str]:
        """Construit un exécutable à partir du code source"""
        try:
            if output_dir is None:
                output_dir = OUTPUT_FOLDER
            
            # Création du répertoire temporaire
            self.temp_dir = tempfile.mkdtemp(prefix="pyapp_build_")
            logger.info(f"Répertoire de build: {self.temp_dir}")
            
            # Copie du fichier source
            source_name = f"{config.name}.py"
            temp_source = os.path.join(self.temp_dir, source_name)
            
            with open(source_file, 'r', encoding='utf-8') as src:
                content = src.read()
            
            with open(temp_source, 'w', encoding='utf-8') as dst:
                dst.write(content)
            
            # Génération du fichier spec si nécessaire
            spec_file = self._generate_spec_file(temp_source, config)
            
            # Construction des arguments PyInstaller
            args = self._build_pyinstaller_args(temp_source, config, output_dir, spec_file)
            
            # Exécution de PyInstaller
            logger.info(f"Commande PyInstaller: {' '.join(args)}")
            
            self.build_process = subprocess.Popen(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                cwd=self.temp_dir
            )
            
            # Lecture de la sortie en temps réel
            output_lines = []
            while True:
                line = self.build_process.stdout.readline()
                if not line and self.build_process.poll() is not None:
                    break
                if line:
                    output_lines.append(line.strip())
                    logger.info(f"PyInstaller: {line.strip()}")
            
            # Vérification du résultat
            return_code = self.build_process.poll()
            output_text = '\n'.join(output_lines)
            
            if return_code == 0:
                # Recherche du fichier exécutable généré
                exe_path = self._find_executable(self.temp_dir, config, output_dir)
                if exe_path and os.path.exists(exe_path):
                    logger.info(f"Exécutable créé avec succès: {exe_path}")
                    return True, exe_path
                else:
                    return False, "Exécutable introuvable après la construction"
            else:
                return False, f"Erreur PyInstaller (code {return_code}):\n{output_text}"
        
        except Exception as e:
            logger.error(f"Erreur lors de la construction: {e}")
            return False, f"Erreur: {str(e)}"
        
        finally:
            # Nettoyage
            if self.temp_dir and os.path.exists(self.temp_dir):
                try:
                    shutil.rmtree(self.temp_dir)
                except Exception as e:
                    logger.warning(f"Impossible de supprimer le répertoire temporaire: {e}")
    
    def _generate_spec_file(self, source_file: str, config: ProjectConfig) -> Optional[str]:
        """Génère un fichier .spec pour PyInstaller"""
        if not config.icon_path and not config.requirements:
            return None
        
        spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(['{os.path.basename(source_file)}'],
             pathex=['{os.path.dirname(source_file)}'],
             binaries=[],
             datas=[],
             hiddenimports={config.requirements},
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='{config.name}',
          debug={str(config.debug_mode).lower()},
          bootloader_ignore_signals=False,
          strip=False,
          upx={str(config.upx_compress).lower()},
          upx_exclude=[],
          runtime_tmpdir=None,
          console={str(config.include_console).lower()},
          icon='{config.icon_path if config.icon_path else ''}')
'''
        
        spec_file = os.path.join(os.path.dirname(source_file), f"{config.name}.spec")
        with open(spec_file, 'w', encoding='utf-8') as f:
            f.write(spec_content)
        
        return spec_file
    
    def _build_pyinstaller_args(self, source_file: str, config: ProjectConfig, 
                               output_dir: str, spec_file: str = None) -> List[str]:
        """Construit les arguments de PyInstaller"""
        if spec_file:
            args = ['pyinstaller', spec_file]
        else:
            args = ['pyinstaller']
            
            # Fichier source
            args.append(source_file)
            
            # Options de base
            args.extend(['--name', config.name])
            args.extend(['--distpath', output_dir])
            
            # Mode one-file
            if config.one_file:
                args.append('--onefile')
            else:
                args.append('--onedir')
            
            # Console
            if config.include_console:
                args.append('--console')
            else:
                args.append('--windowed')
            
            # Icône
            if config.icon_path and os.path.exists(config.icon_path):
                args.extend(['--icon', config.icon_path])
            
            # Requirements
            for req in config.requirements:
                args.extend(['--hidden-import', req])
            
            # UPX compression
            if config.upx_compress:
                args.append('--upx-dir')
                args.append('upx')  # Chemin vers UPX si disponible
            
            # Debug
            if config.debug_mode:
                args.append('--debug')
                args.append('--log-level=DEBUG')
            else:
                args.append('--log-level=WARN')
        
        # Options communes
        args.extend(['--clean', '--noconfirm'])
        
        return args
    
    def _find_executable(self, build_dir: str, config: ProjectConfig, output_dir: str) -> Optional[str]:
        """Trouve l'exécutable généré"""
        possible_paths = [
            os.path.join(output_dir, f"{config.name}.exe"),
            os.path.join(output_dir, config.name, f"{config.name}.exe"),
            os.path.join(build_dir, "dist", f"{config.name}.exe"),
            os.path.join(build_dir, "dist", config.name, f"{config.name}.exe"),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    def cancel_build(self):
        """Annule la construction en cours"""
        if self.build_process and self.build_process.poll() is None:
            self.build_process.terminate()
            try:
                self.build_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.build_process.kill()

class FlaskWebInterface:
    """Interface web Flask pour le convertisseur"""
    
    def __init__(self):
        self.app = Flask(__name__, template_folder=TEMPLATES_FOLDER, static_folder=STATIC_FOLDER)
        self.app.secret_key = hashlib.md5(b'script_converter').hexdigest()
        self.app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE
        self.app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
        
        self.db = DatabaseManager()
        self.analyzer = CodeAnalyzer()
        self.template_generator = TemplateGenerator()
        self.builder = PyInstallerBuilder()
        
        self._setup_routes()
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Assure que tous les répertoires nécessaires existent"""
        directories = [UPLOAD_FOLDER, TEMPLATES_FOLDER, STATIC_FOLDER, OUTPUT_FOLDER]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def _setup_routes(self):
        """Configure les routes Flask"""
        
        @self.app.route('/')
        def index():
            projects = self.db.list_projects()
            return render_template('index.html', projects=projects)
        
        @self.app.route('/upload', methods=['GET', 'POST'])
        def upload_file():
            if request.method == 'POST':
                if 'file' not in request.files:
                    flash('Aucun fichier sélectionné', 'error')
                    return redirect(request.url)
                
                file = request.files['file']
                if file.filename == '':
                    flash('Aucun fichier sélectionné', 'error')
                    return redirect(request.url)
                
                if file and self._allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(self.app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                    
                    # Analyse du fichier
                    analysis = self.analyzer.analyze_file(file_path)
                    
                    # Configuration par défaut
                    config = ProjectConfig(
                        name=os.path.splitext(filename)[0],
                        description=f"Application générée depuis {filename}",
                        author="Utilisateur",
                        version="1.0.0",
                        gui_framework=analysis.get('gui_framework', 'tkinter')
                    )
                    
                    # Sauvegarde
                    with open(file_path, 'r', encoding='utf-8') as f:
                        source_code = f.read()
                    
                    self.db.save_project(config, source_code)
                    
                    flash(f'Fichier {filename} téléchargé et analysé avec succès', 'success')
                    return redirect(url_for('project_config', name=config.name))
                else:
                    flash('Type de fichier non autorisé', 'error')
            
            return render_template('upload.html')
        
        @self.app.route('/project/<name>')
        def project_config(name):
            project_data = self.db.load_project(name)
            if not project_data:
                flash('Projet introuvable', 'error')
                return redirect(url_for('index'))
            
            config, source_code = project_data
            return render_template('project_config.html', config=config, source_code=source_code)
        
        @self.app.route('/build/<name>', methods=['POST'])
        def build_project(name):
            project_data = self.db.load_project(name)
            if not project_data:
                return jsonify({'success': False, 'error': 'Projet introuvable'})
            
            config, source_code = project_data
            
            # Mise à jour de la configuration
            for field in ['description', 'author', 'version', 'gui_framework', 'theme']:
                if field in request.form:
                    setattr(config, field, request.form[field])
            
            # Options booléennes
            config.include_console = 'include_console' in request.form
            config.one_file = 'one_file' in request.form
            config.upx_compress = 'upx_compress' in request.form
            config.debug_mode = 'debug_mode' in request.form
            
            # Génération du code GUI
            gui_code = self.template_generator.generate_gui_wrapper(source_code, config)
            
            # Création du fichier temporaire
            temp_file = os.path.join(UPLOAD_FOLDER, f"temp_{name}.py")
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(gui_code)
            
            # Construction
            success, result = self.builder.build_executable(temp_file, config, OUTPUT_FOLDER)
            
            # Nettoyage
            if os.path.exists(temp_file):
                os.remove(temp_file)
            
            if success:
                return jsonify({
                    'success': True, 
                    'message': 'Exécutable créé avec succès',
                    'path': result
                })
            else:
                return jsonify({'success': False, 'error': result})
        
        @self.app.route('/download/<path:filename>')
        def download_file(filename):
            try:
                return send_file(filename, as_attachment=True)
            except FileNotFoundError:
                flash('Fichier introuvable', 'error')
                return redirect(url_for('index'))
        
        @self.app.route('/preview/<name>')
        def preview_code(name):
            project_data = self.db.load_project(name)
            if not project_data:
                return jsonify({'error': 'Projet introuvable'})
            
            config, source_code = project_data
            gui_code = self.template_generator.generate_gui_wrapper(source_code, config)
            
            return jsonify({'code': gui_code})
        
        @self.app.route('/delete/<name>', methods=['POST'])
        def delete_project(name):
            if self.db.delete_project(name):
                flash('Projet supprimé avec succès', 'success')
            else:
                flash('Erreur lors de la suppression', 'error')
            
            return redirect(url_for('index'))
        
        @self.app.route('/api/projects')
        def api_projects():
            return jsonify(self.db.list_projects())
        
        @self.app.route('/api/analyze', methods=['POST'])
        def api_analyze():
            if 'code' not in request.json:
                return jsonify({'error': 'Code manquant'})
            
            # Analyse du code (simulation)
            code = request.json['code']
            
            # Sauvegarde temporaire pour analyse
            temp_file = os.path.join(UPLOAD_FOLDER, "temp_analysis.py")
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(code)
            
            analysis = self.analyzer.analyze_file(temp_file)
            
            # Nettoyage
            if os.path.exists(temp_file):
                os.remove(temp_file)
            
            return jsonify(analysis)
    
    def _allowed_file(self, filename: str) -> bool:
        """Vérifie si le fichier est autorisé"""
        return '.' in filename and \
               Path(filename).suffix.lower() in ALLOWED_EXTENSIONS
    
    def run(self, host='127.0.0.1', port=5000, debug=False):
        """Lance le serveur Flask"""
        logger.info(f"Démarrage du serveur Flask sur http://{host}:{port}")
        self.app.run(host=host, port=port, debug=debug)

class TkinterGUI:
    """Interface graphique Tkinter pour le convertisseur"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Script to Desktop App Converter")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Variables
        self.current_project = None
        self.source_code = ""
        self.config = ProjectConfig(
            name="MonApp",
            description="Application générée",
            author="Utilisateur",
            version="1.0.0"
        )
        
        # Composants
        self.db = DatabaseManager()
        self.analyzer = CodeAnalyzer()
        self.template_generator = TemplateGenerator()
        self.builder = PyInstallerBuilder()
        
        self.setup_ui()
        self.setup_menus()
        
        # Style
        self.setup_style()
    
    def setup_ui(self):
        """Configure l'interface utilisateur"""
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padding=10)
        
        # Barre d'outils
        toolbar = ttk.Frame(main_frame)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(toolbar, text="📁 Ouvrir Script", 
                  command=self.open_script).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="💾 Sauvegarder Projet", 
                  command=self.save_project).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="📋 Charger Projet", 
                  command=self.load_project).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="🔧 Construire", 
                  command=self.build_executable, style="Accent.TButton").pack(side=tk.LEFT, padx=(0, 5))
        
        # Séparateur
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # Indicateur de statut
        self.status_var = tk.StringVar(value="Prêt")
        ttk.Label(toolbar, textvariable=self.status_var).pack(side=tk.RIGHT)
        
        # Notebook principal
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Onglets
        self.setup_source_tab()
        self.setup_config_tab()
        self.setup_preview_tab()
        self.setup_build_tab()
        self.setup_projects_tab()
    
    def setup_source_tab(self):
        """Onglet Code Source"""
        self.source_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.source_frame, text="📝 Code Source")
        
        # Toolbar
        source_toolbar = ttk.Frame(self.source_frame)
        source_toolbar.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(source_toolbar, text="📁 Charger", 
                  command=self.load_source_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(source_toolbar, text="💾 Sauvegarder", 
                  command=self.save_source_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(source_toolbar, text="🔍 Analyser", 
                  command=self.analyze_code).pack(side=tk.LEFT, padx=(0, 5))
        
        # Éditeur de code
        editor_frame = ttk.Frame(self.source_frame)
        editor_frame.pack(fill=tk.BOTH, expand=True)
        
        self.source_text = scrolledtext.ScrolledText(
            editor_frame, 
            wrap=tk.NONE, 
            font=("Consolas", 10),
            undo=True,
            maxundo=50
        )
        self.source_text.pack(fill=tk.BOTH, expand=True)
        
        # Numérotation des lignes (simplifiée)
        self.source_text.bind('<KeyRelease>', self.on_text_change)
        
        # Zone d'information d'analyse
        info_frame = ttk.LabelFrame(self.source_frame, text="Analyse du Code")
        info_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.analysis_text = tk.Text(info_frame, height=4, font=("Segoe UI", 9))
        self.analysis_text.pack(fill=tk.X, padx=5, pady=5)
    
    def setup_config_tab(self):
        """Onglet Configuration"""
        self.config_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.config_frame, text="⚙️ Configuration")
        
        # Création d'un canvas avec scrollbar
        canvas = tk.Canvas(self.config_frame)
        scrollbar = ttk.Scrollbar(self.config_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Informations générales
        general_frame = ttk.LabelFrame(scrollable_frame, text="Informations Générales")
        general_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Nom du projet
        ttk.Label(general_frame, text="Nom du projet:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.name_var = tk.StringVar(value=self.config.name)
        ttk.Entry(general_frame, textvariable=self.name_var, width=40).grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        
        # Description
        ttk.Label(general_frame, text="Description:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.description_var = tk.StringVar(value=self.config.description)
        ttk.Entry(general_frame, textvariable=self.description_var, width=40).grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        
        # Auteur
        ttk.Label(general_frame, text="Auteur:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.author_var = tk.StringVar(value=self.config.author)
        ttk.Entry(general_frame, textvariable=self.author_var, width=40).grid(row=2, column=1, sticky="ew", padx=5, pady=2)
        
        # Version
        ttk.Label(general_frame, text="Version:").grid(row=3, column=0, sticky="w", padx=5, pady=2)
        self.version_var = tk.StringVar(value=self.config.version)
        ttk.Entry(general_frame, textvariable=self.version_var, width=40).grid(row=3, column=1, sticky="ew", padx=5, pady=2)
        
        general_frame.columnconfigure(1, weight=1)
        
        # Options GUI
        gui_frame = ttk.LabelFrame(scrollable_frame, text="Interface Graphique")
        gui_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(gui_frame, text="Framework GUI:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.gui_framework_var = tk.StringVar(value=self.config.gui_framework)
        gui_combo = ttk.Combobox(gui_frame, textvariable=self.gui_framework_var, width=37)
        gui_combo['values'] = ('tkinter', 'PyQt5', 'PyQt6', 'flask', 'console')
        gui_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        
        ttk.Label(gui_frame, text="Thème:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.theme_var = tk.StringVar(value=self.config.theme)
        theme_combo = ttk.Combobox(gui_frame, textvariable=self.theme_var, width=37)
        theme_combo['values'] = ('default', 'dark', 'light', 'modern', 'classic')
        theme_combo.grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        
        # Icône
        ttk.Label(gui_frame, text="Icône (.ico):").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        icon_frame = ttk.Frame(gui_frame)
        icon_frame.grid(row=2, column=1, sticky="ew", padx=5, pady=2)
        
        self.icon_path_var = tk.StringVar(value=self.config.icon_path or "")
        ttk.Entry(icon_frame, textvariable=self.icon_path_var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(icon_frame, text="...", width=3, 
                  command=self.browse_icon).pack(side=tk.RIGHT, padx=(5, 0))
        
        gui_frame.columnconfigure(1, weight=1)
        
        # Options de construction
        build_frame = ttk.LabelFrame(scrollable_frame, text="Options de Construction")
        build_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Architecture
        ttk.Label(build_frame, text="Architecture:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.architecture_var = tk.StringVar(value=self.config.architecture)
        arch_combo = ttk.Combobox(build_frame, textvariable=self.architecture_var, width=37)
        arch_combo['values'] = ('x64', 'x86', 'auto')
        arch_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        
        # Options booléennes
        self.one_file_var = tk.BooleanVar(value=self.config.one_file)
        ttk.Checkbutton(build_frame, text="Fichier unique (.exe)", 
                       variable=self.one_file_var).grid(row=1, column=0, columnspan=2, sticky="w", padx=5, pady=2)
        
        self.include_console_var = tk.BooleanVar(value=self.config.include_console)
        ttk.Checkbutton(build_frame, text="Inclure la console", 
                       variable=self.include_console_var).grid(row=2, column=0, columnspan=2, sticky="w", padx=5, pady=2)
        
        self.upx_compress_var = tk.BooleanVar(value=self.config.upx_compress)
        ttk.Checkbutton(build_frame, text="Compression UPX", 
                       variable=self.upx_compress_var).grid(row=3, column=0, columnspan=2, sticky="w", padx=5, pady=2)
        
        self.debug_mode_var = tk.BooleanVar(value=self.config.debug_mode)
        ttk.Checkbutton(build_frame, text="Mode debug", 
                       variable=self.debug_mode_var).grid(row=4, column=0, columnspan=2, sticky="w", padx=5, pady=2)
        
        build_frame.columnconfigure(1, weight=1)
        
        # Dépendances
        deps_frame = ttk.LabelFrame(scrollable_frame, text="Dépendances")
        deps_frame.pack(fill=tk.X, padx=10, pady=5)
        
        deps_toolbar = ttk.Frame(deps_frame)
        deps_toolbar.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Button(deps_toolbar, text="➕ Ajouter", 
                  command=self.add_dependency).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(deps_toolbar, text="➖ Supprimer", 
                  command=self.remove_dependency).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(deps_toolbar, text="🔍 Auto-détecter", 
                  command=self.detect_dependencies).pack(side=tk.LEFT)
        
        # Liste des dépendances
        self.deps_listbox = tk.Listbox(deps_frame, height=6)
        self.deps_listbox.pack(fill=tk.X, padx=5, pady=2)
        
        # Mise à jour de la liste
        self.update_dependencies_list()
        
        # Configuration du canvas
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind mousewheel
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind("<MouseWheel>", _on_mousewheel)
    
    def setup_preview_tab(self):
        """Onglet Prévisualisation"""
        self.preview_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.preview_frame, text="👁️ Prévisualisation")
        
        # Toolbar
        preview_toolbar = ttk.Frame(self.preview_frame)
        preview_toolbar.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(preview_toolbar, text="🔄 Actualiser", 
                  command=self.update_preview).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(preview_toolbar, text="💾 Exporter Code", 
                  command=self.export_preview).pack(side=tk.LEFT, padx=(0, 5))
        
        # Zone de prévisualisation
        self.preview_text = scrolledtext.ScrolledText(
            self.preview_frame, 
            wrap=tk.NONE, 
            font=("Consolas", 9),
            state=tk.DISABLED
        )
        self.preview_text.pack(fill=tk.BOTH, expand=True)
    
    def setup_build_tab(self):
        """Onglet Construction"""
        self.build_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.build_frame, text="🔧 Construction")
        
        # Contrôles de construction
        build_controls = ttk.Frame(self.build_frame)
        build_controls.pack(fill=tk.X, pady=(0, 10))
        
        self.build_button = ttk.Button(build_controls, text="🚀 Construire l'Exécutable", 
                                      command=self.build_executable, style="Accent.TButton")
        self.build_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.cancel_button = ttk.Button(build_controls, text="❌ Annuler", 
                                       command=self.cancel_build, state=tk.DISABLED)
        self.cancel_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Barre de progression
        self.progress_var = tk.StringVar(value="Prêt à construire")
        ttk.Label(build_controls, textvariable=self.progress_var).pack(side=tk.RIGHT)
        
        self.build_progress = ttk.Progressbar(build_controls, mode='indeterminate')
        self.build_progress.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 10))
        
        # Log de construction
        log_frame = ttk.LabelFrame(self.build_frame, text="Journal de Construction")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.build_log = scrolledtext.ScrolledText(
            log_frame, 
            wrap=tk.WORD, 
            font=("Consolas", 9),
            bg="#2b2b2b", 
            fg="#ffffff"
        )
        self.build_log.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def setup_projects_tab(self):
        """Onglet Projets"""
        self.projects_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.projects_frame, text="📁 Projets")
        
        # Toolbar
        projects_toolbar = ttk.Frame(self.projects_frame)
        projects_toolbar.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(projects_toolbar, text="🔄 Actualiser", 
                  command=self.refresh_projects).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(projects_toolbar, text="📋 Charger", 
                  command=self.load_selected_project).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(projects_toolbar, text="🗑️ Supprimer", 
                  command=self.delete_selected_project).pack(side=tk.LEFT, padx=(0, 5))
        
        # Liste des projets
        self.projects_tree = ttk.Treeview(self.projects_frame, columns=('created', 'updated'), show='tree headings')
        self.projects_tree.heading('#0', text='Nom du Projet')
        self.projects_tree.heading('created', text='Créé le')
        self.projects_tree.heading('updated', text='Modifié le')
        
        self.projects_tree.column('#0', width=300)
        self.projects_tree.column('created', width=150)
        self.projects_tree.column('updated', width=150)
        
        # Scrollbar pour la liste
        projects_scrollbar = ttk.Scrollbar(self.projects_frame, orient=tk.VERTICAL, command=self.projects_tree.yview)
        self.projects_tree.configure(yscrollcommand=projects_scrollbar.set)
        
        self.projects_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        projects_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Double-clic pour charger
        self.projects_tree.bind('<Double-Button-1>', lambda e: self.load_selected_project())
        
        # Actualisation initiale
        self.refresh_projects()
    
    def setup_menus(self):
        """Configure les menus"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menu Fichier
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Fichier", menu=file_menu)
        file_menu.add_command(label="Nouveau Projet", command=self.new_project, accelerator="Ctrl+N")
        file_menu.add_command(label="Ouvrir Script...", command=self.open_script, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="Sauvegarder Projet", command=self.save_project, accelerator="Ctrl+S")
        file_menu.add_command(label="Charger Projet...", command=self.load_project, accelerator="Ctrl+L")
        file_menu.add_separator()
        file_menu.add_command(label="Exporter Code GUI...", command=self.export_preview, accelerator="Ctrl+E")
        file_menu.add_separator()
        file_menu.add_command(label="Quitter", command=self.root.quit, accelerator="Ctrl+Q")
        
        # Menu Édition
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Édition", menu=edit_menu)
        edit_menu.add_command(label="Annuler", command=lambda: self.source_text.event_generate("<<Undo>>"), accelerator="Ctrl+Z")
        edit_menu.add_command(label="Rétablir", command=lambda: self.source_text.event_generate("<<Redo>>"), accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Couper", command=lambda: self.source_text.event_generate("<<Cut>>"), accelerator="Ctrl+X")
        edit_menu.add_command(label="Copier", command=lambda: self.source_text.event_generate("<<Copy>>"), accelerator="Ctrl+C")
        edit_menu.add_command(label="Coller", command=lambda: self.source_text.event_generate("<<Paste>>"), accelerator="Ctrl+V")
        edit_menu.add_separator()
        edit_menu.add_command(label="Sélectionner tout", command=lambda: self.source_text.event_generate("<<SelectAll>>"), accelerator="Ctrl+A")
        
        # Menu Outils
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Outils", menu=tools_menu)
        tools_menu.add_command(label="Analyser le Code", command=self.analyze_code, accelerator="F7")
        tools_menu.add_command(label="Détecter les Dépendances", command=self.detect_dependencies, accelerator="F8")
        tools_menu.add_command(label="Actualiser Prévisualisation", command=self.update_preview, accelerator="F9")
        tools_menu.add_separator()
        tools_menu.add_command(label="Construire Exécutable", command=self.build_executable, accelerator="F5")
        
        # Menu Aide
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Aide", menu=help_menu)
        help_menu.add_command(label="Documentation", command=self.show_documentation)
        help_menu.add_command(label="À propos", command=self.show_about)
        
        # Raccourcis clavier
        self.root.bind('<Control-n>', lambda e: self.new_project())
        self.root.bind('<Control-o>', lambda e: self.open_script())
        self.root.bind('<Control-s>', lambda e: self.save_project())
        self.root.bind('<Control-l>', lambda e: self.load_project())
        self.root.bind('<Control-e>', lambda e: self.export_preview())
        self.root.bind('<Control-q>', lambda e: self.root.quit())
        self.root.bind('<F5>', lambda e: self.build_executable())
        self.root.bind('<F7>', lambda e: self.analyze_code())
        self.root.bind('<F8>', lambda e: self.detect_dependencies())
        self.root.bind('<F9>', lambda e: self.update_preview())
    
    def setup_style(self):
        """Configure le style de l'interface"""
        style = ttk.Style()
        
        # Thème moderne
        if "vista" in style.theme_names():
            style.theme_use("vista")
        elif "clam" in style.theme_names():
            style.theme_use("clam")
        
        # Styles personnalisés
        style.configure("Accent.TButton", foreground="white")
        
        # Configuration des couleurs
        self.root.configure(bg="#f0f0f0")
    
    # Méthodes événementielles
    def on_text_change(self, event=None):
        """Appelé quand le texte change"""
        self.status_var.set("Modifié")
    
    def new_project(self):
        """Crée un nouveau projet"""
        if messagebox.askyesno("Nouveau Projet", "Voulez-vous créer un nouveau projet?\nLes modifications non sauvegardées seront perdues."):
            self.source_text.delete(1.0, tk.END)
            self.config = ProjectConfig(
                name="MonApp",
                description="Application générée",
                author="Utilisateur",
                version="1.0.0"
            )
            self.update_config_ui()
            self.status_var.set("Nouveau projet")
    
    def open_script(self):
        """Ouvre un script Python"""
        filename = filedialog.askopenfilename(
            title="Ouvrir un script Python",
            filetypes=[
                ("Fichiers Python", "*.py *.pyw"),
                ("Tous les fichiers", "*.*")
            ]
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self.source_text.delete(1.0, tk.END)
                self.source_text.insert(1.0, content)
                
                # Mise à jour du nom du projet
                base_name = os.path.splitext(os.path.basename(filename))[0]
                self.config.name = base_name
                self.name_var.set(base_name)
                
                self.status_var.set(f"Script chargé: {os.path.basename(filename)}")
                
                # Analyse automatique
                self.analyze_code()
                
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible de charger le fichier:\n{str(e)}")
    
    def save_project(self):
        """Sauvegarde le projet"""
        try:
            # Mise à jour de la configuration
            self.update_config_from_ui()
            
            # Sauvegarde du code source
            self.source_code = self.source_text.get(1.0, tk.END)
            
            # Sauvegarde dans la base de données
            self.db.save_project(self.config, self.source_code)
            
            self.status_var.set(f"Projet '{self.config.name}' sauvegardé")
            messagebox.showinfo("Succès", f"Projet '{self.config.name}' sauvegardé avec succès!")
            
            # Actualisation de la liste des projets
            self.refresh_projects()
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de sauvegarder le projet:\n{str(e)}")
    
    def load_project(self):
        """Charge un projet existant"""
        projects = self.db.list_projects()
        if not projects:
            messagebox.showinfo("Information", "Aucun projet sauvegardé trouvé.")
            return
        
        # Fenêtre de sélection de projet
        project_window = tk.Toplevel(self.root)
        project_window.title("Charger un Projet")
        project_window.geometry("500x300")
        project_window.transient(self.root)
        project_window.grab_set()
        
        # Liste des projets
        listbox_frame = ttk.Frame(project_window)
        listbox_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        project_listbox = tk.Listbox(listbox_frame)
        project_listbox.pack(fill=tk.BOTH, expand=True)
        
        for project in projects:
            project_listbox.insert(tk.END, f"{project['name']} (modifié: {project['updated_at'][:19]})")
        
        # Boutons
        button_frame = ttk.Frame(project_window)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        def load_selected():
            selection = project_listbox.curselection()
            if selection:
                project_name = projects[selection[0]]['name']
                self.load_project_by_name(project_name)
                project_window.destroy()
        
        ttk.Button(button_frame, text="Charger", command=load_selected).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Annuler", command=project_window.destroy).pack(side=tk.RIGHT)
        
        # Double-clic pour charger
        project_listbox.bind('<Double-Button-1>', lambda e: load_selected())
    
    def load_project_by_name(self, name: str):
        """Charge un projet par son nom"""
        try:
            project_data = self.db.load_project(name)
            if project_data:
                self.config, self.source_code = project_data
                
                # Mise à jour de l'interface
                self.source_text.delete(1.0, tk.END)
                self.source_text.insert(1.0, self.source_code)
                
                self.update_config_ui()
                self.status_var.set(f"Projet '{name}' chargé")
                
                messagebox.showinfo("Succès", f"Projet '{name}' chargé avec succès!")
            else:
                messagebox.showerror("Erreur", f"Projet '{name}' introuvable.")
        
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de charger le projet:\n{str(e)}")
    
    def update_config_from_ui(self):
        """Met à jour la configuration depuis l'interface"""
        self.config.name = self.name_var.get()
        self.config.description = self.description_var.get()
        self.config.author = self.author_var.get()
        self.config.version = self.version_var.get()
        self.config.gui_framework = self.gui_framework_var.get()
        self.config.theme = self.theme_var.get()
        self.config.icon_path = self.icon_path_var.get() if self.icon_path_var.get() else None
        self.config.architecture = self.architecture_var.get()
        self.config.one_file = self.one_file_var.get()
        self.config.include_console = self.include_console_var.get()
        self.config.upx_compress = self.upx_compress_var.get()
        self.config.debug_mode = self.debug_mode_var.get()
        
        # Dépendances
        self.config.requirements = list(self.deps_listbox.get(0, tk.END))
    
    def update_config_ui(self):
        """Met à jour l'interface depuis la configuration"""
        self.name_var.set(self.config.name)
        self.description_var.set(self.config.description)
        self.author_var.set(self.config.author)
        self.version_var.set(self.config.version)
        self.gui_framework_var.set(self.config.gui_framework)
        self.theme_var.set(self.config.theme)
        self.icon_path_var.set(self.config.icon_path or "")
        self.architecture_var.set(self.config.architecture)
        self.one_file_var.set(self.config.one_file)
        self.include_console_var.set(self.config.include_console)
        self.upx_compress_var.set(self.config.upx_compress)
        self.debug_mode_var.set(self.config.debug_mode)
        
        self.update_dependencies_list()
    
    def analyze_code(self):
        """Analyse le code source"""
        try:
            source_code = self.source_text.get(1.0, tk.END)
            if not source_code.strip():
                self.analysis_text.delete(1.0, tk.END)
                self.analysis_text.insert(1.0, "Aucun code à analyser.")
                return
            
            # Sauvegarde temporaire pour analyse
            temp_file = os.path.join(UPLOAD_FOLDER, "temp_analysis.py")
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(source_code)
            
            # Analyse
            analysis = self.analyzer.analyze_file(temp_file)
            
            # Nettoyage
            if os.path.exists(temp_file):
                os.remove(temp_file)
            
            # Affichage des résultats
            self.analysis_text.delete(1.0, tk.END)
            
            analysis_text = f"""Analyse du code:
• Framework GUI détecté: {analysis.get('gui_framework', 'Non détecté')}
• Nombre de lignes: {analysis.get('lines_of_code', 0)}
• Complexité: {analysis.get('complexity', 0)}
• Imports: {len(analysis.get('imports', []))}
• Fonctions: {len(analysis.get('functions', []))}
• Classes: {len(analysis.get('classes', []))}

Imports détectés: {', '.join(analysis.get('imports', [])[:10])}{'...' if len(analysis.get('imports', [])) > 10 else ''}
"""
            
            self.analysis_text.insert(1.0, analysis_text)
            
            # Mise à jour automatique du framework GUI
            detected_framework = analysis.get('gui_framework', 'console')
            if detected_framework != 'console':
                self.gui_framework_var.set(detected_framework)
            
            self.status_var.set("Code analysé")
            
        except Exception as e:
            self.analysis_text.delete(1.0, tk.END)
            self.analysis_text.insert(1.0, f"Erreur lors de l'analyse:\n{str(e)}")
            logger.error(f"Erreur analyse code: {e}")
    
    def detect_dependencies(self):
        """Détecte automatiquement les dépendances"""
        try:
            source_code = self.source_text.get(1.0, tk.END)
            if not source_code.strip():
                messagebox.showwarning("Attention", "Aucun code à analyser.")
                return
            
            # Sauvegarde temporaire pour analyse
            temp_file = os.path.join(UPLOAD_FOLDER, "temp_deps.py")
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(source_code)
            
            # Analyse
            analysis = self.analyzer.analyze_file(temp_file)
            
            # Nettoyage
            if os.path.exists(temp_file):
                os.remove(temp_file)
            
            # Extraction des imports
            imports = analysis.get('imports', [])
            
            # Filtrage des modules standard Python
            standard_modules = {
                'os', 'sys', 'time', 'datetime', 'json', 'sqlite3', 'threading',
                'subprocess', 'tempfile', 'shutil', 'pathlib', 'logging', 'traceback',
                'argparse', 'configparser', 're', 'math', 'random', 'collections',
                'itertools', 'functools', 'operator', 'typing', 'dataclasses',
                'contextlib', 'asyncio', 'io', 'base64', 'hashlib', 'urllib',
                'http', 'html', 'xml', 'csv', 'email', 'unittest', 'zipfile'
            }
            
            external_imports = [imp for imp in imports if imp not in standard_modules]
            
            # Mise à jour de la liste
            self.deps_listbox.delete(0, tk.END)
            for imp in external_imports:
                self.deps_listbox.insert(tk.END, imp)
            
            # Mise à jour de la configuration
            self.config.requirements = external_imports
            
            self.status_var.set(f"{len(external_imports)} dépendances détectées")
            
            if external_imports:
                messagebox.showinfo("Dépendances détectées", 
                                  f"{len(external_imports)} dépendances externes détectées:\n" + 
                                  "\n".join(external_imports[:10]) + 
                                  ("..." if len(external_imports) > 10 else ""))
            else:
                messagebox.showinfo("Dépendances", "Aucune dépendance externe détectée.")
        
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la détection des dépendances:\n{str(e)}")
    
    def add_dependency(self):
        """Ajoute une dépendance manuellement"""
        dep = tk.simpledialog.askstring("Ajouter une dépendance", "Nom du module:")
        if dep and dep.strip():
            dep = dep.strip()
            if dep not in self.deps_listbox.get(0, tk.END):
                self.deps_listbox.insert(tk.END, dep)
                self.status_var.set(f"Dépendance '{dep}' ajoutée")
    
    def remove_dependency(self):
        """Supprime la dépendance sélectionnée"""
        selection = self.deps_listbox.curselection()
        if selection:
            dep_name = self.deps_listbox.get(selection[0])
            self.deps_listbox.delete(selection[0])
            self.status_var.set(f"Dépendance '{dep_name}' supprimée")
    
    def update_dependencies_list(self):
        """Met à jour la liste des dépendances"""
        self.deps_listbox.delete(0, tk.END)
        for req in self.config.requirements:
            self.deps_listbox.insert(tk.END, req)
    
    def browse_icon(self):
        """Parcourt pour sélectionner une icône"""
        filename = filedialog.askopenfilename(
            title="Sélectionner une icône",
            filetypes=[
                ("Fichiers icône", "*.ico"),
                ("Images", "*.png *.jpg *.jpeg *.bmp"),
                ("Tous les fichiers", "*.*")
            ]
        )
        
        if filename:
            self.icon_path_var.set(filename)
    
    def load_source_file(self):
        """Charge un fichier source"""
        self.open_script()
    
    def save_source_file(self):
        """Sauvegarde le code source dans un fichier"""
        filename = filedialog.asksaveasfilename(
            title="Sauvegarder le code source",
            defaultextension=".py",
            filetypes=[
                ("Fichiers Python", "*.py"),
                ("Tous les fichiers", "*.*")
            ]
        )
        
        if filename:
            try:
                content = self.source_text.get(1.0, tk.END)
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                messagebox.showinfo("Succès", f"Code source sauvegardé: {os.path.basename(filename)}")
                
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible de sauvegarder le fichier:\n{str(e)}")
    
    def update_preview(self):
        """Met à jour la prévisualisation du code GUI"""
        try:
            # Mise à jour de la configuration
            self.update_config_from_ui()
            
            # Récupération du code source
            source_code = self.source_text.get(1.0, tk.END)
            
            if not source_code.strip():
                self.preview_text.config(state=tk.NORMAL)
                self.preview_text.delete(1.0, tk.END)
                self.preview_text.insert(1.0, "# Aucun code source à prévisualiser")
                self.preview_text.config(state=tk.DISABLED)
                return
            
            # Génération du code GUI
            gui_code = self.template_generator.generate_gui_wrapper(source_code, self.config)
            
            # Affichage
            self.preview_text.config(state=tk.NORMAL)
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(1.0, gui_code)
            self.preview_text.config(state=tk.DISABLED)
            
            self.status_var.set("Prévisualisation mise à jour")
            
        except Exception as e:
            self.preview_text.config(state=tk.NORMAL)
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(1.0, f"# Erreur lors de la génération:\n# {str(e)}")
            self.preview_text.config(state=tk.DISABLED)
            logger.error(f"Erreur preview: {e}")
    
    def export_preview(self):
        """Exporte le code de prévisualisation"""
        filename = filedialog.asksaveasfilename(
            title="Exporter le code GUI",
            defaultextension=".py",
            initialname=f"{self.config.name}_gui.py",
            filetypes=[
                ("Fichiers Python", "*.py"),
                ("Tous les fichiers", "*.*")
            ]
        )
        
        if filename:
            try:
                # Génération du code GUI
                self.update_config_from_ui()
                source_code = self.source_text.get(1.0, tk.END)
                gui_code = self.template_generator.generate_gui_wrapper(source_code, self.config)
                
                # Sauvegarde
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(gui_code)
                
                messagebox.showinfo("Succès", f"Code GUI exporté: {os.path.basename(filename)}")
                
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible d'exporter le code:\n{str(e)}")
    
    def build_executable(self):
        """Construit l'exécutable"""
        try:
            # Vérifications préliminaires
            source_code = self.source_text.get(1.0, tk.END)
            if not source_code.strip():
                messagebox.showwarning("Attention", "Aucun code source à construire.")
                return
            
            # Mise à jour de la configuration
            self.update_config_from_ui()
            
            # Vérification des outils requis
            if not self._check_build_requirements():
                return
            
            # Interface de construction
            self.build_button.config(state=tk.DISABLED)
            self.cancel_button.config(state=tk.NORMAL)
            self.build_progress.start()
            self.progress_var.set("Construction en cours...")
            
            # Nettoyage du log
            self.build_log.delete(1.0, tk.END)
            self.build_log.insert(tk.END, f"=== Construction de {self.config.name} ===\n")
            self.build_log.insert(tk.END, f"Démarrage: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Lancement de la construction dans un thread
            build_thread = threading.Thread(target=self._build_thread, daemon=True)
            build_thread.start()
            
        except Exception as e:
            self._build_finished(False, str(e))
    
    def _check_build_requirements(self):
        """Vérifie les prérequis pour la construction"""
        try:
            # Vérification de PyInstaller
            import pyinstaller
            return True
        except ImportError:
            result = messagebox.askyesnocancel(
                "PyInstaller manquant",
                "PyInstaller n'est pas installé.\n\n"
                "Voulez-vous l'installer automatiquement?\n\n"
                "Oui: Installer automatiquement\n"
                "Non: Continuer sans installer (peut échouer)\n"
                "Annuler: Annuler la construction"
            )
            
            if result is True:  # Oui
                try:
                    self.build_log.insert(tk.END, "Installation de PyInstaller...\n")
                    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])
                    self.build_log.insert(tk.END, "PyInstaller installé avec succès.\n\n")
                    return True
                except subprocess.CalledProcessError as e:
                    messagebox.showerror("Erreur", f"Impossible d'installer PyInstaller:\n{str(e)}")
                    return False
            elif result is False:  # Non
                return True
            else:  # Annuler
                return False
    
    def _build_thread(self):
        """Thread de construction"""
        try:
            # Génération du code GUI
            source_code = self.source_text.get(1.0, tk.END)
            gui_code = self.template_generator.generate_gui_wrapper(source_code, self.config)
            
            # Création du fichier temporaire
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            temp_file = os.path.join(UPLOAD_FOLDER, f"build_{self.config.name}.py")
            
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(gui_code)
            
            self.root.after(0, lambda: self.build_log.insert(tk.END, f"Code GUI généré: {temp_file}\n"))
            
            # Construction
            os.makedirs(OUTPUT_FOLDER, exist_ok=True)
            success, result = self.builder.build_executable(temp_file, self.config, OUTPUT_FOLDER)
            
            # Nettoyage
            if os.path.exists(temp_file):
                os.remove(temp_file)
            
            # Callback sur le thread principal
            self.root.after(0, lambda: self._build_finished(success, result))
            
        except Exception as e:
            self.root.after(0, lambda: self._build_finished(False, str(e)))
    
    def _build_finished(self, success: bool, result: str):
        """Appelé quand la construction est terminée"""
        # Interface
        self.build_button.config(state=tk.NORMAL)
        self.cancel_button.config(state=tk.DISABLED)
        self.build_progress.stop()
        
        # Log
        self.build_log.insert(tk.END, f"\n=== Fin de construction ===\n")
        self.build_log.insert(tk.END, f"Terminé: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        if success:
            self.progress_var.set("Construction réussie!")
            self.build_log.insert(tk.END, f"✅ SUCCÈS: Exécutable créé\n")
            self.build_log.insert(tk.END, f"Emplacement: {result}\n")
            
            # Proposition d'ouvrir le dossier
            if messagebox.askyesno("Construction réussie", 
                                   f"Exécutable créé avec succès!\n\n"
                                   f"Emplacement: {result}\n\n"
                                   f"Voulez-vous ouvrir le dossier de sortie?"):
                try:
                    if sys.platform == "win32":
                        os.startfile(os.path.dirname(result))
                    elif sys.platform == "darwin":
                        subprocess.call(["open", os.path.dirname(result)])
                    else:
                        subprocess.call(["xdg-open", os.path.dirname(result)])
                except Exception as e:
                    logger.warning(f"Impossible d'ouvrir le dossier: {e}")
        else:
            self.progress_var.set("Construction échouée!")
            self.build_log.insert(tk.END, f"❌ ÉCHEC: {result}\n")
            messagebox.showerror("Erreur de construction", f"La construction a échoué:\n\n{result}")
        
        # Scroll vers le bas
        self.build_log.see(tk.END)
    
    def cancel_build(self):
        """Annule la construction"""
        self.builder.cancel_build()
        self._build_finished(False, "Construction annulée par l'utilisateur")
    
    def refresh_projects(self):
        """Actualise la liste des projets"""
        try:
            # Nettoyage
            for item in self.projects_tree.get_children():
                self.projects_tree.delete(item)
            
            # Rechargement
            projects = self.db.list_projects()
            for project in projects:
                created = project['created_at'][:19] if project['created_at'] else 'N/A'
                updated = project['updated_at'][:19] if project['updated_at'] else 'N/A'
                
                self.projects_tree.insert('', tk.END, text=project['name'], 
                                        values=(created, updated))
        
        except Exception as e:
            logger.error(f"Erreur actualisation projets: {e}")
    
    def load_selected_project(self):
        """Charge le projet sélectionné"""
        selection = self.projects_tree.selection()
        if selection:
            item = self.projects_tree.item(selection[0])
            project_name = item['text']
            self.load_project_by_name(project_name)
    
    def delete_selected_project(self):
        """Supprime le projet sélectionné"""
        selection = self.projects_tree.selection()
        if selection:
            item = self.projects_tree.item(selection[0])
            project_name = item['text']
            
            if messagebox.askyesno("Confirmation", 
                                 f"Voulez-vous vraiment supprimer le projet '{project_name}'?\n\n"
                                 f"Cette action est irréversible."):
                try:
                    if self.db.delete_project(project_name):
                        messagebox.showinfo("Succès", f"Projet '{project_name}' supprimé.")
                        self.refresh_projects()
                    else:
                        messagebox.showerror("Erreur", f"Impossible de supprimer le projet '{project_name}'.")
                except Exception as e:
                    messagebox.showerror("Erreur", f"Erreur lors de la suppression:\n{str(e)}")
    
    def show_documentation(self):
        """Affiche la documentation"""
        doc_window = tk.Toplevel(self.root)
        doc_window.title("Documentation")
        doc_window.geometry("800x600")
        
        doc_text = scrolledtext.ScrolledText(doc_window, wrap=tk.WORD, font=("Segoe UI", 10))
        doc_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        documentation = """
CONVERTISSEUR SCRIPT TO DESKTOP APP

Cette application permet de convertir des scripts Python en applications de bureau avec interface graphique.

=== FONCTIONNALITÉS ===

1. ANALYSE DE CODE
   • Détection automatique du framework GUI utilisé
   • Analyse de la complexité du code
   • Extraction des imports et dépendances
   • Statistiques sur le code (lignes, fonctions, classes)

2. GÉNÉRATION D'INTERFACE
   • Support multiple frameworks: Tkinter, PyQt5/6, Flask, Console
   • Templates personnalisables selon le framework
   • Interface adaptive au code source original
   • Intégration du code original dans l'interface

3. CONFIGURATION AVANCÉE
   • Métadonnées du projet (nom, version, auteur)
   • Options de construction (fichier unique, console, compression)
   • Gestion des dépendances
   • Sélection d'icône personnalisée

4. CONSTRUCTION D'EXÉCUTABLE
   • Utilisation de PyInstaller
   • Support architecture x86/x64
   • Options de compression UPX
   • Mode debug disponible
   • Journal de construction détaillé

5. GESTION DE PROJETS
   • Sauvegarde/chargement de projets
   • Base de données SQLite intégrée
   • Historique des projets
   • Export de code GUI

=== UTILISATION ===

1. CRÉER UN NOUVEAU PROJET
   • Fichier → Nouveau Projet (Ctrl+N)
   • Ou commencer avec un script existant

2. CHARGER UN SCRIPT
   • Fichier → Ouvrir Script (Ctrl+O)
   • Sélectionner un fichier .py ou .pyw
   • L'analyse se lance automatiquement

3. CONFIGURER LE PROJET
   • Onglet "Configuration"
   • Remplir les métadonnées
   • Sélectionner le framework GUI approprié
   • Ajuster les options de construction

4. PRÉVISUALISER LE CODE
   • Onglet "Prévisualisation"
   • Voir le code GUI généré
   • Exporter si nécessaire

5. CONSTRUIRE L'EXÉCUTABLE
   • Onglet "Construction"
   • Cliquer "Construire l'Exécutable"
   • Suivre le journal de construction

6. GÉRER LES PROJETS
   • Onglet "Projets"
   • Voir tous les projets sauvegardés
   • Charger/supprimer des projets

=== FRAMEWORKS SUPPORTÉS ===

• TKINTER: Interface native Python, léger, multi-plateforme
• PYQT5/6: Interface moderne et riche, nécessite installation
• FLASK: Application web, interface navigateur
• CONSOLE: Interface texte/terminal, simple et efficace

=== CONSEILS ===

• Analysez votre code avant configuration pour détecter le framework
• Testez la prévisualisation avant construction
• Gardez une sauvegarde de vos projets importants
• Vérifiez les dépendances pour éviter les erreurs de construction
• Utilisez le mode debug pour diagnostiquer les problèmes

=== RACCOURCIS CLAVIER ===

• Ctrl+N: Nouveau projet
• Ctrl+O: Ouvrir script
• Ctrl+S: Sauvegarder projet
• Ctrl+L: Charger projet
• Ctrl+E: Exporter code GUI
• F5: Construire exécutable
• F7: Analyser code
• F8: Détecter dépendances
• F9: Actualiser prévisualisation

=== DÉPANNAGE ===

Si la construction échoue:
1. Vérifiez que PyInstaller est installé
2. Contrôlez les dépendances listées
3. Essayez le mode debug
4. Consultez le journal de construction
5. Testez d'abord sans compression UPX

Pour plus d'aide, consultez les logs ou contactez le support.
        """
        
        doc_text.insert(1.0, documentation)
        doc_text.config(state=tk.DISABLED)
    
    def show_about(self):
        """Affiche la fenêtre À propos"""
        about_window = tk.Toplevel(self.root)
        about_window.title("À propos")
        about_window.geometry("500x400")
        about_window.resizable(False, False)
        
        # Logo/Titre
        title_frame = ttk.Frame(about_window)
        title_frame.pack(fill=tk.X, pady=20)
        
        title_label = tk.Label(title_frame, text="Script to Desktop App Converter", 
                              font=("Segoe UI", 16, "bold"))
        title_label.pack()
        
        version_label = tk.Label(title_frame, text="Version 2.0", 
                               font=("Segoe UI", 12))
        version_label.pack()
        
        # Information
        info_text = f"""
Convertisseur automatique de scripts Python en applications de bureau

Fonctionnalités:
• Support multi-framework (Tkinter, PyQt, Flask, Console)
• Analyse automatique du code source
• Génération d'interface graphique adaptative
• Construction d'exécutables avec PyInstaller
• Gestion de projets avec base de données SQLite
• Interface web Flask intégrée

Développé avec Python {sys.version.split()[0]}
Généré le: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

Technologies utilisées:
• Python 3.7+
• Tkinter (Interface desktop)
• Flask (Interface web)
• SQLite (Base de données)
• PyInstaller (Construction exécutables)
• AST (Analyse de code)

© 2024 - Tous droits réservés
        """
        
        info_label = tk.Label(about_window, text=info_text, justify=tk.LEFT, 
                             font=("Segoe UI", 10), wraplength=450)
        info_label.pack(expand=True, padx=20)
        
        # Bouton fermer
        ttk.Button(about_window, text="Fermer", command=about_window.destroy).pack(pady=10)
    
    def run(self):
        """Lance l'application GUI"""
        try:
            logger.info("Démarrage de l'interface Tkinter")
            self.root.mainloop()
        except Exception as e:
            logger.error(f"Erreur interface Tkinter: {e}")
            messagebox.showerror("Erreur fatale", f"Erreur critique:\n{str(e)}")

class CommandLineInterface:
    """Interface en ligne de commande"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.analyzer = CodeAnalyzer()
        self.template_generator = TemplateGenerator()
        self.builder = PyInstallerBuilder()
    
    def create_parser(self) -> argparse.ArgumentParser:
        """Crée le parser d'arguments"""
        parser = argparse.ArgumentParser(
            description="Convertit des scripts Python en applications de bureau",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Exemples:
  # Interface graphique
  python script_converter.py --gui
  
  # Interface web
  python script_converter.py --web
  
  # Conversion directe
  python script_converter.py script.py --name MonApp --framework tkinter
  
  # Avec options avancées
  python script_converter.py script.py --name MonApp --author "John Doe" --version 2.0 --onefile --no-console
  
  # Lister les projets
  python script_converter.py --list-projects
  
  # Charger et construire un projet
  python script_converter.py --load MonProjet --build
            """
        )
        
        # Arguments principaux
        parser.add_argument('source', nargs='?', help='Fichier Python source')
        parser.add_argument('--gui', action='store_true', help='Lance l\'interface graphique Tkinter')
        parser.add_argument('--web', action='store_true', help='Lance l\'interface web Flask')
        parser.add_argument('--port', type=int, default=5000, help='Port pour l\'interface web (défaut: 5000)')
        parser.add_argument('--host', default='127.0.0.1', help='Host pour l\'interface web (défaut: 127.0.0.1)')
        
        # Configuration du projet
        project_group = parser.add_argument_group('Configuration du projet')
        project_group.add_argument('--name', help='Nom du projet')
        project_group.add_argument('--description', help='Description du projet')
        project_group.add_argument('--author', default='Utilisateur', help='Auteur du projet')
        project_group.add_argument('--version', default='1.0.0', help='Version du projet')
        project_group.add_argument('--framework', choices=['tkinter', 'PyQt5', 'PyQt6', 'flask', 'console'],
                                  help='Framework GUI à utiliser')
        project_group.add_argument('--theme', default='default', help='Thème de l\'interface')
        project_group.add_argument('--icon', help='Chemin vers l\'icône (.ico)')
        
        # Options de construction
        build_group = parser.add_argument_group('Options de construction')
        build_group.add_argument('--output', default=OUTPUT_FOLDER, help='Dossier de sortie')
        build_group.add_argument('--onefile', action='store_true', help='Créer un fichier unique')
        build_group.add_argument('--onedir', dest='onefile', action='store_false', help='Créer un dossier')
        build_group.add_argument('--console', dest='no_console', action='store_false', help='Inclure la console')
        build_group.add_argument('--no-console', dest='no_console', action='store_true', help='Masquer la console')
        build_group.add_argument('--debug', action='store_true', help='Mode debug')
        build_group.add_argument('--upx', action='store_true', help='Compression UPX')
        build_group.add_argument('--arch', choices=['x86', 'x64', 'auto'], default='x64', help='Architecture cible')
        
        # Gestion des projets
        project_mgmt = parser.add_argument_group('Gestion des projets')
        project_mgmt.add_argument('--save', help='Sauvegarder le projet avec ce nom')
        project_mgmt.add_argument('--load', help='Charger un projet existant')
        project_mgmt.add_argument('--list-projects', action='store_true', help='Lister tous les projets')
        project_mgmt.add_argument('--delete-project', help='Supprimer un projet')
        
        # Actions
        action_group = parser.add_argument_group('Actions')
        action_group.add_argument('--analyze', action='store_true', help='Analyser seulement le code')
        action_group.add_argument('--preview', action='store_true', help='Générer la prévisualisation du code GUI')
        action_group.add_argument('--build', action='store_true', help='Construire l\'exécutable')
        action_group.add_argument('--export', help='Exporter le code GUI vers un fichier')
        
        # Options générales
        parser.add_argument('--verbose', '-v', action='store_true', help='Mode verbeux')
        parser.add_argument('--quiet', '-q', action='store_true', help='Mode silence')
        parser.add_argument('--log-file', help='Fichier de log')
        
        return parser
    
    def run(self, args=None):
        """Lance l'interface CLI"""
        parser = self.create_parser()
        args = parser.parse_args(args)
        
        # Configuration du logging
        if args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)
        elif args.quiet:
            logging.getLogger().setLevel(logging.ERROR)
        
        if args.log_file:
            handler = logging.FileHandler(args.log_file)
            logging.getLogger().addHandler(handler)
        
        try:
            # Interface graphique
            if args.gui:
                return self._run_gui()
            
            # Interface web
            if args.web:
                return self._run_web(args.host, args.port)
            
            # Gestion des projets
            if args.list_projects:
                return self._list_projects()
            
            if args.delete_project:
                return self._delete_project(args.delete_project)
            
            if args.load:
                return self._load_and_process_project(args)
            
            # Traitement d'un fichier source
            if args.source:
                return self._process_source_file(args)
            
            # Aucune action spécifiée
            print("Aucune action spécifiée. Utilisez --help pour voir les options.")
            print("Ou lancez l'interface graphique avec --gui")
            return 1
        
        except KeyboardInterrupt:
            print("\nInterrompu par l'utilisateur.")
            return 1
        except Exception as e:
            logger.error(f"Erreur CLI: {e}")
            if args.verbose:
                import traceback
                traceback.print_exc()
            return 1
    
    def _run_gui(self):
        """Lance l'interface graphique"""
        try:
            gui = TkinterGUI()
            gui.run()
            return 0
        except ImportError:
            print("Erreur: Tkinter n'est pas disponible.")
            return 1
    
    def _run_web(self, host, port):
        """Lance l'interface web"""
        try:
            web = FlaskWebInterface()
            print(f"Interface web disponible sur http://{host}:{port}")
            print("Appuyez sur Ctrl+C pour arrêter")
            web.run(host=host, port=port)
            return 0
        except ImportError:
            print("Erreur: Flask n'est pas disponible.")
            return 1
        except OSError as e:
            print(f"Erreur réseau: {e}")
            return 1
    
    def _list_projects(self):
        """Liste tous les projets"""
        projects = self.db.list_projects()
        
        if not projects:
            print("Aucun projet trouvé.")
            return 0
        
        print(f"{'Nom':<20} {'Créé le':<20} {'Modifié le':<20}")
        print("-" * 60)
        
        for project in projects:
            created = project['created_at'][:19] if project['created_at'] else 'N/A'
            updated = project['updated_at'][:19] if project['updated_at'] else 'N/A'
            print(f"{project['name']:<20} {created:<20} {updated:<20}")
        
        return 0
    
    def _delete_project(self, name):
        """Supprime un projet"""
        if self.db.delete_project(name):
            print(f"Projet '{name}' supprimé avec succès.")
            return 0
        else:
            print(f"Projet '{name}' introuvable.")
            return 1
    
    def _load_and_process_project(self, args):
        """Charge et traite un projet existant"""
        project_data = self.db.load_project(args.load)
        if not project_data:
            print(f"Projet '{args.load}' introuvable.")
            return 1
        
        config, source_code = project_data
        print(f"Projet '{config.name}' chargé.")
        
        # Actions sur le projet chargé
        if args.analyze:
            return self._analyze_code(source_code, config.name)
        
        if args.preview:
            return self._preview_code(source_code, config)
        
        if args.export:
            return self._export_code(source_code, config, args.export)
        
        if args.build:
            return self._build_project(source_code, config)
        
        # Affichage des informations du projet
        self._display_project_info(config)
        return 0
    
    def _process_source_file(self, args):
        """Traite un fichier source"""
        if not os.path.exists(args.source):
            print(f"Erreur: Fichier '{args.source}' introuvable.")
            return 1
        
        # Lecture du fichier source
        try:
            with open(args.source, 'r', encoding='utf-8') as f:
                source_code = f.read()
        except Exception as e:
            print(f"Erreur lecture fichier: {e}")
            return 1
        
        # Configuration du projet
        config = self._create_config_from_args(args)
        
        # Actions
        if args.analyze:
            return self._analyze_code(source_code, args.source)
        
        if args.preview:
            return self._preview_code(source_code, config)
        
        if args.export:
            return self._export_code(source_code, config, args.export)
        
        if args.save:
            self.db.save_project(config, source_code)
            print(f"Projet '{args.save}' sauvegardé.")
        
        if args.build:
            return self._build_project(source_code, config)
        
        # Par défaut, analyse seulement
        return self._analyze_code(source_code, args.source)
    
    def _create_config_from_args(self, args):
        """Crée une configuration à partir des arguments"""
        # Nom du projet
        if args.name:
            name = args.name
        elif args.source:
            name = os.path.splitext(os.path.basename(args.source))[0]
        elif args.save:
            name = args.save
        else:
            name = "MonApp"
        
        # Détection automatique du framework si non spécifiée
        framework = args.framework
        if not framework and args.source:
            # Analyse rapide pour détecter le framework
            try:
                with open(args.source, 'r', encoding='utf-8') as f:
                    temp_code = f.read()
                temp_file = os.path.join(UPLOAD_FOLDER, "temp_detect.py")
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                with open(temp_file, 'w', encoding='utf-8') as f:
                    f.write(temp_code)
                analysis = self.analyzer.analyze_file(temp_file)
                framework = analysis.get('gui_framework', 'tkinter')
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except:
                framework = 'tkinter'
        
        if not framework:
            framework = 'tkinter'
        
        return ProjectConfig(
            name=name,
            description=args.description or f"Application générée depuis {args.source or 'code'}",
            author=args.author,
            version=args.version,
            gui_framework=framework,
            theme=args.theme,
            icon_path=args.icon,
            architecture=args.arch,
            one_file=args.onefile,
            include_console=not args.no_console,
            upx_compress=args.upx,
            debug_mode=args.debug
        )
    
    def _analyze_code(self, source_code, source_name):
        """Analyse le code source"""
        print(f"\n=== ANALYSE DE {source_name} ===")
        
        # Sauvegarde temporaire pour analyse
        temp_file = os.path.join(UPLOAD_FOLDER, "temp_cli_analysis.py")
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        try:
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(source_code)
            
            analysis = self.analyzer.analyze_file(temp_file)
            
            # Affichage des résultats
            print(f"Framework GUI détecté: {analysis.get('gui_framework', 'Non détecté')}")
            print(f"Lignes de code: {analysis.get('lines_of_code', 0)}")
            print(f"Complexité cyclomatique: {analysis.get('complexity', 0)}")
            print(f"Nombre d'imports: {len(analysis.get('imports', []))}")
            print(f"Nombre de fonctions: {len(analysis.get('functions', []))}")
            print(f"Nombre de classes: {len(analysis.get('classes', []))}")
            
            imports = analysis.get('imports', [])
            if imports:
                print(f"\nImports détectés:")
                for imp in imports[:20]:  # Limite à 20 pour l'affichage
                    print(f"  • {imp}")
                if len(imports) > 20:
                    print(f"  ... et {len(imports) - 20} autres")
            
            functions = analysis.get('functions', [])
            if functions:
                print(f"\nFonctions détectées:")
                for func in functions[:10]:  # Limite à 10
                    print(f"  • {func['name']}() - ligne {func['line']}")
                if len(functions) > 10:
                    print(f"  ... et {len(functions) - 10} autres")
            
            classes = analysis.get('classes', [])
            if classes:
                print(f"\nClasses détectées:")
                for cls in classes[:10]:  # Limite à 10
                    print(f"  • {cls['name']} - ligne {cls['line']}")
                if len(classes) > 10:
                    print(f"  ... et {len(classes) - 10} autres")
            
            return 0
        
        except Exception as e:
            print(f"Erreur lors de l'analyse: {e}")
            return 1
        
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)
    
    def _preview_code(self, source_code, config):
        """Génère la prévisualisation du code GUI"""
        print(f"\n=== PRÉVISUALISATION - {config.name} ===")
        print(f"Framework: {config.gui_framework}")
        print(f"Thème: {config.theme}")
        print("=" * 60)
        
        try:
            gui_code = self.template_generator.generate_gui_wrapper(source_code, config)
            print(gui_code)
            return 0
        
        except Exception as e:
            print(f"Erreur lors de la génération: {e}")
            return 1
    
    def _export_code(self, source_code, config, export_path):
        """Exporte le code GUI vers un fichier"""
        try:
            gui_code = self.template_generator.generate_gui_wrapper(source_code, config)
            
            with open(export_path, 'w', encoding='utf-8') as f:
                f.write(gui_code)
            
            print(f"Code GUI exporté vers: {export_path}")
            return 0
        
        except Exception as e:
            print(f"Erreur lors de l'export: {e}")
            return 1
    
    def _build_project(self, source_code, config):
        """Construit l'exécutable du projet"""
        print(f"\n=== CONSTRUCTION - {config.name} ===")
        print(f"Framework: {config.gui_framework}")
        print(f"Architecture: {config.architecture}")
        print(f"Fichier unique: {config.one_file}")
        print(f"Console: {config.include_console}")
        print("=" * 50)
        
        try:
            # Génération du code GUI
            print("Génération du code GUI...")
            gui_code = self.template_generator.generate_gui_wrapper(source_code, config)
            
            # Création du fichier temporaire
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            temp_file = os.path.join(UPLOAD_FOLDER, f"build_{config.name}.py")
            
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(gui_code)
            
            print(f"Code GUI sauvegardé: {temp_file}")
            
            # Construction
            print("Construction de l'exécutable...")
            os.makedirs(OUTPUT_FOLDER, exist_ok=True)
            
            success, result = self.builder.build_executable(temp_file, config, OUTPUT_FOLDER)
            
            # Nettoyage
            if os.path.exists(temp_file):
                os.remove(temp_file)
            
            if success:
                print(f"✅ SUCCÈS: Exécutable créé")
                print(f"Emplacement: {result}")
                return 0
            else:
                print(f"❌ ÉCHEC: {result}")
                return 1
        
        except Exception as e:
            print(f"Erreur lors de la construction: {e}")
            return 1
    
    def _display_project_info(self, config):
        """Affiche les informations d'un projet"""
        print(f"\n=== INFORMATIONS PROJET ===")
        print(f"Nom: {config.name}")
        print(f"Description: {config.description}")
        print(f"Auteur: {config.author}")
        print(f"Version: {config.version}")
        print(f"Framework GUI: {config.gui_framework}")
        print(f"Thème: {config.theme}")
        print(f"Architecture: {config.architecture}")
        print(f"Fichier unique: {config.one_file}")
        print(f"Console incluse: {config.include_console}")
        print(f"Mode debug: {config.debug_mode}")
        print(f"Compression UPX: {config.upx_compress}")
        
        if config.icon_path:
            print(f"Icône: {config.icon_path}")
        
        if config.requirements:
            print(f"Dépendances ({len(config.requirements)}):")
            for req in config.requirements:
                print(f"  • {req}")
        
        print(f"Créé le: {config.created_at}")

def create_flask_templates():
    """Crée les templates Flask nécessaires"""
    templates_dir = TEMPLATES_FOLDER
    os.makedirs(templates_dir, exist_ok=True)
    
    # Template de base
    base_template = '''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Script to Desktop App Converter{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .navbar-brand { font-weight: bold; }
        .card { box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); }
        .btn-primary { background: linear-gradient(45deg, #007bff, #0056b3); }
        .code-preview { font-family: 'Courier New', monospace; font-size: 12px; }
        .build-log { background: #2d3748; color: #e2e8f0; font-family: monospace; }
        footer { margin-top: 50px; padding: 30px 0; background: #f8f9fa; }
    </style>
    {% block extra_css %}{% endblock %}
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="{{ url_for('index') }}">
                <i class="fas fa-cogs"></i> Script Converter
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav me-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('index') }}">
                            <i class="fas fa-home"></i> Accueil
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('upload_file') }}">
                            <i class="fas fa-upload"></i> Télécharger
                        </a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <!-- Messages Flash -->
    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            <div class="container mt-3">
                {% for category, message in messages %}
                    <div class="alert alert-{{ 'danger' if category == 'error' else category }} alert-dismissible fade show">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                {% endfor %}
            </div>
        {% endif %}
    {% endwith %}

    <!-- Contenu principal -->
    <main class="container my-4">
        {% block content %}{% endblock %}
    </main>

    <!-- Footer -->
    <footer class="text-center text-muted">
        <div class="container">
            <p>&copy; 2024 Script to Desktop App Converter. Généré automatiquement.</p>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    {% block extra_js %}{% endblock %}
</body>
</html>'''
    
    # Page d'accueil
    index_template = '''{% extends "base.html" %}

{% block title %}Accueil - Script Converter{% endblock %}

{% block content %}
<div class="row">
    <div class="col-lg-8 mx-auto">
        <div class="jumbotron bg-light p-5 rounded mb-4">
            <h1 class="display-4">
                <i class="fas fa-magic text-primary"></i>
                Script to Desktop App
            </h1>
            <p class="lead">
                Convertissez facilement vos scripts Python en applications de bureau avec interface graphique.
            </p>
            <hr class="my-4">
            <p>
                Supportés: Tkinter, PyQt5/6, Flask, Console. Construction automatique d'exécutables avec PyInstaller.
            </p>
            <a class="btn btn-primary btn-lg" href="{{ url_for('upload_file') }}">
                <i class="fas fa-rocket"></i> Commencer
            </a>
        </div>
    </div>
</div>

<!-- Projets récents -->
<div class="row">
    <div class="col-12">
        <div class="card">
            <div class="card-header d-flex justify-content-between align-items-center">
                <h5 class="mb-0">
                    <i class="fas fa-folder"></i> Projets Récents
                </h5>
                <a href="{{ url_for('upload_file') }}" class="btn btn-outline-primary btn-sm">
                    <i class="fas fa-plus"></i> Nouveau Projet
                </a>
            </div>
            <div class="card-body">
                {% if projects %}
                    <div class="table-responsive">
                        <table class="table table-hover">
                            <thead>
                                <tr>
                                    <th>Nom</th>
                                    <th>Créé le</th>
                                    <th>Modifié le</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for project in projects[:10] %}
                                <tr>
                                    <td>
                                        <strong>{{ project.name }}</strong>
                                    </td>
                                    <td>{{ project.created_at[:19] }}</td>
                                    <td>{{ project.updated_at[:19] }}</td>
                                    <td>
                                        <a href="{{ url_for('project_config', name=project.name) }}" 
                                           class="btn btn-sm btn-outline-primary">
                                            <i class="fas fa-edit"></i> Configurer
                                        </a>
                                        <form method="post" action="{{ url_for('delete_project', name=project.name) }}" 
                                              class="d-inline" 
                                              onsubmit="return confirm('Supprimer ce projet?')">
                                            <button type="submit" class="btn btn-sm btn-outline-danger">
                                                <i class="fas fa-trash"></i>
                                            </button>
                                        </form>
                                    </td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                {% else %}
                    <div class="text-center py-4">
                        <i class="fas fa-folder-open fa-3x text-muted mb-3"></i>
                        <h5 class="text-muted">Aucun projet trouvé</h5>
                        <p class="text-muted">Commencez par télécharger un script Python.</p>
                    </div>
                {% endif %}
            </div>
        </div>
    </div>
</div>
{% endblock %}'''
    
    # Page de téléchargement
    upload_template = '''{% extends "base.html" %}

{% block title %}Télécharger - Script Converter{% endblock %}

{% block content %}
<div class="row">
    <div class="col-lg-8 mx-auto">
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">
                    <i class="fas fa-upload"></i> Télécharger un Script Python
                </h5>
            </div>
            <div class="card-body">
                <form method="post" enctype="multipart/form-data" id="uploadForm">
                    <div class="mb-3">
                        <label for="file" class="form-label">Sélectionner un fichier Python</label>
                        <input type="file" class="form-control" id="file" name="file" 
                               accept=".py,.pyw" required>
                        <div class="form-text">
                            Formats supportés: .py, .pyw (max 50MB)
                        </div>
                    </div>
                    
                    <div class="mb-3">
                        <div class="progress" style="height: 3px; display: none;" id="uploadProgress">
                            <div class="progress-bar" role="progressbar" style="width: 0%"></div>
                        </div>
                    </div>
                    
                    <button type="submit" class="btn btn-primary" id="uploadBtn">
                        <i class="fas fa-upload"></i> Télécharger et Analyser
                    </button>
                </form>
            </div>
        </div>
        
        <!-- Aide -->
        <div class="card mt-4">
            <div class="card-header">
                <h6 class="mb-0">
                    <i class="fas fa-info-circle"></i> Guide d'utilisation
                </h6>
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-6">
                        <h6>Étapes de conversion:</h6>
                        <ol class="small">
                            <li>Téléchargez votre script Python</li>
                            <li>Configurez les options du projet</li>
                            <li>Prévisualisez le code GUI généré</li>
                            <li>Construisez l'exécutable</li>
                        </ol>
                    </div>
                    <div class="col-md-6">
                        <h6>Frameworks supportés:</h6>
                        <ul class="small">
                            <li><strong>Tkinter:</strong> Interface native Python</li>
                            <li><strong>PyQt5/6:</strong> Interface moderne</li>
                            <li><strong>Flask:</strong> Application web</li>
                            <li><strong>Console:</strong> Interface texte</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script>
document.getElementById('uploadForm').addEventListener('submit', function(e) {
    const btn = document.getElementById('uploadBtn');
    const progress = document.getElementById('uploadProgress');
    
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Téléchargement...';
    progress.style.display = 'block';
    
    // Simulation de progression (la vraie progression nécessiterait AJAX)
    let width = 0;
    const interval = setInterval(() => {
        width += 10;
        progress.querySelector('.progress-bar').style.width = width + '%';
        if (width >= 90) clearInterval(interval);
    }, 100);
});
</script>
{% endblock %}'''
    
    # Page de configuration
    config_template = '''{% extends "base.html" %}

{% block title %}Configuration - {{ config.name }}{% endblock %}

{% block content %}
<div class="row">
    <div class="col-lg-10 mx-auto">
        <div class="card">
            <div class="card-header d-flex justify-content-between align-items-center">
                <h5 class="mb-0">
                    <i class="fas fa-cog"></i> Configuration - {{ config.name }}
                </h5>
                <div>
                    <button class="btn btn-outline-secondary btn-sm" onclick="previewCode()">
                        <i class="fas fa-eye"></i> Prévisualiser
                    </button>
                    <button class="btn btn-success btn-sm" onclick="buildProject()">
                        <i class="fas fa-hammer"></i> Construire
                    </button>
                </div>
            </div>
            <div class="card-body">
                <form id="configForm">
                    <div class="row">
                        <!-- Informations générales -->
                        <div class="col-md-6">
                            <div class="card mb-3">
                                <div class="card-header">
                                    <h6 class="mb-0">Informations Générales</h6>
                                </div>
                                <div class="card-body">
                                    <div class="mb-3">
                                        <label class="form-label">Nom du projet</label>
                                        <input type="text" class="form-control" name="name" 
                                               value="{{ config.name }}" required>
                                    </div>
                                    <div class="mb-3">
                                        <label class="form-label">Description</label>
                                        <textarea class="form-control" name="description" rows="2">{{ config.description }}</textarea>
                                    </div>
                                    <div class="row">
                                        <div class="col-6">
                                            <label class="form-label">Auteur</label>
                                            <input type="text" class="form-control" name="author" 
                                                   value="{{ config.author }}">
                                        </div>
                                        <div class="col-6">
                                            <label class="form-label">Version</label>
                                            <input type="text" class="form-control" name="version" 
                                                   value="{{ config.version }}">
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Options GUI -->
                        <div class="col-md-6">
                            <div class="card mb-3">
                                <div class="card-header">
                                    <h6 class="mb-0">Interface Graphique</h6>
                                </div>
                                <div class="card-body">
                                    <div class="mb-3">
                                        <label class="form-label">Framework GUI</label>
                                        <select class="form-select" name="gui_framework">
                                            <option value="tkinter" {{ 'selected' if config.gui_framework == 'tkinter' }}>Tkinter</option>
                                            <option value="PyQt5" {{ 'selected' if config.gui_framework == 'PyQt5' }}>PyQt5</option>
                                            <option value="PyQt6" {{ 'selected' if config.gui_framework == 'PyQt6' }}>PyQt6</option>
                                            <option value="flask" {{ 'selected' if config.gui_framework == 'flask' }}>Flask (Web)</option>
                                            <option value="console" {{ 'selected' if config.gui_framework == 'console' }}>Console</option>
                                        </select>
                                    </div>
                                    <div class="mb-3">
                                        <label class="form-label">Thème</label>
                                        <select class="form-select" name="theme">
                                            <option value="default" {{ 'selected' if config.theme == 'default' }}>Défaut</option>
                                            <option value="dark" {{ 'selected' if config.theme == 'dark' }}>Sombre</option>
                                            <option value="light" {{ 'selected' if config.theme == 'light' }}>Clair</option>
                                            <option value="modern" {{ 'selected' if config.theme == 'modern' }}>Moderne</option>
                                        </select>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Options de construction -->
                    <div class="card mb-3">
                        <div class="card-header">
                            <h6 class="mb-0">Options de Construction</h6>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="form-check mb-2">
                                        <input class="form-check-input" type="checkbox" name="one_file" 
                                               {{ 'checked' if config.one_file }}>
                                        <label class="form-check-label">Fichier unique (.exe)</label>
                                    </div>
                                    <div class="form-check mb-2">
                                        <input class="form-check-input" type="checkbox" name="include_console" 
                                               {{ 'checked' if config.include_console }}>
                                        <label class="form-check-label">Inclure la console</label>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="form-check mb-2">
                                        <input class="form-check-input" type="checkbox" name="upx_compress" 
                                               {{ 'checked' if config.upx_compress }}>
                                        <label class="form-check-label">Compression UPX</label>
                                    </div>
                                    <div class="form-check mb-2">
                                        <input class="form-check-input" type="checkbox" name="debug_mode" 
                                               {{ 'checked' if config.debug_mode }}>
                                        <label class="form-check-label">Mode debug</label>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </form>
                
                <!-- Code source -->
                <div class="card">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <h6 class="mb-0">Code Source</h6>
                        <small class="text-muted">{{ source_code.count('\n') + 1 }} lignes</small>
                    </div>
                    <div class="card-body">
                        <pre class="code-preview bg-light p-3" style="max-height: 300px; overflow-y: auto;"><code>{{ source_code[:2000] }}{% if source_code|length > 2000 %}...{% endif %}</code></pre>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Modal de prévisualisation -->
<div class="modal fade" id="previewModal" tabindex="-1">
    <div class="modal-dialog modal-xl">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Prévisualisation du Code GUI</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <pre id="previewCode" class="code-preview bg-dark text-light p-3" style="max-height: 600px; overflow: auto;"></pre>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Fermer</button>
                <button type="button" class="btn btn-primary" onclick="downloadPreview()">
                    <i class="fas fa-download"></i> Télécharger
                </button>
            </div>
        </div>
    </div>
</div>

<!-- Modal de construction -->
<div class="modal fade" id="buildModal" tabindex="-1">
    <div class="modal-dialog modal-lg">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Construction en cours</h5>
            </div>
            <div class="modal-body">
                <div class="mb-3">
                    <div class="progress">
                        <div class="progress-bar progress-bar-striped progress-bar-animated" 
                             role="progressbar" style="width: 100%"></div>
                    </div>
                </div>
                <div id="buildStatus" class="alert alert-info">
                    <i class="fas fa-spinner fa-spin"></i> Préparation de la construction...
                </div>
                <div id="buildResult" style="display: none;"></div>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal" id="closeBuildModal">Fermer</button>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script>
function previewCode() {
    fetch(`/preview/{{ config.name }}`)
        .then(response => response.json())
        .then(data => {
            if (data.code) {
                document.getElementById('previewCode').textContent = data.code;
                new bootstrap.Modal(document.getElementById('previewModal')).show();
            } else {
                alert('Erreur: ' + (data.error || 'Impossible de générer la prévisualisation'));
            }
        })
        .catch(error => alert('Erreur réseau: ' + error));
}

function buildProject() {
    const form = document.getElementById('configForm');
    const formData = new FormData(form);
    
    // Afficher le modal de construction
    const buildModal = new bootstrap.Modal(document.getElementById('buildModal'));
    buildModal.show();
    
    // Lancer la construction
    fetch(`/build/{{ config.name }}`, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        const statusDiv = document.getElementById('buildStatus');
        const resultDiv = document.getElementById('buildResult');
        
        if (data.success) {
            statusDiv.className = 'alert alert-success';
            statusDiv.innerHTML = '<i class="fas fa-check"></i> Construction réussie!';
            resultDiv.innerHTML = `
                <div class="alert alert-success">
                    <h6>Exécutable créé avec succès!</h6>
                    <p>Emplacement: <code>${data.path}</code></p>
                    <a href="/download/${encodeURIComponent(data.path)}" class="btn btn-primary btn-sm">
                        <i class="fas fa-download"></i> Télécharger
                    </a>
                </div>
            `;
        } else {
            statusDiv.className = 'alert alert-danger';
            statusDiv.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Construction échouée!';
            resultDiv.innerHTML = `
                <div class="alert alert-danger">
                    <h6>Erreur de construction:</h6>
                    <pre class="small">${data.error}</pre>
                </div>
            `;
        }
        
        resultDiv.style.display = 'block';
        document.getElementById('closeBuildModal').textContent = 'Fermer';
    })
    .catch(error => {
        document.getElementById('buildStatus').className = 'alert alert-danger';
        document.getElementById('buildStatus').innerHTML = '<i class="fas fa-exclamation-triangle"></i> Erreur réseau: ' + error;
        document.getElementById('closeBuildModal').textContent = 'Fermer';
    });
}

function downloadPreview() {
    const code = document.getElementById('previewCode').textContent;
    const blob = new Blob([code], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = '{{ config.name }}_gui.py';
    a.click();
    window.URL.revokeObjectURL(url);
}
</script>
{% endblock %}'''
    
    # Template À propos
    about_template = '''{% extends "base.html" %}

{% block title %}À propos - {{ app_name }}{% endblock %}

{% block content %}
<div class="row">
    <div class="col-lg-8 mx-auto">
        <div class="card">
            <div class="card-header text-center">
                <h4>{{ app_name }}</h4>
                <p class="text-muted mb-0">Version {{ version }}</p>
            </div>
            <div class="card-body">
                <div class="text-center mb-4">
                    <i class="fas fa-cogs fa-4x text-primary mb-3"></i>
                    <h5>Convertisseur Script vers Application Desktop</h5>
                    <p class="text-muted">{{ description }}</p>
                </div>
                
                <div class="row">
                    <div class="col-md-6">
                        <h6><i class="fas fa-user"></i> Auteur</h6>
                        <p>{{ author }}</p>
                        
                        <h6><i class="fas fa-calendar"></i> Généré le</h6>
                        <p>{{ moment().format('DD/MM/YYYY HH:mm') }}</p>
                    </div>
                    <div class="col-md-6">
                        <h6><i class="fas fa-code"></i> Technologies</h6>
                        <ul class="list-unstyled">
                            <li>• Python 3.7+</li>
                            <li>• Flask (Interface web)</li>
                            <li>• SQLite (Base de données)</li>
                            <li>• PyInstaller (Exécutables)</li>
                            <li>• Bootstrap 5 (UI)</li>
                        </ul>
                    </div>
                </div>
                
                <hr>
                
                <div class="row">
                    <div class="col-12">
                        <h6><i class="fas fa-star"></i> Fonctionnalités</h6>
                        <div class="row">
                            <div class="col-md-6">
                                <ul class="list-unstyled">
                                    <li>✅ Support multi-framework</li>
                                    <li>✅ Analyse automatique du code</li>
                                    <li>✅ Génération d'interface adaptative</li>
                                    <li>✅ Construction d'exécutables</li>
                                </ul>
                            </div>
                            <div class="col-md-6">
                                <ul class="list-unstyled">
                                    <li>✅ Gestion de projets</li>
                                    <li>✅ Interface web responsive</li>
                                    <li>✅ Prévisualisation de code</li>
                                    <li>✅ Export et téléchargement</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="card-footer text-center text-muted">
                <small>© 2024 - Script to Desktop App Converter</small>
            </div>
        </div>
    </div>
</div>
{% endblock %}'''
    
    # Sauvegarde des templates
    templates = {
        'base.html': base_template,
        'index.html': index_template,
        'upload.html': upload_template,
        'project_config.html': config_template,
        'about.html': about_template
    }
    
    for filename, content in templates.items():
        filepath = os.path.join(templates_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    
    logger.info(f"Templates Flask créés dans {templates_dir}")

def create_static_files():
    """Crée les fichiers statiques nécessaires"""
    static_dir = STATIC_FOLDER
    os.makedirs(static_dir, exist_ok=True)
    
    # CSS personnalisé
    custom_css = '''/* Styles personnalisés pour Script Converter */

.navbar-brand {
    font-weight: 700;
    letter-spacing: 0.5px;
}

.card {
    border: none;
    box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
    transition: all 0.15s ease-in-out;
}

.card:hover {
    box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
}

.btn-primary {
    background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
    border: none;
    font-weight: 500;
}

.btn-primary:hover {
    background: linear-gradient(135deg, #0056b3 0%, #004085 100%);
    transform: translateY(-1px);
}

.jumbotron {
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    border-left: 4px solid #007bff;
}

.code-preview {
    font-family: 'Fira Code', 'Courier New', monospace;
    font-size: 13px;
    line-height: 1.4;
    border-radius: 8px;
}

.build-log {
    background: #1a1a1a;
    color: #00ff00;
    font-family: 'Fira Code', monospace;
    font-size: 12px;
    border-radius: 8px;
    padding: 1rem;
}

.progress {
    height: 8px;
    border-radius: 4px;
    overflow: hidden;
}

.progress-bar {
    background: linear-gradient(90deg, #007bff, #00d4aa);
}

.modal-xl .modal-body {
    max-height: 70vh;
    overflow-y: auto;
}

.table th {
    font-weight: 600;
    color: #495057;
    border-top: none;
}

.alert {
    border: none;
    border-radius: 8px;
}

.alert-success {
    background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
    color: #155724;
}

.alert-danger {
    background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
    color: #721c24;
}

.alert-info {
    background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%);
    color: #0c5460;
}

footer {
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    border-top: 1px solid #dee2e6;
}

/* Animations */
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.card {
    animation: fadeInUp 0.5s ease-out;
}

/* Responsive */
@media (max-width: 768px) {
    .jumbotron {
        padding: 2rem 1rem;
    }
    
    .display-4 {
        font-size: 2rem;
    }
    
    .code-preview {
        font-size: 11px;
    }
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
    .bg-light {
        background-color: #343a40 !important;
    }
    
    .text-muted {
        color: #adb5bd !important;
    }
}

/* Loading spinner */
.spinner-border-sm {
    width: 1rem;
    height: 1rem;
}

/* Custom scrollbar */
.code-preview::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

.code-preview::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 4px;
}

.code-preview::-webkit-scrollbar-thumb {
    background: #c1c1c1;
    border-radius: 4px;
}

.code-preview::-webkit-scrollbar-thumb:hover {
    background: #a8a8a8;
}'''
    
    # JavaScript personnalisé
    custom_js = '''/* JavaScript personnalisé pour Script Converter */

// Utilitaires généraux
const utils = {
    // Afficher un toast de notification
    showToast(message, type = 'info') {
        const toastContainer = document.getElementById('toastContainer') || this.createToastContainer();
        const toast = this.createToast(message, type);
        toastContainer.appendChild(toast);
        
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        // Suppression automatique après affichage
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    },
    
    createToastContainer() {
        const container = document.createElement('div');
        container.id = 'toastContainer';
        container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        container.style.zIndex = '1055';
        document.body.appendChild(container);
        return container;
    },
    
    createToast(message, type) {
        const toast = document.createElement('div');
        toast.className = 'toast';
        toast.setAttribute('role', 'alert');
        
        const iconMap = {
            'success': 'fas fa-check-circle text-success',
            'error': 'fas fa-exclamation-circle text-danger',
            'warning': 'fas fa-exclamation-triangle text-warning',
            'info': 'fas fa-info-circle text-info'
        };
        
        toast.innerHTML = `
            <div class="toast-header">
                <i class="${iconMap[type] || iconMap.info}"></i>
                <strong class="me-auto ms-2">Notification</strong>
                <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        `;
        
        return toast;
    },
    
    // Copier du texte dans le presse-papiers
    async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            this.showToast('Copié dans le presse-papiers!', 'success');
        } catch (err) {
            this.showToast('Erreur lors de la copie', 'error');
        }
    },
    
    // Formater la taille de fichier
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },
    
    // Debounce function
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
};

// Gestion des formulaires
const formManager = {
    // Validation côté client
    validateForm(form) {
        const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
        let isValid = true;
        
        inputs.forEach(input => {
            if (!input.value.trim()) {
                this.showFieldError(input, 'Ce champ est requis');
                isValid = false;
            } else {
                this.clearFieldError(input);
            }
        });
        
        return isValid;
    },
    
    showFieldError(input, message) {
        input.classList.add('is-invalid');
        
        let feedback = input.parentNode.querySelector('.invalid-feedback');
        if (!feedback) {
            feedback = document.createElement('div');
            feedback.className = 'invalid-feedback';
            input.parentNode.appendChild(feedback);
        }
        feedback.textContent = message;
    },
    
    clearFieldError(input) {
        input.classList.remove('is-invalid');
        const feedback = input.parentNode.querySelector('.invalid-feedback');
        if (feedback) {
            feedback.remove();
        }
    },
    
    // Sauvegarde automatique
    enableAutoSave(form, callback, delay = 2000) {
        const inputs = form.querySelectorAll('input, select, textarea');
        const debouncedSave = utils.debounce(callback, delay);
        
        inputs.forEach(input => {
            input.addEventListener('input', debouncedSave);
            input.addEventListener('change', debouncedSave);
        });
    }
};

// Gestion des fichiers
const fileManager = {
    // Validation de fichier
    validateFile(file, maxSize = 50 * 1024 * 1024, allowedTypes = ['.py', '.pyw']) {
        if (!file) {
            return { valid: false, error: 'Aucun fichier sélectionné' };
        }
        
        if (file.size > maxSize) {
            return { valid: false, error: `Fichier trop volumineux (max ${utils.formatFileSize(maxSize)})` };
        }
        
        const extension = '.' + file.name.split('.').pop().toLowerCase();
        if (!allowedTypes.includes(extension)) {
            return { valid: false, error: `Type de fichier non autorisé (${allowedTypes.join(', ')})` };
        }
        
        return { valid: true };
    },
    
    // Lecture de fichier
    readFileAsText(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = e => resolve(e.target.result);
            reader.onerror = e => reject(e);
            reader.readAsText(file, 'utf-8');
        });
    },
    
    // Téléchargement de fichier
    downloadText(content, filename) {
        const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    }
};

// Gestionnaire d'API
const apiManager = {
    async request(url, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
            ...options
        };
        
        try {
            const response = await fetch(url, defaultOptions);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            } else {
                return await response.text();
            }
        } catch (error) {
            utils.showToast(`Erreur API: ${error.message}`, 'error');
            throw error;
        }
    },
    
    async get(url) {
        return this.request(url, { method: 'GET' });
    },
    
    async post(url, data) {
        return this.request(url, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },
    
    async postForm(url, formData) {
        return this.request(url, {
            method: 'POST',
            headers: {}, // Laisser le navigateur définir Content-Type pour FormData
            body: formData
        });
    }
};

// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', function() {
    // Initialiser les tooltips Bootstrap
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialiser les popovers Bootstrap
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Améliorer les formulaires de téléchargement
    const uploadForms = document.querySelectorAll('form[enctype="multipart/form-data"]');
    uploadForms.forEach(form => {
        const fileInput = form.querySelector('input[type="file"]');
        if (fileInput) {
            fileInput.addEventListener('change', function(e) {
                const file = e.target.files[0];
                if (file) {
                    const validation = fileManager.validateFile(file);
                    if (!validation.valid) {
                        utils.showToast(validation.error, 'error');
                        e.target.value = '';
                        return;
                    }
                    
                    // Afficher les informations du fichier
                    const info = `Fichier: ${file.name} (${utils.formatFileSize(file.size)})`;
                    utils.showToast(info, 'info');
                }
            });
        }
    });
    
    // Améliorer les zones de code
    const codeBlocks = document.querySelectorAll('.code-preview');
    codeBlocks.forEach(block => {
        // Ajouter un bouton de copie
        if (block.textContent.trim()) {
            const copyBtn = document.createElement('button');
            copyBtn.className = 'btn btn-sm btn-outline-secondary position-absolute';
            copyBtn.style.top = '10px';
            copyBtn.style.right = '10px';
            copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
            copyBtn.title = 'Copier le code';
            
            const container = block.parentNode;
            if (container.style.position !== 'relative') {
                container.style.position = 'relative';
            }
            container.appendChild(copyBtn);
            
            copyBtn.addEventListener('click', () => {
                utils.copyToClipboard(block.textContent);
            });
        }
    });
    
    // Gestion des erreurs globales
    window.addEventListener('error', function(e) {
        console.error('Erreur JavaScript:', e.error);
        utils.showToast('Une erreur inattendue s\'est produite', 'error');
    });
    
    // Gestion des promesses rejetées
    window.addEventListener('unhandledrejection', function(e) {
        console.error('Promesse rejetée:', e.reason);
        utils.showToast('Erreur de réseau ou de traitement', 'error');
    });
});

// Fonctions utilitaires spécifiques à l'application
window.ScriptConverter = {
    utils,
    formManager,
    fileManager,
    apiManager
};'''
    
    # Sauvegarde des fichiers statiques
    static_files = {
        'style.css': custom_css,
        'script.js': custom_js
    }
    
    for filename, content in static_files.items():
        filepath = os.path.join(static_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    
    logger.info(f"Fichiers statiques créés dans {static_dir}")

def setup_directories():
    """Configure tous les répertoires nécessaires"""
    directories = [
        UPLOAD_FOLDER,
        TEMPLATES_FOLDER,
        STATIC_FOLDER,
        OUTPUT_FOLDER
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Répertoire créé/vérifié: {directory}")

def main():
    """Point d'entrée principal du programme"""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    SCRIPT TO DESKTOP APP CONVERTER v2.0                      ║
║                  Convertisseur Python vers Applications GUI                  ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Fonctionnalités:                                                            ║
║  • Support multi-framework (Tkinter, PyQt5/6, Flask, Console)               ║
║  • Analyse automatique du code source                                       ║
║  • Génération d'interface graphique adaptative                              ║
║  • Construction d'exécutables avec PyInstaller                              ║
║  • Interface graphique Tkinter + Interface web Flask                        ║
║  • Gestion de projets avec base de données SQLite                           ║
║                                                                              ║
║  Utilisation:                                                               ║
║  python script_converter.py --gui      # Interface graphique                ║
║  python script_converter.py --web      # Interface web (port 5000)          ║
║  python script_converter.py script.py  # Conversion directe                 ║
║  python script_converter.py --help     # Aide complète                      ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    try:
        # Configuration des répertoires
        setup_directories()
        
        # Création des templates et fichiers statiques
        create_flask_templates()
        create_static_files()
        
        # Interface en ligne de commande
        cli = CommandLineInterface()
        return cli.run()
        
    except KeyboardInterrupt:
        print("\n\nArrêt demandé par l'utilisateur.")
        return 0
    except Exception as e:
        logger.error(f"Erreur fatale: {e}")
        print(f"\n❌ ERREUR FATALE: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
