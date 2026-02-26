from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

# Используем v4, чтобы создать абсолютно новую чистую базу
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///news_portal_v4.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- МОДЕЛИ ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_verified = db.Column(db.Boolean, default=False)
    blocked_until = db.Column(db.DateTime, nullable=True)

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50))
    author = db.Column(db.String(80))

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, nullable=False)
    author = db.Column(db.String(80), nullable=False)
    text = db.Column(db.Text, nullable=False)

with app.app_context():
    db.create_all()

# --- МАРШРУТЫ ---

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data['username'], password=data['password']).first()
    if user:
        # АВТО-АДМИН ДЛЯ ТЕБЯ (замени ТВОЙ_ЛОГИН на свой ник)
        if user.username == "V.V.Putin":
            user.is_admin = True
            user.is_verified = True
            db.session.commit()
            
        return jsonify({
            "username": user.username, 
            "is_admin": user.is_admin,
            "is_verified": user.is_verified,
            "is_blocked": user.blocked_until > datetime.utcnow() if user.blocked_until else False
        }), 200
    return jsonify({"message": "Ошибка"}), 401

@app.route('/get-articles', methods=['GET'])
def get_articles():
    articles = Article.query.all()
    return jsonify([{"id": a.id, "title": a.title, "category": a.category, "author": a.author} for a in articles])

@app.route('/create-article', methods=['POST'])
def create_article():
    data = request.json
    user = User.query.filter_by(username=data['author']).first()
    if not user or not user.is_verified:
        return jsonify({"message": "Нужна верификация!"}), 403
    new_art = Article(title=data['title'], content=data['content'], category=data['category'], author=data['author'])
    db.session.add(new_art)
    db.session.commit()
    return jsonify({"message": "Опубликовано"}), 201

# --- АДМИНКА ---
@app.route('/admin/data', methods=['GET'])
def get_admin_data():
    users = User.query.all()
    articles = Article.query.all()
    comments = Comment.query.all()
    return jsonify({
        "users": [{"id": u.id, "username": u.username, "is_admin": u.is_admin, "is_verified": u.is_verified, "blocked": str(u.blocked_until)} for u in users],
        "articles": [{"id": a.id, "title": a.title, "author": a.author} for a in articles],
        "comments": [{"id": c.id, "text": c.text, "author": c.author} for c in comments]
    })

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"message": "Имя занято"}), 400
    new_user = User(username=data['username'], password=data['password'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "Аккаунт создан"}), 201

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    
