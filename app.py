#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
app.py
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
                                   command=self.run_original_code)
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
        about_text = f"""
{config.name}
Version: {config.version}
Auteur: {config.author}
Description: {config.description}

Application generee automatiquement
Date de generation: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

Framework GUI: Tkinter
Architecture: {config.architecture}
Mode Debug: {"Active" if config.debug_mode else "Desactive"}

(c) {datetime.now().year} - Tous droits reserves
        """
        
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
        return original_code
    
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
        help_text = f"""
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
        self.code_editor.setPlainText(original_code)
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
            original_code = "{original_code}"
            
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
        
        original_code = "{original_code}"
        
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
║  • Interface web Flask                                                       ║
║  • Gestion de projets avec base de données SQLite                           ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    try:
        # Configuration des répertoires
        setup_directories()
        
        # Interface web Flask
        web = FlaskWebInterface()
        print("Interface web disponible sur http://127.0.0.1:5000")
        print("Appuyez sur Ctrl+C pour arrêter")
        web.run(host='127.0.0.1', port=5000, debug=True)
        
    except KeyboardInterrupt:
        print("\n\nArrêt demandé par l'utilisateur.")
        return 0
    except Exception as e:
        logger.error(f"Erreur fatale: {e}")
        print(f"\n❌ ERREUR FATALE: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())