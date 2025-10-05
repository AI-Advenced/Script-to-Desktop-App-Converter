#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Application Web Flask - Blog Simple
Démontre la conversion d'une application Flask vers desktop
"""

from flask import Flask, render_template_string, request, redirect, url_for, flash, jsonify
import json
import datetime
import os
from typing import Dict, List

# Configuration
DATA_FILE = "blog_posts.json"

app = Flask(__name__)
app.secret_key = "demo_secret_key_change_in_production"

# Données en mémoire
posts = []
comments = {}

def load_data():
    """Charge les données depuis le fichier JSON"""
    global posts, comments
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                posts = data.get('posts', [])
                comments = data.get('comments', {})
        else:
            # Données par défaut
            posts = [
                {
                    "id": 1,
                    "title": "Bienvenue sur mon blog!",
                    "content": "Ceci est le premier article de mon blog. J'espère que vous apprécierez le contenu que je vais partager ici.",
                    "author": "Admin",
                    "date": "2024-01-01T10:00:00",
                    "tags": ["bienvenue", "premier-post"]
                },
                {
                    "id": 2,
                    "title": "Les bases de Python",
                    "content": "Python est un langage de programmation fantastique pour débuter. Dans cet article, nous allons voir pourquoi.",
                    "author": "Admin", 
                    "date": "2024-01-02T14:30:00",
                    "tags": ["python", "programmation", "tutoriel"]
                }
            ]
            comments = {
                "1": [
                    {"author": "Lecteur1", "content": "Super blog, j'ai hâte de lire la suite!", "date": "2024-01-01T11:00:00"},
                    {"author": "Lecteur2", "content": "Merci pour ce contenu de qualité", "date": "2024-01-01T15:30:00"}
                ]
            }
            save_data()
    except Exception as e:
        print(f"Erreur lors du chargement: {e}")
        posts = []
        comments = {}

def save_data():
    """Sauvegarde les données dans le fichier JSON"""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump({
                'posts': posts,
                'comments': comments
            }, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Erreur lors de la sauvegarde: {e}")

# Templates HTML intégrés
BASE_TEMPLATE = '''
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Mon Blog{% endblock %}</title>
    <style>
        body { 
            font-family: 'Segoe UI', Arial, sans-serif; 
            margin: 0; 
            padding: 0; 
            background-color: #f5f5f5;
            line-height: 1.6;
        }
        .container { 
            max-width: 800px; 
            margin: 0 auto; 
            padding: 20px;
            background-color: white;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
            min-height: 100vh;
        }
        header { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; 
            padding: 2rem; 
            margin: -20px -20px 20px -20px;
            text-align: center;
        }
        h1 { margin: 0; font-size: 2.5em; }
        .subtitle { margin: 10px 0 0 0; opacity: 0.9; }
        nav { 
            background: #333; 
            padding: 1rem;
            margin: -20px -20px 20px -20px;
        }
        nav a { 
            color: white; 
            text-decoration: none; 
            margin-right: 20px; 
            padding: 5px 10px;
            border-radius: 3px;
            transition: background 0.3s;
        }
        nav a:hover { background: #555; }
        .post { 
            border: 1px solid #ddd; 
            margin-bottom: 20px; 
            padding: 20px;
            border-radius: 8px;
            background: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        .post h2 { 
            color: #333; 
            margin-top: 0; 
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }
        .post-meta { 
            color: #666; 
            font-size: 0.9em; 
            margin-bottom: 15px;
        }
        .tags {
            margin: 10px 0;
        }
        .tag {
            background: #667eea;
            color: white;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            margin-right: 5px;
            display: inline-block;
        }
        .comments {
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #eee;
        }
        .comment {
            background: #f8f9fa;
            padding: 10px;
            margin: 10px 0;
            border-left: 3px solid #667eea;
            border-radius: 0 5px 5px 0;
        }
        .comment-meta {
            font-size: 0.8em;
            color: #666;
            margin-bottom: 5px;
        }
        .form-group { margin: 15px 0; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input, textarea { 
            width: 100%; 
            padding: 10px; 
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
        }
        textarea { height: 120px; resize: vertical; }
        .btn { 
            background: #667eea; 
            color: white; 
            padding: 10px 20px; 
            border: none; 
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            transition: background 0.3s;
        }
        .btn:hover { background: #5a6fd8; }
        .btn-danger { background: #dc3545; }
        .btn-danger:hover { background: #c82333; }
        .flash { 
            padding: 10px; 
            margin: 10px 0; 
            border-radius: 4px;
            background: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
        }
        .error { 
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24;
        }
        footer {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            text-align: center;
            color: #666;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🌟 Mon Blog Personnel</h1>
            <p class="subtitle">Partage d'idées et d'expériences</p>
        </header>
        
        <nav>
            <a href="{{ url_for('index') }}">🏠 Accueil</a>
            <a href="{{ url_for('new_post') }}">✏️ Nouvel Article</a>
            <a href="{{ url_for('admin') }}">⚙️ Administration</a>
            <a href="{{ url_for('api_posts') }}">📊 API</a>
        </nav>
        
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="flash {{ 'error' if category == 'error' else '' }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        {% block content %}{% endblock %}
        
        <footer>
            <p>© 2024 Mon Blog - Créé avec Flask et Python 🐍</p>
            <p>Application générée automatiquement par Script to Desktop App Converter</p>
        </footer>
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    """Page d'accueil avec liste des articles"""
    template = BASE_TEMPLATE + '''
{% block content %}
<h2>📰 Derniers Articles</h2>

{% if posts %}
    {% for post in posts|reverse %}
    <article class="post">
        <h2>{{ post.title }}</h2>
        <div class="post-meta">
            👤 Par {{ post.author }} • 📅 {{ post.date[:19] | replace('T', ' à ') }}
        </div>
        <div class="content">
            {{ post.content }}
        </div>
        {% if post.tags %}
        <div class="tags">
            🏷️ 
            {% for tag in post.tags %}
                <span class="tag">{{ tag }}</span>
            {% endfor %}
        </div>
        {% endif %}
        
        <div class="comments">
            <h4>💬 Commentaires ({{ comments.get(post.id|string, [])|length }})</h4>
            {% for comment in comments.get(post.id|string, []) %}
                <div class="comment">
                    <div class="comment-meta">
                        {{ comment.author }} • {{ comment.date[:19] | replace('T', ' à ') }}
                    </div>
                    <div>{{ comment.content }}</div>
                </div>
            {% endfor %}
            
            <form method="POST" action="{{ url_for('add_comment', post_id=post.id) }}" style="margin-top: 15px;">
                <div class="form-group">
                    <label>Votre nom:</label>
                    <input type="text" name="author" required>
                </div>
                <div class="form-group">
                    <label>Commentaire:</label>
                    <textarea name="content" required placeholder="Partagez votre avis..."></textarea>
                </div>
                <button type="submit" class="btn">💬 Ajouter un commentaire</button>
            </form>
        </div>
    </article>
    {% endfor %}
{% else %}
    <div class="post">
        <h2>Aucun article pour le moment</h2>
        <p>Il n'y a pas encore d'articles sur ce blog. <a href="{{ url_for('new_post') }}">Créez le premier article!</a></p>
    </div>
{% endif %}
{% endblock %}
'''
    return render_template_string(template, posts=posts, comments=comments)

