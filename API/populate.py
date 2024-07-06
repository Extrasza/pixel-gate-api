import sqlite3


def convert_image_to_blob(path):
    with open(path, 'rb') as file:
        blob = file.read()
    return blob


def populate_platforms(cursor):
    cursor.execute(
        'CREATE TABLE IF NOT EXISTS platforms (platform_id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, manufacturer TEXT, generation INTEGER)')
    cursor.execute('SELECT COUNT(*) FROM platforms')
    count = cursor.fetchone()[0]
    if count == 0:
        cursor.executemany(
            'INSERT INTO platforms (name, manufacturer, generation) VALUES (?, ?, ?)',
            [
                ("Nintendo Switch", "Nintendo", 8),
                ("Computer", "Microsoft", 0),
                ("PS5", "Sony", 9),
                ("Xbox Series X", "Microsoft", 9),
                ("PS4", "Sony", 8),
                ("Nintendo Wii U", "Nintendo", 7)
            ]
        )


def populate_users(cursor):
    cursor.execute(
        'CREATE TABLE IF NOT EXISTS user (user_id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, createdOn DATE, password TEXT)')
    cursor.execute('SELECT COUNT(*) FROM user')
    count = cursor.fetchone()[0]
    if count == 0:
        cursor.executemany(
            'INSERT INTO user (name, createdOn, password) VALUES (?, ?, ?)',
            [
                ("Mattchi", "2024-07-01 02:15:22.002431",
                 "da39a3ee5e6b4b0d3255bfef95601890afd80709"),
                ("User02", "2024-07-01 11:39:10.496092",
                 "42c231120f22dfd0f0ee3446cdcc5fb5dfb02855"),
                ("JucaX", "2024-07-01 06:07:50.138756",
                 "39fdf5094ebaf0b36646aeb32daa9a46735fd19e"),
                ("Leah", "2024-07-01 05:21:47.385710",
                 "bf695dd6d1dc6c3987aa5cbd46b9f0035cf65fda")
            ]
        )


def populate_reviews(cursor):
    cursor.execute(
        'CREATE TABLE IF NOT EXISTS review (review_id INTEGER PRIMARY KEY AUTOINCREMENT, game_id INTEGER, user INTEGER, review REAL, rating INTEGER, platform INTEGER, image_blob BLOB NULL)')
    cursor.execute('SELECT COUNT(*) FROM review')
    count = cursor.fetchone()[0]
    if count == 0:
        cursor.executemany(
            'INSERT INTO review (game_id, user, review, rating, platform, image_blob) VALUES (?, ?, ?, ?, ?, ?)',
            [
                (1, 2, "Eu amo esse jogo!", 5, 1, convert_image_to_blob(
                    'API/mock_resources/blob_1.webp')),
                (2, 4, "A animação é melhor que o jogo!", 3, 2,
                 convert_image_to_blob('API/mock_resources/blob_2.webp')),
                (3, 3, "Terrível!", 2, 1, convert_image_to_blob(
                    'API/mock_resources/blob_3.webp')),
                (4, 2, "Um dos melhores zeldas da história", 5, 1,
                 convert_image_to_blob('API/mock_resources/blob_4.webp')),
                (5, 1, "Exemplo de sequência boa!", 1, 2,
                 convert_image_to_blob('API/mock_resources/blob_5.webp'))
            ]
        )


def populate_games(cursor):
    cursor.execute(
        'CREATE TABLE IF NOT EXISTS game (game_id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT,genre TEXT, createdOn DATE, developer TEXT, publisher TEXT )')
    cursor.execute('SELECT COUNT(*) FROM game')
    count = cursor.fetchone()[0]
    print(count)
    if count == 0:
        cursor.executemany(
            'INSERT INTO game (name, genre, createdOn, developer, publisher) VALUES (?, ?, ?, ?, ?)',
            [
                ("Super Mario Odyssey", "Platform",
                 "2017-10-27", "Nintendo EPD", "Nintendo"),
                ("Transistor", "Action", "2014-05-20",
                 "Supergiant Games", "Supergiant Games"),
                ("The Last of Us Part II", "Action", "2020-06-19",
                 "Naughty Dog", "Sony Interactive Entertainment"),
                ("The Legend of Zelda: Breath of the Wild",
                 "Adventure", "2017-03-03", "Nintendo EPD", "Nintendo"),
                ("The Witcher 3: Wild Hunt", "RPG",
                 "2015-05-19", "CD Projekt Red", "CD Projekt"),
            ]
        )
