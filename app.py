from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Используем новую базу, чтобы избежать ошибок старых колонок
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///news_portal_v6.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    blocked_until = db.Column(db.DateTime, nullable=True)

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50))
    author = db.Column(db.String(80))

with app.app_context():
    db.create_all()

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data['username'], password=data['password']).first()
    if user:
        return jsonify({
            "username": user.username, 
            "is_admin": user.username == "V.V.Putin", # Замени на свой ник
            "is_blocked": False 
        }), 200
    return jsonify({"message": "Ошибка"}), 401

@app.route('/get-articles', methods=['GET'])
def get_articles():
    articles = Article.query.all()
    return jsonify([{"id": a.id, "title": a.title, "category": a.category, "author": a.author, "content": a.content} for a in articles])

@app.route('/create-article', methods=['POST'])
def create_article():
    data = request.json
    new_art = Article(title=data['title'], content=data['content'], category=data['category'], author=data['author'])
    db.session.add(new_art)
    db.session.commit()
    return jsonify({"message": "Опубликовано"}), 201

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    
