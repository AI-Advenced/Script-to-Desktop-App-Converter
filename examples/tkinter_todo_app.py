#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Application TODO avec Tkinter
Démontre la conversion d'une app Tkinter existante
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import datetime
from typing import List, Dict

class TodoApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Todo App - Gestionnaire de Tâches")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # Données
        self.tasks = []
        self.current_file = None
        
        # Interface
        self.setup_ui()
        self.setup_menus()
        
        # Chargement automatique
        self.load_default_tasks()
    
    def setup_ui(self):
        """Configure l'interface utilisateur"""
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Titre
        title_label = ttk.Label(main_frame, text="📝 Gestionnaire de Tâches", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Frame pour ajouter une tâche
        add_frame = ttk.LabelFrame(main_frame, text="Ajouter une tâche")
        add_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Champs de saisie
        input_frame = ttk.Frame(add_frame)
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(input_frame, text="Tâche:").grid(row=0, column=0, sticky="w", padx=(0, 5))
        self.task_entry = ttk.Entry(input_frame, width=30)
        self.task_entry.grid(row=0, column=1, sticky="ew", padx=(0, 5))
        
        ttk.Label(input_frame, text="Priorité:").grid(row=0, column=2, sticky="w", padx=(5, 5))
        self.priority_combo = ttk.Combobox(input_frame, values=["Faible", "Moyenne", "Élevée"], 
                                          state="readonly", width=10)
        self.priority_combo.set("Moyenne")
        self.priority_combo.grid(row=0, column=3, padx=(0, 5))
        
        self.add_button = ttk.Button(input_frame, text="➕ Ajouter", command=self.add_task)
        self.add_button.grid(row=0, column=4, padx=(5, 0))
        
        input_frame.columnconfigure(1, weight=1)
        
        # Bind Enter pour ajouter
        self.task_entry.bind("<Return>", lambda e: self.add_task())
        
        # Frame pour les filtres
        filter_frame = ttk.Frame(main_frame)
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(filter_frame, text="Filtrer:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.filter_var = tk.StringVar(value="Toutes")
        filter_combo = ttk.Combobox(filter_frame, textvariable=self.filter_var,
                                   values=["Toutes", "En cours", "Terminées", "Faible", "Moyenne", "Élevée"],
                                   state="readonly", width=15)
        filter_combo.pack(side=tk.LEFT, padx=(0, 10))
        filter_combo.bind("<<ComboboxSelected>>", self.filter_tasks)
        
        # Boutons d'action
        ttk.Button(filter_frame, text="✅ Marquer terminée", 
                  command=self.mark_complete).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(filter_frame, text="🗑️ Supprimer", 
                  command=self.delete_task).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(filter_frame, text="✏️ Modifier", 
                  command=self.edit_task).pack(side=tk.LEFT, padx=(0, 5))
        
        # Liste des tâches
        list_frame = ttk.LabelFrame(main_frame, text="Liste des tâches")
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview avec scrollbar
        tree_frame = ttk.Frame(list_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Définition des colonnes
        columns = ("ID", "Tâche", "Priorité", "Statut", "Créée le")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        
        # Configuration des colonnes
        self.tree.heading("ID", text="ID")
        self.tree.heading("Tâche", text="Tâche")
        self.tree.heading("Priorité", text="Priorité")
        self.tree.heading("Statut", text="Statut")
        self.tree.heading("Créée le", text="Créée le")
        
        self.tree.column("ID", width=50, minwidth=50)
        self.tree.column("Tâche", width=300, minwidth=200)
        self.tree.column("Priorité", width=100, minwidth=80)
        self.tree.column("Statut", width=100, minwidth=80)
        self.tree.column("Créée le", width=150, minwidth=120)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Double-clic pour modifier
        self.tree.bind("<Double-1>", lambda e: self.edit_task())
        
        # Frame de statistiques
        stats_frame = ttk.Frame(main_frame)
        stats_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.stats_label = ttk.Label(stats_frame, text="", font=("Arial", 9))
        self.stats_label.pack()
    
    def setup_menus(self):
        """Configure les menus"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menu Fichier
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Fichier", menu=file_menu)
        file_menu.add_command(label="Nouveau", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Ouvrir...", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Sauvegarder", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Sauvegarder sous...", command=self.save_as_file)
        file_menu.add_separator()
        file_menu.add_command(label="Quitter", command=self.quit_app, accelerator="Ctrl+Q")
        
        # Menu Édition
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Édition", menu=edit_menu)
        edit_menu.add_command(label="Ajouter tâche", command=self.add_task, accelerator="Ctrl+A")
        edit_menu.add_command(label="Modifier tâche", command=self.edit_task, accelerator="F2")
        edit_menu.add_command(label="Supprimer tâche", command=self.delete_task, accelerator="Suppr")
        edit_menu.add_separator()
        edit_menu.add_command(label="Marquer terminée", command=self.mark_complete, accelerator="Ctrl+M")
        edit_menu.add_command(label="Tout sélectionner", command=self.select_all, accelerator="Ctrl+A")
        
        # Menu Affichage
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Affichage", menu=view_menu)
        view_menu.add_command(label="Actualiser", command=self.refresh_display, accelerator="F5")
        view_menu.add_separator()
        view_menu.add_command(label="Statistiques", command=self.show_statistics)
        
        # Menu Aide
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Aide", menu=help_menu)
        help_menu.add_command(label="Aide", command=self.show_help, accelerator="F1")
        help_menu.add_command(label="À propos", command=self.show_about)
        
        # Raccourcis clavier
        self.root.bind("<Control-n>", lambda e: self.new_file())
        self.root.bind("<Control-o>", lambda e: self.open_file())
        self.root.bind("<Control-s>", lambda e: self.save_file())
        self.root.bind("<Control-q>", lambda e: self.quit_app())
        self.root.bind("<Control-a>", lambda e: self.add_task())
        self.root.bind("<Control-m>", lambda e: self.mark_complete())
        self.root.bind("<F2>", lambda e: self.edit_task())
        self.root.bind("<Delete>", lambda e: self.delete_task())
        self.root.bind("<F5>", lambda e: self.refresh_display())
        self.root.bind("<F1>", lambda e: self.show_help())
    
    def add_task(self):
        """Ajoute une nouvelle tâche"""
        task_text = self.task_entry.get().strip()
        if not task_text:
            messagebox.showwarning("Attention", "Veuillez saisir une tâche.")
            return
        
        task = {
            "id": len(self.tasks) + 1,
            "text": task_text,
            "priority": self.priority_combo.get(),
            "completed": False,
            "created_at": datetime.datetime.now().isoformat(),
            "completed_at": None
        }
        
        self.tasks.append(task)
        self.task_entry.delete(0, tk.END)
        self.refresh_display()
        
        # Focus sur le champ de saisie
        self.task_entry.focus()
    
    def mark_complete(self):
        """Marque la tâche sélectionnée comme terminée"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner une tâche.")
            return
        
        item = selection[0]
        task_id = int(self.tree.item(item)["values"][0])
        
        for task in self.tasks:
            if task["id"] == task_id:
                task["completed"] = not task["completed"]
                task["completed_at"] = datetime.datetime.now().isoformat() if task["completed"] else None
                break
        
        self.refresh_display()
    
    def delete_task(self):
        """Supprime la tâche sélectionnée"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner une tâche.")
            return
        
        item = selection[0]
        task_text = self.tree.item(item)["values"][1]
        
        if not messagebox.askyesno("Confirmation", f"Supprimer la tâche '{task_text}' ?"):
            return
        
        task_id = int(self.tree.item(item)["values"][0])
        self.tasks = [task for task in self.tasks if task["id"] != task_id]
        self.refresh_display()
    
    def edit_task(self):
        """Modifie la tâche sélectionnée"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner une tâche.")
            return
        
        item = selection[0]
        values = self.tree.item(item)["values"]
        task_id = int(values[0])
        current_text = values[1]
        current_priority = values[2]
        
        # Fenêtre de modification
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Modifier la tâche")
        edit_window.geometry("400x200")
        edit_window.transient(self.root)
        edit_window.grab_set()
        
        # Centrer la fenêtre
        edit_window.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
        
        ttk.Label(edit_window, text="Texte de la tâche:").pack(pady=5)
        text_entry = ttk.Entry(edit_window, width=50)
        text_entry.pack(pady=5, padx=10)
        text_entry.insert(0, current_text)
        
        ttk.Label(edit_window, text="Priorité:").pack(pady=5)
        priority_combo = ttk.Combobox(edit_window, values=["Faible", "Moyenne", "Élevée"], 
                                     state="readonly")
        priority_combo.pack(pady=5)
        priority_combo.set(current_priority)
        
        def save_changes():
            new_text = text_entry.get().strip()
            if not new_text:
                messagebox.showwarning("Attention", "Le texte ne peut pas être vide.")
                return
            
            for task in self.tasks:
                if task["id"] == task_id:
                    task["text"] = new_text
                    task["priority"] = priority_combo.get()
                    break
            
            edit_window.destroy()
            self.refresh_display()
        
        button_frame = ttk.Frame(edit_window)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="Sauvegarder", command=save_changes).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Annuler", command=edit_window.destroy).pack(side=tk.LEFT, padx=5)
        
        text_entry.focus()
        text_entry.select_range(0, tk.END)
    
    def filter_tasks(self, event=None):
        """Filtre les tâches selon le critère sélectionné"""
        self.refresh_display()
    
    def refresh_display(self):
        """Met à jour l'affichage de la liste"""
        # Vider la liste
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Filtrer les tâches
        filter_value = self.filter_var.get()
        filtered_tasks = []
        
        for task in self.tasks:
            if filter_value == "Toutes":
                filtered_tasks.append(task)
            elif filter_value == "En cours" and not task["completed"]:
                filtered_tasks.append(task)
            elif filter_value == "Terminées" and task["completed"]:
                filtered_tasks.append(task)
            elif filter_value in ["Faible", "Moyenne", "Élevée"] and task["priority"] == filter_value:
                filtered_tasks.append(task)
        
        # Ajouter les tâches filtrées
        for task in filtered_tasks:
            status = "✅ Terminée" if task["completed"] else "⏳ En cours"
            created_date = datetime.datetime.fromisoformat(task["created_at"]).strftime("%d/%m/%Y %H:%M")
            
            # Couleur selon priorité
            tags = []
            if task["priority"] == "Élevée":
                tags.append("high_priority")
            elif task["priority"] == "Faible":
                tags.append("low_priority")
            
            if task["completed"]:
                tags.append("completed")
            
            self.tree.insert("", "end", values=(
                task["id"], 
                task["text"], 
                task["priority"], 
                status, 
                created_date
            ), tags=tags)
        
        # Configuration des couleurs
        self.tree.tag_configure("high_priority", background="#ffebee")
        self.tree.tag_configure("low_priority", background="#e8f5e8")
        self.tree.tag_configure("completed", foreground="#888888")
        
        # Mise à jour des statistiques
        self.update_statistics()
    
    def update_statistics(self):
        """Met à jour les statistiques"""
        total = len(self.tasks)
        completed = len([t for t in self.tasks if t["completed"]])
        pending = total - completed
        
        if total > 0:
            completion_rate = (completed / total) * 100
            stats_text = f"Total: {total} | Terminées: {completed} | En cours: {pending} | Progression: {completion_rate:.1f}%"
        else:
            stats_text = "Aucune tâche enregistrée"
        
        self.stats_label.config(text=stats_text)
    
    def load_default_tasks(self):
        """Charge des tâches par défaut"""
        default_tasks = [
            {"text": "Apprendre Python", "priority": "Élevée"},
            {"text": "Faire les courses", "priority": "Moyenne"},
            {"text": "Appeler le médecin", "priority": "Élevée"},
            {"text": "Lire un livre", "priority": "Faible"},
            {"text": "Nettoyer la maison", "priority": "Moyenne"}
        ]
        
        for i, task_data in enumerate(default_tasks):
            task = {
                "id": i + 1,
                "text": task_data["text"],
                "priority": task_data["priority"],
                "completed": False,
                "created_at": datetime.datetime.now().isoformat(),
                "completed_at": None
            }
            self.tasks.append(task)
        
        self.refresh_display()
    
    def new_file(self):
        """Nouveau fichier"""
        if messagebox.askyesno("Nouveau", "Voulez-vous créer une nouvelle liste de tâches?\nToutes les tâches actuelles seront perdues."):
            self.tasks.clear()
            self.current_file = None
            self.root.title("Todo App - Gestionnaire de Tâches")
            self.refresh_display()
    
    def open_file(self):
        """Ouvre un fichier JSON"""
        filename = filedialog.askopenfilename(
            title="Ouvrir une liste de tâches",
            filetypes=[("Fichiers JSON", "*.json"), ("Tous les fichiers", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    self.tasks = json.load(f)
                
                self.current_file = filename
                self.root.title(f"Todo App - {filename}")
                self.refresh_display()
                messagebox.showinfo("Succès", f"Fichier chargé: {filename}")
                
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible d'ouvrir le fichier:\n{str(e)}")
    
    def save_file(self):
        """Sauvegarde le fichier actuel"""
        if self.current_file:
            self._save_to_file(self.current_file)
        else:
            self.save_as_file()
    
    def save_as_file(self):
        """Sauvegarde sous un nouveau nom"""
        filename = filedialog.asksaveasfilename(
            title="Sauvegarder la liste de tâches",
            defaultextension=".json",
            filetypes=[("Fichiers JSON", "*.json"), ("Tous les fichiers", "*.*")]
        )
        
        if filename:
            self._save_to_file(filename)
    
    def _save_to_file(self, filename):
        """Sauvegarde dans un fichier"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.tasks, f, indent=2, ensure_ascii=False)
            
            self.current_file = filename
            self.root.title(f"Todo App - {filename}")
            messagebox.showinfo("Succès", f"Fichier sauvegardé: {filename}")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de sauvegarder le fichier:\n{str(e)}")
    
    def select_all(self):
        """Sélectionne toutes les tâches"""
        for item in self.tree.get_children():
            self.tree.selection_add(item)
    
    def show_statistics(self):
        """Affiche les statistiques détaillées"""
        total = len(self.tasks)
        if total == 0:
            messagebox.showinfo("Statistiques", "Aucune tâche enregistrée.")
            return
        
        completed = len([t for t in self.tasks if t["completed"]])
        pending = total - completed
        
        high_priority = len([t for t in self.tasks if t["priority"] == "Élevée"])
        medium_priority = len([t for t in self.tasks if t["priority"] == "Moyenne"])
        low_priority = len([t for t in self.tasks if t["priority"] == "Faible"])
        
        stats_text = f"""STATISTIQUES DES TÂCHES

Nombre total de tâches: {total}
Tâches terminées: {completed}
Tâches en cours: {pending}
Taux de completion: {(completed/total)*100:.1f}%

RÉPARTITION PAR PRIORITÉ:
Priorité élevée: {high_priority}
Priorité moyenne: {medium_priority}
Priorité faible: {low_priority}
"""
        
        messagebox.showinfo("Statistiques", stats_text)
    
    def show_help(self):
        """Affiche l'aide"""
        help_text = """AIDE - GESTIONNAIRE DE TÂCHES

RACCOURCIS CLAVIER:
• Ctrl+N: Nouveau fichier
• Ctrl+O: Ouvrir un fichier
• Ctrl+S: Sauvegarder
• Ctrl+A: Ajouter une tâche
• Ctrl+M: Marquer comme terminée
• F2: Modifier la tâche sélectionnée
• Suppr: Supprimer la tâche sélectionnée
• F5: Actualiser l'affichage
• F1: Afficher cette aide

UTILISATION:
1. Saisissez le texte de la tâche
2. Choisissez la priorité
3. Cliquez sur "Ajouter" ou appuyez sur Entrée
4. Double-cliquez sur une tâche pour la modifier
5. Utilisez les filtres pour organiser vos tâches
6. Sauvegardez votre liste au format JSON

CONSEILS:
• Utilisez les priorités pour organiser vos tâches
• Le filtre vous permet de voir seulement certaines tâches
• Vos données sont sauvegardées au format JSON
• Double-cliquez pour modifier rapidement une tâche
"""
        
        help_window = tk.Toplevel(self.root)
        help_window.title("Aide")
        help_window.geometry("600x500")
        help_window.transient(self.root)
        
        text_widget = tk.Text(help_window, wrap=tk.WORD, padx=10, pady=10)
        scrollbar = ttk.Scrollbar(help_window, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        text_widget.insert(1.0, help_text)
        text_widget.config(state=tk.DISABLED)
    
    def show_about(self):
        """Affiche les informations sur l'application"""
        about_text = """Gestionnaire de Tâches v1.0

Une application simple et efficace pour gérer vos tâches quotidiennes.

Fonctionnalités:
• Ajout, modification et suppression de tâches
• Système de priorités (Faible, Moyenne, Élevée)
• Filtrage par statut et priorité
• Sauvegarde au format JSON
• Statistiques de progression
• Interface intuitive avec raccourcis clavier

Développé avec Python et Tkinter.
"""
        
        messagebox.showinfo("À propos", about_text)
    
    def quit_app(self):
        """Quitte l'application"""
        if messagebox.askyesno("Quitter", "Voulez-vous vraiment quitter l'application?"):
            self.root.destroy()
    
    def run(self):
        """Lance l'application"""
        self.root.mainloop()

def main():
    """Point d'entrée principal"""
    try:
        app = TodoApp()
        app.run()
    except Exception as e:
        print(f"Erreur critique: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
