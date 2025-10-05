#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test simple pour tester le convertisseur
"""

import datetime
import sys

def calculer_age():
    """Calcule l'âge à partir de l'année de naissance"""
    print("=== Calculateur d'âge ===")
    
    try:
        annee_naissance = int(input("Entrez votre année de naissance: "))
        annee_actuelle = datetime.datetime.now().year
        
        age = annee_actuelle - annee_naissance
        
        if age < 0:
            print("Erreur: L'année de naissance ne peut pas être dans le futur!")
        elif age > 150:
            print("Erreur: Âge trop élevé, vérifiez l'année de naissance.")
        else:
            print(f"Vous avez {age} ans.")
            
            if age < 18:
                print("Vous êtes mineur.")
            elif age < 65:
                print("Vous êtes en âge de travailler.")
            else:
                print("Vous êtes à l'âge de la retraite.")
    
    except ValueError:
        print("Erreur: Veuillez entrer un nombre valide.")
    except KeyboardInterrupt:
        print("\nProgramme interrompu par l'utilisateur.")

def afficher_info_systeme():
    """Affiche des informations sur le système"""
    print("\n=== Informations système ===")
    print(f"Version Python: {sys.version}")
    print(f"Plateforme: {sys.platform}")
    print(f"Date/Heure actuelle: {datetime.datetime.now()}")

def menu_principal():
    """Menu principal de l'application"""
    while True:
        print("\n" + "="*40)
        print("    SCRIPT DE DÉMONSTRATION")
        print("="*40)
        print("1. Calculer l'âge")
        print("2. Informations système")
        print("3. Quitter")
        print("-"*40)
        
        choix = input("Votre choix (1-3): ").strip()
        
        if choix == "1":
            calculer_age()
        elif choix == "2":
            afficher_info_systeme()
        elif choix == "3":
            print("Au revoir!")
            break
        else:
            print("Choix invalide. Veuillez saisir 1, 2 ou 3.")

if __name__ == "__main__":
    try:
        menu_principal()
    except Exception as e:
        print(f"Erreur inattendue: {e}")
        input("Appuyez sur Entrée pour fermer...")