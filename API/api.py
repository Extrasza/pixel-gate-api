import base64
from datetime import datetime
from flask_openapi3 import Info, Tag
from flask_openapi3 import OpenAPI
from flask import request, jsonify
import sqlite3
import models
from flask_cors import CORS
import hashlib
import populate as mock

info = Info(title="Game Registry API", version="1.0.0")
app = OpenAPI(__name__, info=info)
CORS(app)

review_tag = Tag(
    name="Review", description="Cadastro e listagem de reviews de jogos")
user_tag = Tag(
    name="User", description="Cadastro e autenticação de usuários")


def get_db_connection():
    conn = sqlite3.connect('API/pxgate_prd.db')
    conn.row_factory = sqlite3.Row
    return conn


@app.before_first_request
def initialize_database():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        mock.populate_platforms(cursor)
        mock.populate_users(cursor)
        mock.populate_reviews(cursor)
        mock.populate_games(cursor)
        conn.commit()


@app.post('/review', description='Insere uma review na base de dados.', tags=[review_tag], responses={
    200: {
        "description": "Review cadastrada com sucesso!",
        "content": {
            "application/json": {
                "example": {
                    "message": "Review cadastrada com sucesso!"
                }
            }
        }
    }
})
def review(body: models.ReviewRequest):
    content = request.json
    content = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    content['image_blob'] = base64.b64decode(content['image_blob'])
    content['user_id'] = cursor.execute(
        'SELECT user_id FROM user WHERE name = ?', (content['user_id'],)).fetchone()[0]
    cursor.execute(
        'INSERT INTO review (game_id, user, review, rating, platform, image_blob) VALUES (?, ?, ?, ?, ?, ?)',
        (content['game_id'], content['user_id'], content['review'],
         content['rating'], content['platform_id'], content['image_blob'])
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Review cadastrada com sucesso!"})


@app.get("/getreviews", description='Traz os últimos 20 dados de revisões de usuários.', tags=[review_tag], responses={
    200: {
        "description": "Lista das últimas 20 revisões de usuários.",
        "content": {
            "application/json": {
                "example": [
                    {
                        "game": "The Legend of Zelda",
                        "user": "Joao",
                        "review": "Incrível, excelente história.",
                        "rating": 4,
                        "platform": "Nintendo Switch",
                        "image_blob": "iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNQwAAAABJRU5ErkJggg=="
                    },
                    {
                        "game": "Minecraft",
                        "user": "Maria",
                        "review": "Adoro criar vacas!",
                        "rating": 2,
                        "platform": "PC",
                        "image_blob": None
                    }
                ]
            }
        }
    }
})
def get_reviews():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT game.name as game, user.name as user, review, rating, platforms.name as platform, image_blob '
        'FROM review '
        'INNER JOIN user ON review.user = user.user_id '
        'INNER JOIN game ON review.game_id = game.game_id '
        'INNER JOIN platforms ON review.platform = platforms.platform_id '
        'ORDER BY review_id DESC '
        'LIMIT 20'
    )
    reviews = cursor.fetchall()
    reviews_list = []
    for review in reviews:
        review_dict = dict(review)
        if review_dict['image_blob']:
            review_dict['image_blob'] = base64.b64encode(
                review_dict['image_blob']).decode('utf-8')
        reviews_list.append(review_dict)
    conn.close()
    return jsonify(reviews_list)


