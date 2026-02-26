from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# База данных будет создана в той же папке
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///news_portal.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ТАБЛИЦЫ
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

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

# МАРШРУТЫ
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"message": "Имя занято"}), 400
    new_user = User(username=data['username'], password=data['password'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "Аккаунт создан"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data['username'], password=data['password']).first()
    if user:
        return jsonify({"message": "Вход выполнен", "username": user.username}), 200
    return jsonify({"message": "Ошибка входа"}), 401

@app.route('/get-articles', methods=['GET'])
def get_articles():
    articles = Article.query.all()
    return jsonify([{"id": a.id, "title": a.title, "category": a.category, "author": a.author} for a in articles])

@app.route('/get-article/<int:art_id>', methods=['GET'])
def get_article(art_id):
    a = Article.query.get(art_id)
    if a:
        return jsonify({"id": a.id, "title": a.title, "content": a.content, "author": a.author, "category": a.category})
    return jsonify({"message": "Статья не найдена"}), 404

@app.route('/create-article', methods=['POST'])
def create_article():
    data = request.json
    new_art = Article(title=data['title'], content=data['content'], category=data['category'], author=data['author'])
    db.session.add(new_art)
    db.session.commit()
    return jsonify({"message": "Статья опубликована"}), 201

@app.route('/add-comment', methods=['POST'])
def add_comment():
    data = request.json
    new_comm = Comment(article_id=data['article_id'], author=data['author'], text=data['text'])
    db.session.add(new_comm)
    db.session.commit()
    return jsonify({"message": "Комментарий добавлен"}), 201

@app.route('/get-comments/<int:art_id>', methods=['GET'])
def get_comments(art_id):
    comments = Comment.query.filter_by(article_id=art_id).all()
    return jsonify([{"author": c.author, "text": c.text} for c in comments])

if __name__ == '__main__':
    app.run(debug=True, port=5000)

