from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Используем v6, чтобы база точно создалась без старых ошибок
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///news_portal_v6.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- МОДЕЛИ ---
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

# --- МАРШРУТЫ ---

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data['username'], password=data['password']).first()
    if user:
        # Ты админ, если твой ник совпадает
        is_admin = True if user.username == "V.V.Putin" else user.is_admin
        return jsonify({
            "username": user.username, 
            "is_admin": is_admin,
            "is_blocked": user.blocked_until > datetime.utcnow() if user.blocked_until else False
        }), 200
    return jsonify({"message": "Ошибка"}), 401

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"message": "Имя занято"}), 400
    new_user = User(username=data['username'], password=data['password'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "Успех"}), 201

@app.route('/create-article', methods=['POST'])
def create_article():
    data = request.json
    # Проверяем только бан
    user = User.query.filter_by(username=data['author']).first()
    if user and user.blocked_until and user.blocked_until > datetime.utcnow():
        return jsonify({"message": "Вы заблокированы!"}), 403

    new_art = Article(
        title=data['title'], 
        content=data['content'], 
        category=data['category'], 
        author=data['author']
    )
    db.session.add(new_art)
    db.session.commit()
    return jsonify({"message": "Опубликовано"}), 201

@app.route('/get-articles', methods=['GET'])
def get_articles():
    articles = Article.query.all()
    return jsonify([{"id": a.id, "title": a.title, "category": a.category, "author": a.author} for a in articles])

# Удаление для админа
@app.route('/admin/delete/<string:target>/<int:id>', methods=['DELETE'])
def delete_item(target, id):
    item = Article.query.get(id) if target == 'article' else User.query.get(id)
    if item:
        db.session.delete(item)
        db.session.commit()
        return jsonify({"message": "Удалено"}), 200
    return jsonify({"message": "Не найдено"}), 404

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    