@app.route('/new', methods=['GET', 'POST'])
def new_post():
    """Créer un nouveau post"""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        author = request.form.get('author', 'Anonyme').strip()
        tags = request.form.get('tags', '').strip()
        
        if not title or not content:
            flash('Le titre et le contenu sont obligatoires', 'error')
        else:
            # Nouveau post
            post_id = max([p['id'] for p in posts], default=0) + 1
            new_post = {
                'id': post_id,
                'title': title,
                'content': content,
                'author': author,
                'date': datetime.datetime.now().isoformat(),
                'tags': [tag.strip() for tag in tags.split(',') if tag.strip()]
            }
            
            posts.append(new_post)
            save_data()
            
            flash(f'Article "{title}" créé avec succès!', 'success')
            return redirect(url_for('index'))
    
    template = BASE_TEMPLATE + '''
{% block content %}
<h2>✏️ Nouvel Article</h2>

<form method="POST">
    <div class="form-group">
        <label for="title">Titre de l'article *</label>
        <input type="text" name="title" id="title" required placeholder="Entrez le titre de votre article">
    </div>
    
    <div class="form-group">
        <label for="author">Auteur</label>
        <input type="text" name="author" id="author" value="Admin" placeholder="Votre nom">
    </div>
    
    <div class="form-group">
        <label for="content">Contenu *</label>
        <textarea name="content" id="content" required placeholder="Rédigez votre article ici..."></textarea>
    </div>
    
    <div class="form-group">
        <label for="tags">Tags (séparés par des virgules)</label>
        <input type="text" name="tags" id="tags" placeholder="python, web, tutoriel">
    </div>
    
    <button type="submit" class="btn">📝 Publier l'article</button>
    <a href="{{ url_for('index') }}" class="btn" style="background: #6c757d; margin-left: 10px;">❌ Annuler</a>
</form>
{% endblock %}
'''
    return render_template_string(template)

