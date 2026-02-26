from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///news_portal.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- МОДЕЛИ ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    blocked_until = db.Column(db.DateTime, nullable=True) # Время, до которого бан

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
    # Сделаем первого юзера админом, если нужно (замени 'AdminName' на свой ник)
    # admin = User.query.filter_by(username='AdminName').first()
    # if admin: admin.is_admin = True; db.session.commit()

# --- API ---

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data['username'], password=data['password']).first()
    if user:
        return jsonify({
            "username": user.username, 
            "is_admin": user.is_admin,
            "is_blocked": user.blocked_until > datetime.utcnow() if user.blocked_until else False
        }), 200
    return jsonify({"message": "Ошибка"}), 401

@app.route('/create-article', methods=['POST'])
def create_article():
    data = request.json
    user = User.query.filter_by(username=data['author']).first()
    if user and user.blocked_until and user.blocked_until > datetime.utcnow():
        return jsonify({"message": "Вы заблокированы!"}), 403
    new_art = Article(title=data['title'], content=data['content'], category=data['category'], author=data['author'])
    db.session.add(new_art)
    db.session.commit()
    return jsonify({"message": "Опубликовано"}), 201

# --- АДМИНСКИЕ ФУНКЦИИ ---

@app.route('/admin/data', methods=['GET'])
def get_admin_data():
    # В реальности тут нужна проверка токена, но для начала сделаем просто получение всех данных
    users = User.query.all()
    articles = Article.query.all()
    comments = Comment.query.all()
    return jsonify({
        "users": [{"id": u.id, "username": u.username, "is_admin": u.is_admin, "blocked": str(u.blocked_until)} for u in users],
        "articles": [{"id": a.id, "title": a.title, "author": a.author} for a in articles],
        "comments": [{"id": c.id, "text": c.text, "author": c.author} for c in comments]
    })

@app.route('/admin/delete/<string:target>/<int:id>', methods=['DELETE'])
def delete_item(target, id):
    if target == 'article': item = Article.query.get(id)
    elif target == 'comment': item = Comment.query.get(id)
    elif target == 'user': item = User.query.get(id)
    
    if item:
        db.session.delete(item)
        db.session.commit()
        return jsonify({"message": "Удалено"}), 200
    return jsonify({"message": "Не найдено"}), 404

@app.route('/admin/block/<int:user_id>', methods=['POST'])
def block_user(user_id):
    user = User.query.get(user_id)
    if user:
        user.blocked_until = datetime.utcnow() + timedelta(hours=24) # Блок на сутки
        db.session.commit()
        return jsonify({"message": "Заблокирован на 24ч"}), 200
    return jsonify({"message": "Ошибка"}), 404

# Остальные маршруты (register, get-articles и т.д.) оставить как были раньше
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

