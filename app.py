from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///news_portal_open.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50))
    author = db.Column(db.String(80))

with app.app_context():
    db.create_all()

@app.route('/get-articles', methods=['GET'])
def get_articles():
    articles = Article.query.all()
    return jsonify([{"id": a.id, "title": a.title, "content": a.content, "category": a.category, "author": a.author} for a in articles])

@app.route('/create-article', methods=['POST'])
def create_article():
    data = request.json
    new_art = Article(
        title=data['title'], 
        content=data['content'], 
        category=data['category'] or 'Без категории', 
        author=data['author'] or 'Аноним'
    )
    db.session.add(new_art)
    db.session.commit()
    return jsonify({"message": "Успех"}), 201

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    