@app.route('/comment/<int:post_id>', methods=['POST'])
def add_comment(post_id):
    """Ajouter un commentaire à un post"""
    author = request.form.get('author', 'Anonyme').strip()
    content = request.form.get('content', '').strip()
    
    if not content:
        flash('Le commentaire ne peut pas être vide', 'error')
    else:
        comment = {
            'author': author,
            'content': content,
            'date': datetime.datetime.now().isoformat()
        }
        
        post_id_str = str(post_id)
        if post_id_str not in comments:
            comments[post_id_str] = []
        
        comments[post_id_str].append(comment)
        save_data()
        
        flash('Commentaire ajouté avec succès!', 'success')
    
    return redirect(url_for('index'))

@app.route('/admin')
def admin():
    """Panel d'administration"""
    template = BASE_TEMPLATE + '''
{% block content %}
<h2>⚙️ Administration</h2>

<div class="post">
    <h3>📊 Statistiques</h3>
    <p><strong>Nombre d'articles:</strong> {{ posts|length }}</p>
    <p><strong>Nombre total de commentaires:</strong> {{ total_comments }}</p>
    <p><strong>Dernier article:</strong> 
        {% if posts %}
            "{{ posts[-1].title }}" par {{ posts[-1].author }}
        {% else %}
            Aucun article
        {% endif %}
    </p>
</div>

<div class="post">
    <h3>📝 Gestion des Articles</h3>
    {% if posts %}
        <table style="width: 100%; border-collapse: collapse;">
            <thead>
                <tr style="background: #f8f9fa;">
                    <th style="padding: 10px; text-align: left; border: 1px solid #ddd;">ID</th>
                    <th style="padding: 10px; text-align: left; border: 1px solid #ddd;">Titre</th>
                    <th style="padding: 10px; text-align: left; border: 1px solid #ddd;">Auteur</th>
                    <th style="padding: 10px; text-align: left; border: 1px solid #ddd;">Date</th>
                    <th style="padding: 10px; text-align: left; border: 1px solid #ddd;">Commentaires</th>
                    <th style="padding: 10px; text-align: left; border: 1px solid #ddd;">Actions</th>
                </tr>
            </thead>
            <tbody>
                {% for post in posts %}
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;">{{ post.id }}</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{{ post.title }}</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{{ post.author }}</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{{ post.date[:10] }}</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{{ comments.get(post.id|string, [])|length }}</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">
                        <form method="POST" action="{{ url_for('delete_post', post_id=post.id) }}" style="display: inline;">
                            <button type="submit" class="btn btn-danger" style="padding: 5px 10px; font-size: 12px;"
                                    onclick="return confirm('Êtes-vous sûr de vouloir supprimer cet article?')">
                                🗑️ Supprimer
                            </button>
                        </form>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    {% else %}
        <p>Aucun article à gérer.</p>
    {% endif %}
</div>

<div class="post">
    <h3>🔧 Actions Administratives</h3>
    <form method="POST" action="{{ url_for('clear_all') }}" style="display: inline;">
        <button type="submit" class="btn btn-danger"
                onclick="return confirm('Êtes-vous sûr de vouloir supprimer TOUS les articles et commentaires?')">
            🗑️ Tout supprimer
        </button>
    </form>
    
    <form method="POST" action="{{ url_for('export_data') }}" style="display: inline; margin-left: 10px;">
        <button type="submit" class="btn">📁 Exporter les données</button>
    </form>
    
    <a href="{{ url_for('new_post') }}" class="btn" style="margin-left: 10px;">✏️ Nouvel article</a>
</div>
{% endblock %}
'''
    
    total_comments = sum(len(comment_list) for comment_list in comments.values())
    
    return render_template_string(template, 
                                posts=posts, 
                                comments=comments,
                                total_comments=total_comments)