@app.post('/register', description='Registra um novo usuário no banco de dados.', tags=[user_tag], responses={
    200: {
        "description": "Cadastro realizado com sucesso!",
        "content": {
            "application/json": {
                "example": {
                    "message": "Cadastro realizado com sucesso!"
                }
            }
        }
    },
})
def register(body: models.RegisterRequest):
    try:
        content = request.json
        if not content or 'name' not in content or 'password' not in content:
            return jsonify({"message": "Dados de cadastro inválidos!"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        content['createdOn'] = datetime.now()
        content['password'] = hashlib.sha1(
            content['password'].encode()).hexdigest()
        cursor.execute(
            'INSERT INTO user (name, createdOn, password) VALUES (?, ?, ?)',
            (content['name'], content['createdOn'], content['password'])
        )
        conn.commit()
        conn.close()
        return jsonify({"message": "Cadastro realizado com sucesso!"}), 200

    except Exception as err:
        return jsonify({"message": str(err)}), 500


@app.post('/login', description='Verifica se o usuário existe na base e realiza autenticação.', tags=[user_tag], responses={
    200: {
        "description": "Usuário autenticado com sucesso!",
    },
})
def login(body: models.LoginRequest):
    content = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    content['password'] = hashlib.sha1(
        content['password'].encode()).hexdigest()
    cursor.execute(
        'SELECT user_id FROM user WHERE name = ? AND password = ?',
        (content['name'], content['password'])
    )
    user = cursor.fetchone()
    conn.close()
    if user:
        return jsonify({"message": "Usuário autenticado com sucesso!"})
    return jsonify({"message": "Usuário ou senha incorretos!"})


@app.get("/fetchUserReviews", description='Traz as revisões específicas do usuário conectado.', tags=[review_tag], responses={
    200: {
        "description": "Success. Lista de revisões do usuário.",
        "content": {
            "application/json": {
                "example": [
                    {
                        "game": "The Legend of Zelda",
                        "review": "Incredible game with great story.",
                        "rating": 9.5,
                        "platform": "Nintendo Switch",
                        "image_blob": "iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNQwAAAABJRU5ErkJggg=="
                    },
                    {
                        "game": "Minecraft",
                        "review": "A sandbox game with endless possibilities.",
                        "rating": 9.0,
                        "platform": "PC",
                        "image_blob": None
                    }
                ]
            }
        }
    }
})
def fetch_user_reviews(query: models.FetchUserReviewsQuery):
    user_name = query.name
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT game.name as game, review, rating, platforms.name as platform, image_blob '
        'FROM review '
        'INNER JOIN user ON review.user = user.user_id '
        'INNER JOIN game ON review.game_id = game.game_id '
        'INNER JOIN platforms ON review.platform = platforms.platform_id '
        'WHERE user.name = ? '
        'ORDER BY review_id DESC ',
        (user_name,)
    )
    reviews = cursor.fetchall()
    reviews_list = []
    for review in reviews:
        review_dict = dict(review)
        if review_dict['image_blob']:
            review_dict['image_blob'] = base64.b64encode(
                review_dict['image_blob']).decode('utf-8')
        reviews_list.append(review_dict)
    conn.close()
    return jsonify(reviews_list)


@app.get("/fetchGames", description='Traz as opções do seletor de jogos.', tags=[review_tag], responses={
    200: {
        "description": "Success. Lista de jogos disponíveis.",
        "content": {
            "application/json": {
                "example": {
                    "games": [
                        {"game_id": 1, "name": "The Legend of Zelda"},
                        {"game_id": 2, "name": "Super Mario Bros"},
                        {"game_id": 3, "name": "Minecraft"}
                    ]
                }
            }
        }
    }
})
def fetch_games():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT game_id,name FROM game'
    )
    games = cursor.fetchall()
    games_list = []
    for game in games:
        game_dict = dict(game)
        games_list.append(game_dict)
    conn.close()
    return jsonify(games_list)


@app.get("/fetchPlatforms", description='Traz as opções do seletor de jogos.', tags=[review_tag], responses={
    200: {
        "description": "Success. Retorna lista de plataformas",
        "content": {
            "application/json": {
                "example": {
                    "platforms": [
                        {"id": 1, "name": "PlayStation"},
                        {"id": 2, "name": "Xbox"},
                        {"id": 3, "name": "PC"}
                    ]
                }
            }
        }
    }
})
def fetch_platforms():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT platform_id,name FROM platforms'
    )
    platforms = cursor.fetchall()
    platforms_list = []
    for platform in platforms:
        platform_dict = dict(platform)
        platforms_list.append(platform_dict)
    conn.close()
    return jsonify(platforms_list)


if __name__ == '__main__':
    app.run(debug=True)
