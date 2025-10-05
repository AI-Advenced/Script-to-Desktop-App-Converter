#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Calculatrice Simple
Un exemple de script Python basique pour démontrer la conversion GUI
"""

import math
import sys

class SimpleCalculator:
    def __init__(self):
        self.history = []
        
    def add(self, a, b):
        """Addition de deux nombres"""
        result = a + b
        self.history.append(f"{a} + {b} = {result}")
        return result
    
    def subtract(self, a, b):
        """Soustraction de deux nombres"""
        result = a - b
        self.history.append(f"{a} - {b} = {result}")
        return result
    
    def multiply(self, a, b):
        """Multiplication de deux nombres"""
        result = a * b
        self.history.append(f"{a} × {b} = {result}")
        return result
    
    def divide(self, a, b):
        """Division de deux nombres"""
        if b == 0:
            raise ValueError("Division par zéro impossible!")
        result = a / b
        self.history.append(f"{a} ÷ {b} = {result}")
        return result
    
    def power(self, a, b):
        """Puissance"""
        result = a ** b
        self.history.append(f"{a} ^ {b} = {result}")
        return result
    
    def square_root(self, a):
        """Racine carrée"""
        if a < 0:
            raise ValueError("Racine carrée d'un nombre négatif impossible!")
        result = math.sqrt(a)
        self.history.append(f"√{a} = {result}")
        return result
    
    def show_history(self):
        """Affiche l'historique des calculs"""
        if not self.history:
            print("Aucun calcul dans l'historique.")
            return
        
        print("\n=== HISTORIQUE DES CALCULS ===")
        for i, calc in enumerate(self.history, 1):
            print(f"{i:2d}. {calc}")
    
    def clear_history(self):
        """Efface l'historique"""
        self.history.clear()
        print("Historique effacé.")

def get_number(prompt):
    """Demande un nombre à l'utilisateur avec validation"""
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Erreur: Veuillez entrer un nombre valide.")
        except KeyboardInterrupt:
            print("\nOpération annulée.")
            return None

def main_menu():
    """Affiche le menu principal"""
    print("\n" + "="*50)
    print("         CALCULATRICE SIMPLE")
    print("="*50)
    print("1. Addition (+)")
    print("2. Soustraction (-)")
    print("3. Multiplication (×)")
    print("4. Division (÷)")
    print("5. Puissance (^)")
    print("6. Racine carrée (√)")
    print("7. Afficher l'historique")
    print("8. Effacer l'historique")
    print("9. Quitter")
    print("-"*50)

def main():
    """Fonction principale"""
    calc = SimpleCalculator()
    
    print("Bienvenue dans la Calculatrice Simple!")
    print("Tapez Ctrl+C à tout moment pour annuler une opération.")
    
    while True:
        try:
            main_menu()
            choice = input("Votre choix (1-9): ").strip()
            
            if choice == "1":  # Addition
                a = get_number("Premier nombre: ")
                if a is None: continue
                b = get_number("Deuxième nombre: ")
                if b is None: continue
                result = calc.add(a, b)
                print(f"Résultat: {a} + {b} = {result}")
                
            elif choice == "2":  # Soustraction
                a = get_number("Premier nombre: ")
                if a is None: continue
                b = get_number("Deuxième nombre: ")
                if b is None: continue
                result = calc.subtract(a, b)
                print(f"Résultat: {a} - {b} = {result}")
                
            elif choice == "3":  # Multiplication
                a = get_number("Premier nombre: ")
                if a is None: continue
                b = get_number("Deuxième nombre: ")
                if b is None: continue
                result = calc.multiply(a, b)
                print(f"Résultat: {a} × {b} = {result}")
                
            elif choice == "4":  # Division
                a = get_number("Numérateur: ")
                if a is None: continue
                b = get_number("Dénominateur: ")
                if b is None: continue
                try:
                    result = calc.divide(a, b)
                    print(f"Résultat: {a} ÷ {b} = {result}")
                except ValueError as e:
                    print(f"Erreur: {e}")
                    
            elif choice == "5":  # Puissance
                a = get_number("Base: ")
                if a is None: continue
                b = get_number("Exposant: ")
                if b is None: continue
                result = calc.power(a, b)
                print(f"Résultat: {a} ^ {b} = {result}")
                
            elif choice == "6":  # Racine carrée
                a = get_number("Nombre: ")
                if a is None: continue
                try:
                    result = calc.square_root(a)
                    print(f"Résultat: √{a} = {result}")
                except ValueError as e:
                    print(f"Erreur: {e}")
                    
            elif choice == "7":  # Historique
                calc.show_history()
                
            elif choice == "8":  # Effacer historique
                calc.clear_history()
                
            elif choice == "9":  # Quitter
                print("\nMerci d'avoir utilisé la Calculatrice Simple!")
                print("Au revoir! 👋")
                break
                
            else:
                print("Choix invalide. Veuillez saisir un nombre entre 1 et 9.")
                
        except KeyboardInterrupt:
            print("\n\nProgramme interrompu par l'utilisateur.")
            confirm = input("Voulez-vous vraiment quitter? (o/N): ").lower()
            if confirm in ['o', 'oui', 'y', 'yes']:
                break
        except Exception as e:
            print(f"Erreur inattendue: {e}")
            print("Le programme continue...")

if __name__ == "__main__":
    main()