@app.route('/delete/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    """Supprimer un article"""
    global posts
    posts = [p for p in posts if p['id'] != post_id]
    
    # Supprimer aussi les commentaires associés
    post_id_str = str(post_id)
    if post_id_str in comments:
        del comments[post_id_str]
    
    save_data()
    flash('Article supprimé avec succès!', 'success')
    return redirect(url_for('admin'))

@app.route('/clear', methods=['POST'])
def clear_all():
    """Supprimer tous les données"""
    global posts, comments
    posts.clear()
    comments.clear()
    save_data()
    flash('Toutes les données ont été supprimées!', 'success')
    return redirect(url_for('admin'))

@app.route('/export', methods=['POST'])
def export_data():
    """Exporter les données"""
    try:
        export_filename = f"blog_export_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(export_filename, 'w', encoding='utf-8') as f:
            json.dump({
                'posts': posts,
                'comments': comments,
                'exported_at': datetime.datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
        
        flash(f'Données exportées vers {export_filename}', 'success')
    except Exception as e:
        flash(f'Erreur lors de l\'export: {str(e)}', 'error')
    
    return redirect(url_for('admin'))

@app.route('/api/posts')
def api_posts():
    """API REST - Liste des posts"""
    return jsonify({
        'status': 'success',
        'data': {
            'posts': posts,
            'total_posts': len(posts),
            'total_comments': sum(len(comment_list) for comment_list in comments.values())
        }
    })

@app.route('/api/post/<int:post_id>')
def api_post(post_id):
    """API REST - Détail d'un post"""
    post = next((p for p in posts if p['id'] == post_id), None)
    if not post:
        return jsonify({'status': 'error', 'message': 'Post not found'}), 404
    
    post_comments = comments.get(str(post_id), [])
    
    return jsonify({
        'status': 'success',
        'data': {
            'post': post,
            'comments': post_comments,
            'comment_count': len(post_comments)
        }
    })

@app.route('/health')
def health():
    """Endpoint de santé pour vérification"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.datetime.now().isoformat(),
        'posts_count': len(posts),
        'comments_count': sum(len(comment_list) for comment_list in comments.values())
    })

# Gestion des erreurs
@app.errorhandler(404)
def not_found(error):
    template = BASE_TEMPLATE + '''
{% block content %}
<div class="post">
    <h2>🔍 Page non trouvée</h2>
    <p>Désolé, la page que vous cherchez n'existe pas.</p>
    <a href="{{ url_for('index') }}" class="btn">🏠 Retour à l'accueil</a>
</div>
{% endblock %}
'''
    return render_template_string(template), 404

@app.errorhandler(500)
def server_error(error):
    template = BASE_TEMPLATE + '''
{% block content %}
<div class="post">
    <h2>⚠️ Erreur serveur</h2>
    <p>Une erreur interne s'est produite. Veuillez réessayer plus tard.</p>
    <a href="{{ url_for('index') }}" class="btn">🏠 Retour à l'accueil</a>
</div>
{% endblock %}
'''
    return render_template_string(template), 500

def main():
    """Point d'entrée principal"""
    print("🌐 Démarrage du blog Flask...")
    print("📝 Chargement des données...")
    
    load_data()
    
    print(f"✅ Blog prêt avec {len(posts)} articles et {sum(len(c) for c in comments.values())} commentaires")
    print("🚀 Serveur Flask démarré sur http://127.0.0.1:5000")
    print("📊 API disponible sur http://127.0.0.1:5000/api/posts")
    print("⚙️ Administration sur http://127.0.0.1:5000/admin")
    print("\nAppuyez sur Ctrl+C pour arrêter le serveur")
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    except KeyboardInterrupt:
        print("\n👋 Arrêt du serveur demandé par l'utilisateur")
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == '__main__':
    main()
