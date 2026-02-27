from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# Если меняешь структуру базы, лучше поменять имя файла на news_v3.db
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///news_v3.db'
db = SQLAlchemy(app)

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(80))

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'), nullable=False)
    author = db.Column(db.String(50))
    text = db.Column(db.Text, nullable=False)

with app.app_context():
    db.create_all()

# Старые методы...
@app.route('/get-articles', methods=['GET'])
def get_articles():
    articles = Article.query.all()
    return jsonify([{"id": a.id, "title": a.title, "content": a.content, "author": a.author} for a in articles])

# Новые методы для комментариев
@app.route('/get-comments', methods=['GET'])
def get_comments():
    aid = request.args.get('article_id')
    comments = Comment.query.filter_by(article_id=aid).all()
    return jsonify([{"author": c.author, "text": c.text} for c in comments])

@app.route('/add-comment', methods=['POST'])
def add_comment():
    data = request.json
    new_com = Comment(article_id=data['article_id'], author=data['author'] or 'Аноним', text=data['text'])
    db.session.add(new_com)
    db.session.commit()
    return jsonify({"message": "OK"}), 201

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    
