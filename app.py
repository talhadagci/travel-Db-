from flask import Flask, jsonify, request, send_from_directory, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import sqlite3
import os
import secrets

app = Flask(__name__, static_folder='.')

_KEY_FILE = os.path.join(os.path.dirname(__file__), '.secret_key')
if os.path.exists(_KEY_FILE):
    with open(_KEY_FILE) as f:
        app.secret_key = f.read().strip()
else:
    _key = secrets.token_hex(32)
    with open(_KEY_FILE, 'w') as f:
        f.write(_key)
    app.secret_key = _key

CORS(app, supports_credentials=True)

DB_PATH     = os.path.join(os.path.dirname(__file__), 'turkey_travel.db')
UPLOAD_DIR  = os.path.join(os.path.dirname(__file__), 'uploads')
ALLOWED_EXT = {'jpg', 'jpeg', 'png', 'webp'}
os.makedirs(UPLOAD_DIR, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT

CITIES = [
    (1,  'İstanbul', 'Marmara',      'İki kıtayı birleştiren İstanbul; binlerce yıllık Bizans ve Osmanlı mirasını, Boğazın muhteşem manzarasıyla harmanlıyor.',                                     'Tarih,Müze,Yemek'),
    (2,  'Ankara',   'İç Anadolu',   'Türkiye Cumhuriyetinin başkenti Ankara; Atatürkün anıt mezarından Hitit eserlerine uzanan zengin kültür mirasıyla öne çıkar.',                                 'Müze,Tarih'),
    (3,  'Antalya',  'Akdeniz',      'Akdenizin incisi Antalya; turkuaz suları, antik kentleri ve Roma kalıntılarıyla tarih ile doğayı bir arada sunar.',                                            'Tarih,Doğa,Yemek'),
    (4,  'İzmir',    'Ege',          'Egenin kozmopolit kalbi İzmir; antik Efesten Kemeraltı çarşısına uzanan kültürel zenginliği ve sıcakkanlı insanlarıyla öne çıkar.',                            'Tarih,Yemek,Doğa'),
    (5,  'Muğla',    'Ege',          'Bodrum, Marmaris, Fethiye ve Ölüdenizi bünyesinde barındıran Muğla; dünyanın en güzel koylarını sunar.',                                                       'Doğa,Yemek'),
    (6,  'Nevşehir', 'İç Anadolu',   'Kapadokyanın kalbi Nevşehir; peri bacaları, yeraltı şehirleri ve şafakta gökyüzünü dolduran balonlarıyla eşsiz bir coğrafyadır.',                             'Tarih,Doğa,Müze'),
    (7,  'Bursa',    'Marmara',      'Osmanlının ilk başkenti Bursa; Ulu Camiden Yeşil Türbeye uzanan tarihi dokusu ve İskender kebabıyla öne çıkar.',                                               'Tarih,Yemek,Doğa'),
    (8,  'Trabzon',  'Karadeniz',    'Karadenizin yeşil başkenti Trabzon; Sümela Manastırı, Uzungöl yaylası ve hamsi ile kuymakın buluştuğu özgün mutfağıyla tanınır.',                             'Tarih,Doğa,Yemek'),
    (9,  'Mardin',   'Güneydoğu',    'Mezopotamya ovasına hükmeden Mardin; sarı taş evleri, manastırları ve minareleriyle masalsı bir silüet çizer.',                                                'Tarih,Müze,Yemek'),
    (10, 'Aydın',    'Ege',          'Dünyaca ünlü Efes antik kentine ev sahipliği yapan Aydın; zengin arkeolojik mirası ve Ege kıyılarıyla ziyaretçileri büyüler.',                                'Tarih,Doğa'),
]

PLACES = [
    ('Ayasofya',                'İstanbul', 'Tarihi Yer', 'tarih', 4.9, 'Bizans ve Osmanlı döneminden kalma ikonik yapı.',          '🏛️', 'Ayasofya Fetih Camii'),
    ('Topkapı Sarayı',          'İstanbul', 'Tarihi Yer', 'tarih', 4.8, '600 yıllık Osmanlı sarayı ve hazine koleksiyonu.',          '👑', 'Topkapı Sarayı'),
    ('Göreme Milli Parkı',      'Nevşehir', 'Doğa',       'doga',  4.9, 'Peri bacaları ve balon turları.',                           '🌄', 'Göreme'),
    ('Derinkuyu Yeraltı Şehri', 'Nevşehir', 'Tarihi Yer', 'tarih', 4.8, '8 kat derinliğe inen antik yeraltı şehri.',                 '🏺', 'Yeraltı Şehirleri'),
    ('Aspendos Tiyatrosu',      'Antalya',  'Tarihi Yer', 'tarih', 4.9, 'Roma döneminden hâlâ kullanılan tiyatro.',                  '🎭', 'Side Antik Kent'),
    ('Antalya Müzesi',          'Antalya',  'Müze',       'muze',  4.7, 'Dünyanın en zengin arkeoloji müzelerinden.',                '🗿', 'Oyuncak Müzesi'),
    ('Sümela Manastırı',        'Trabzon',  'Tarihi Yer', 'tarih', 4.9, 'Kaya yüzeyine inşa edilmiş Bizans manastırı.',              '⛪', 'Sümela Manastırı'),
    ('Uzungöl',                 'Trabzon',  'Doğa',       'doga',  4.8, 'Karadeniz yaylasında saklı göl.',                           '🏞️', 'Uzungöl'),
    ('Deyrulzafaran Manastırı', 'Mardin',   'Tarihi Yer', 'tarih', 4.9, 'MS 493 tarihli Süryani manastırı.',                         '🕌', 'Deyrulzafaran Manastırı'),
    ('Efes Antik Kenti',        'Aydın',    'Tarihi Yer', 'tarih', 5.0, 'Dünyanın en iyi korunmuş antik kentlerinden.',              '🏟️', 'Efes Antik Kenti'),
]

SEED_REVIEWS = [
    ('İstanbul', 'Ahmet Y.',  5, "Ayasofya'yı görünce tarihin içinde kayboluyorsunuz. Hayatımda gördüğüm en etkileyici yapı."),
    ('İstanbul', 'Selin K.',  5, "Kapalıçarşı'da saatlerce dolaştık. Boğaz turu şart, günbatımında Köprü manzarası unutulmaz."),
    ('İstanbul', 'Burak T.',  4, "Topkapı Sarayı'nı rehberle gezmek çok daha verimli oluyor. Hazine bölümü inanılmaz."),
    ('Ankara',   'Deniz A.',  5, "Anıtkabir her Türk'ün mutlaka görmesi gereken bir yer. Duygu yüklü, tarihi bir deneyim."),
    ('Ankara',   'Murat S.',  4, "Anadolu Medeniyetleri Müzesi dünya standartlarında. Hitit eserleri nefes kesiyor."),
    ('Antalya',  'Fatma D.',  5, "Aspendos tiyatrosunu görünce insan Roma'nın büyüklüğü karşısında küçülüyor."),
    ('Antalya',  'Can M.',    5, "Kaleiçi'nde kaybolmak ayrı bir keyif. Dar taş sokaklar ve yat limanı manzarası harikaydı."),
    ('Antalya',  'Zehra K.',  4, "Antalya Müzesi için tam gün ayırın. Perge heykelleri dünya müzelerinde aranan eserler."),
    ('İzmir',    'Emre B.',   5, "Efes'i İzmir'den günübirlik gezmek çok kolay. Celsus Kütüphanesi muhteşem çıkıyor."),
    ('İzmir',    'Pınar Y.',  4, "Kemeraltı Çarşısı'nda yerel lezzetleri tatmak şart. Boyoz ve gevrek olmadan İzmir olmaz."),
    ('Muğla',    'Ali K.',    5, "Ölüdeniz'deki mavi lagün fotoğraflarda gördüğümden çok daha güzeldi."),
    ('Muğla',    'Hande T.',  5, "Bodrum'da tekne kiralayıp koyları gezmek en doğru karar. Her koy birbirinden güzel."),
    ('Nevşehir', 'Zeynep K.', 5, "Sabah balonuyla izlediğimizde peri bacaları bambaşka görünüyor. Hayatımın en güzel deneyimi."),
    ('Nevşehir', 'Onur S.',   5, "Derinkuyu yeraltı şehri inanılmaz mühendislik. 8 kat aşağıya inince tarih karşısında küçülüyorsunuz."),
    ('Nevşehir', 'Lale M.',   4, "Göreme'de butik otel şart. Peri bacasına oyulmuş odada kalmak ayrı bir deneyim."),
    ('Bursa',    'Serkan A.', 5, "Uludağ'da kayak yaparken Bursa manzarası görülmeye değer. Teleferik yolculuğu da harikaydı."),
    ('Bursa',    'Ceyda K.',  4, "Ulu Cami içindeki şadırvan ve hat yazıları inanılmaz. Osmanlı mimarisinin en güzel örnekleri."),
    ('Trabzon',  'Mehmet A.', 5, "Sümela Manastırı'nı görmek için yağmurlu hava bile sorun değil. Mistik atmosferi başka."),
    ('Trabzon',  'Seda Y.',   5, "Uzungöl sabah sisinde bambaşka. Yaylalarda çay bahçelerinde oturmak zamanı durduruyor."),
    ('Trabzon',  'Bora K.',   4, "Kuymak ve hamsi tava olmadan Trabzon olmaz. Karadeniz mutfağı gerçekten enfes."),
    ('Mardin',   'Can S.',    5, "Mardin'e gittiğimde en çok Deyrulzafaran etkiledi. Süryani kültürünün derin izlerini hissediyorsunuz."),
    ('Mardin',   'Ayşe T.',   5, "Taş evlerin arasında dolaşmak, Mezopotamya'ya bakmak başka hiçbir yerde yaşanmaz."),
    ('Mardin',   'Kaan M.',   4, "Cercis Murat Konağı'nda akşam yemeği için rezervasyon şart. Manzara ve yemek mükemmel."),
    ('Aydın',    'Fatma D.',  5, "Efes Antik Kenti'ni görmeden Türkiye'yi görmüş sayılmazsınız."),
    ('Aydın',    'Tolga K.',  5, "Afrodisias daha az kalabalık ama Efes kadar etkileyici. Mermer işçiliği inanılmaz."),
]


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn


def init_db():
    conn = get_db()
    c = conn.cursor()
    c.executescript('''
        CREATE TABLE IF NOT EXISTS cities (
            id      INTEGER PRIMARY KEY,
            name    TEXT    UNIQUE NOT NULL,
            region  TEXT    NOT NULL,
            description TEXT,
            tags    TEXT
        );

        CREATE TABLE IF NOT EXISTS users (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            username     TEXT    UNIQUE NOT NULL,
            email        TEXT    UNIQUE NOT NULL,
            password     TEXT    NOT NULL,
            role         TEXT    DEFAULT 'user',
            bio          TEXT,
            location     TEXT,
            avatar_color TEXT    DEFAULT '#C1272D',
            created_at   DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS favorites (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL,
            city_id    INTEGER NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, city_id),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (city_id) REFERENCES cities(id)
        );

        CREATE TABLE IF NOT EXISTS review_likes (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL,
            review_id  INTEGER NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, review_id),
            FOREIGN KEY (user_id)   REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (review_id) REFERENCES reviews(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS city_views (
            city_id    INTEGER PRIMARY KEY,
            view_count INTEGER DEFAULT 0,
            FOREIGN KEY (city_id) REFERENCES cities(id)
        );

        CREATE TABLE IF NOT EXISTS trips (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            title       TEXT    NOT NULL,
            start_date  TEXT,
            end_date    TEXT,
            description TEXT,
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS trip_stops (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            trip_id    INTEGER NOT NULL,
            city_id    INTEGER NOT NULL,
            city_name  TEXT    NOT NULL,
            stop_order INTEGER NOT NULL DEFAULT 0,
            notes      TEXT,
            FOREIGN KEY (trip_id) REFERENCES trips(id) ON DELETE CASCADE,
            FOREIGN KEY (city_id) REFERENCES cities(id)
        );

        CREATE TABLE IF NOT EXISTS photos (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL,
            city_id    INTEGER NOT NULL,
            city_name  TEXT    NOT NULL,
            file_path  TEXT    NOT NULL,
            caption    TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (city_id) REFERENCES cities(id)
        );

        CREATE TABLE IF NOT EXISTS notifications (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL,
            message    TEXT    NOT NULL,
            link       TEXT,
            is_read    INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS places (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            name         TEXT    NOT NULL,
            city_id      INTEGER NOT NULL,
            city_name    TEXT    NOT NULL,
            category     TEXT    NOT NULL,
            category_key TEXT    NOT NULL,
            rating       REAL    NOT NULL DEFAULT 0,
            description  TEXT,
            icon         TEXT,
            img_key      TEXT,
            FOREIGN KEY (city_id) REFERENCES cities(id)
        );

        CREATE TABLE IF NOT EXISTS reviews (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            city_id       INTEGER NOT NULL,
            city_name     TEXT    NOT NULL,
            reviewer_name TEXT    NOT NULL,
            rating        INTEGER NOT NULL CHECK(rating >= 1 AND rating <= 5),
            text          TEXT    NOT NULL,
            user_id       INTEGER,
            created_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (city_id)  REFERENCES cities(id),
            FOREIGN KEY (user_id)  REFERENCES users(id)
        );
    ''')

    city_id_map = {row[1]: row[0] for row in c.execute('SELECT id, name FROM cities').fetchall()}

    for place in PLACES:
        name, city_name = place[0], place[1]
        city_id = city_id_map.get(city_name, 1)
        c.execute(
            '''INSERT OR IGNORE INTO places (name, city_id, city_name, category, category_key, rating, description, icon, img_key)
               SELECT ?,?,?,?,?,?,?,?,? WHERE NOT EXISTS (SELECT 1 FROM places WHERE name=? AND city_name=?)''',
            (name, city_id, *place[1:], name, city_name)
        )

    seeded = c.execute('SELECT COUNT(*) FROM reviews').fetchone()[0]
    if seeded == 0:
        for row in SEED_REVIEWS:
            city_name = row[0]
            city_id   = city_id_map.get(city_name, 1)
            c.execute(
                'INSERT INTO reviews (city_id, city_name, reviewer_name, rating, text) VALUES (?,?,?,?,?)',
                (city_id, *row)
            )

    conn.commit()
    conn.close()


# ── Auth ───────────────────────────────────────────────────────────────────
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json(silent=True) or {}
    username = str(data.get('username', '')).strip()
    email    = str(data.get('email',    '')).strip().lower()
    password = str(data.get('password', '')).strip()

    if not username or not email or not password:
        return jsonify({'error': 'Tüm alanlar zorunlu'}), 400
    if len(username) < 3:
        return jsonify({'error': 'Kullanıcı adı en az 3 karakter olmalı'}), 400
    if '@' not in email:
        return jsonify({'error': 'Geçerli bir e-posta girin'}), 400
    if len(password) < 6:
        return jsonify({'error': 'Şifre en az 6 karakter olmalı'}), 400

    conn = get_db()
    try:
        conn.execute(
            'INSERT INTO users (username, email, password) VALUES (?,?,?)',
            (username, email, generate_password_hash(password))
        )
        conn.commit()
        user = conn.execute('SELECT id, username, email FROM users WHERE email=?', (email,)).fetchone()
        session['user_id']   = user['id']
        session['username']  = user['username']
        return jsonify({'success': True, 'username': user['username']}), 201
    except sqlite3.IntegrityError as e:
        msg = 'Bu e-posta zaten kayıtlı' if 'email' in str(e) else 'Bu kullanıcı adı alınmış'
        return jsonify({'error': msg}), 409
    finally:
        conn.close()


@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    email    = str(data.get('email',    '')).strip().lower()
    password = str(data.get('password', '')).strip()

    if not email or not password:
        return jsonify({'error': 'E-posta ve şifre gerekli'}), 400

    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE email=?', (email,)).fetchone()
    conn.close()

    if not user or not check_password_hash(user['password'], password):
        return jsonify({'error': 'E-posta veya şifre hatalı'}), 401

    session['user_id']  = user['id']
    session['username'] = user['username']
    session['role']     = user['role'] or 'user'
    return jsonify({'success': True, 'username': user['username'], 'role': session['role']})


@app.route('/api/auth/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True})


@app.route('/api/auth/me', methods=['GET'])
def me():
    if 'user_id' in session:
        conn = get_db()
        user = conn.execute('SELECT role FROM users WHERE id = ?', (session['user_id'],)).fetchone()
        conn.close()
        role = user['role'] if user else 'user'
        session['role'] = role
        return jsonify({'loggedIn': True, 'username': session['username'], 'user_id': session['user_id'], 'role': role})
    return jsonify({'loggedIn': False})


# ── Sayfaları sun ──────────────────────────────────────────────────────────
@app.route('/')
def index():
    return send_from_directory('.', 'turkey_travel(12).html')

@app.route('/login')
def login_page():
    return send_from_directory('.', 'login.html')

@app.route('/fotograflar/<path:filename>')
def static_photos(filename):
    return send_from_directory('fotograflar', filename)


# ── Şehirler ───────────────────────────────────────────────────────────────
@app.route('/api/cities', methods=['GET'])
def get_cities():
    conn = get_db()
    rows = conn.execute('SELECT * FROM cities ORDER BY id').fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        d['tags'] = d['tags'].split(',') if d['tags'] else []
        result.append(d)
    return jsonify(result)


@app.route('/api/cities/<city_name>', methods=['GET'])
def get_city(city_name):
    conn = get_db()
    city = conn.execute('SELECT * FROM cities WHERE name = ?', (city_name,)).fetchone()
    if not city:
        conn.close()
        return jsonify({'error': 'Şehir bulunamadı'}), 404
    d = dict(city)
    d['tags'] = d['tags'].split(',') if d['tags'] else []
    conn.close()
    return jsonify(d)


# ── Popüler Yerler ─────────────────────────────────────────────────────────
@app.route('/api/places', methods=['GET'])
def get_places():
    city = request.args.get('city')
    conn = get_db()
    if city:
        rows = conn.execute(
            'SELECT * FROM places WHERE city_name = ? ORDER BY rating DESC', (city,)
        ).fetchall()
    else:
        rows = conn.execute('SELECT * FROM places ORDER BY rating DESC').fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


# ── Yorumlar ───────────────────────────────────────────────────────────────
@app.route('/api/reviews/<city_name>', methods=['GET'])
def get_reviews(city_name):
    conn = get_db()
    rows = conn.execute(
        '''SELECT id, city_name, reviewer_name, rating, text, user_id,
                  strftime('%m/%Y', created_at) AS date
           FROM reviews
           WHERE city_name = ?
           ORDER BY created_at DESC''',
        (city_name,)
    ).fetchall()
    conn.close()
    result = []
    months = ['','Ocak','Şubat','Mart','Nisan','Mayıs','Haziran',
              'Temmuz','Ağustos','Eylül','Ekim','Kasım','Aralık']
    for r in rows:
        d = dict(r)
        m, y = d['date'].split('/')
        d['date'] = f"{months[int(m)]} {y}"
        result.append(d)
    return jsonify(result)


@app.route('/api/reviews/<city_name>', methods=['POST'])
def add_review(city_name):
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'JSON verisi bekleniyor'}), 400

    name   = str(data.get('name',  '')).strip()
    text   = str(data.get('text',  '')).strip()
    rating = data.get('rating')

    if not name:
        return jsonify({'error': 'Ad gerekli'}), 400
    if not text:
        return jsonify({'error': 'Yorum metni gerekli'}), 400
    if not isinstance(rating, int) or rating < 1 or rating > 5:
        return jsonify({'error': 'Puan 1-5 arasında olmalı'}), 400
    if len(name) > 100:
        return jsonify({'error': 'Ad çok uzun'}), 400
    if len(text) > 1000:
        return jsonify({'error': 'Yorum metni çok uzun'}), 400

    conn = get_db()
    city_exists = conn.execute('SELECT 1 FROM cities WHERE name = ?', (city_name,)).fetchone()
    if not city_exists:
        conn.close()
        return jsonify({'error': 'Geçersiz şehir'}), 404

    city_row = conn.execute('SELECT id FROM cities WHERE name = ?', (city_name,)).fetchone()
    city_id  = city_row['id']
    user_id  = session.get('user_id')
    cursor = conn.execute(
        'INSERT INTO reviews (city_id, city_name, reviewer_name, rating, text, user_id) VALUES (?,?,?,?,?,?)',
        (city_id, city_name, name, rating, text, user_id)
    )
    conn.commit()
    review_id = cursor.lastrowid
    conn.close()
    return jsonify({'success': True, 'id': review_id}), 201


@app.route('/api/reviews/<int:review_id>', methods=['PUT'])
def update_review(review_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Giriş yapmalısın'}), 401

    data   = request.get_json(silent=True) or {}
    text   = str(data.get('text',   '')).strip()
    rating = data.get('rating')

    if not text:
        return jsonify({'error': 'Yorum metni gerekli'}), 400
    if not isinstance(rating, int) or rating < 1 or rating > 5:
        return jsonify({'error': 'Puan 1-5 arasında olmalı'}), 400
    if len(text) > 1000:
        return jsonify({'error': 'Yorum metni çok uzun'}), 400

    conn = get_db()
    review = conn.execute('SELECT user_id FROM reviews WHERE id = ?', (review_id,)).fetchone()
    if not review:
        conn.close()
        return jsonify({'error': 'Yorum bulunamadı'}), 404
    if review['user_id'] != session['user_id']:
        conn.close()
        return jsonify({'error': 'Bu yorumu düzenleme yetkin yok'}), 403

    conn.execute('UPDATE reviews SET text = ?, rating = ? WHERE id = ?', (text, rating, review_id))
    conn.commit()
    conn.close()
    return jsonify({'success': True})


@app.route('/api/reviews/<int:review_id>', methods=['DELETE'])
def delete_review(review_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Giriş yapmalısın'}), 401

    conn = get_db()
    review = conn.execute('SELECT user_id FROM reviews WHERE id = ?', (review_id,)).fetchone()
    if not review:
        conn.close()
        return jsonify({'error': 'Yorum bulunamadı'}), 404
    if review['user_id'] != session['user_id']:
        conn.close()
        return jsonify({'error': 'Bu yorumu silme yetkin yok'}), 403

    conn.execute('DELETE FROM reviews WHERE id = ?', (review_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})


# ── Arama ─────────────────────────────────────────────────────────────────
@app.route('/api/search', methods=['GET'])
def search():
    q = request.args.get('q', '').strip()
    if len(q) < 2:
        return jsonify({'cities': [], 'places': []})
    like = f'%{q}%'
    conn = get_db()
    cities = conn.execute(
        'SELECT id, name, region, description FROM cities WHERE name LIKE ? OR region LIKE ? OR description LIKE ? LIMIT 5',
        (like, like, like)
    ).fetchall()
    places = conn.execute(
        'SELECT id, name, city_name, category, description FROM places WHERE name LIKE ? OR description LIKE ? OR city_name LIKE ? LIMIT 8',
        (like, like, like)
    ).fetchall()
    conn.close()
    return jsonify({'cities': [dict(r) for r in cities], 'places': [dict(r) for r in places]})


# ── Şehir Görüntülenme ────────────────────────────────────────────────────
@app.route('/api/cities/<city_name>/view', methods=['POST'])
def record_view(city_name):
    conn = get_db()
    city = conn.execute('SELECT id FROM cities WHERE name = ?', (city_name,)).fetchone()
    if city:
        conn.execute('UPDATE city_views SET view_count = view_count + 1 WHERE city_id = ?', (city['id'],))
        conn.commit()
    conn.close()
    return jsonify({'success': True})


# ── Favoriler ─────────────────────────────────────────────────────────────
@app.route('/api/favorites', methods=['GET'])
def get_favorites():
    if 'user_id' not in session:
        return jsonify([])
    conn = get_db()
    rows = conn.execute(
        '''SELECT c.id, c.name, c.region, c.description, c.tags
           FROM favorites f JOIN cities c ON f.city_id = c.id
           WHERE f.user_id = ? ORDER BY f.created_at DESC''',
        (session['user_id'],)
    ).fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        d['tags'] = d['tags'].split(',') if d['tags'] else []
        result.append(d)
    return jsonify(result)


@app.route('/api/favorites/<city_name>', methods=['POST'])
def toggle_favorite(city_name):
    if 'user_id' not in session:
        return jsonify({'error': 'Giriş yapmalısın'}), 401
    conn = get_db()
    city = conn.execute('SELECT id FROM cities WHERE name = ?', (city_name,)).fetchone()
    if not city:
        conn.close()
        return jsonify({'error': 'Şehir bulunamadı'}), 404
    existing = conn.execute(
        'SELECT id FROM favorites WHERE user_id = ? AND city_id = ?',
        (session['user_id'], city['id'])
    ).fetchone()
    if existing:
        conn.execute('DELETE FROM favorites WHERE id = ?', (existing['id'],))
        conn.commit()
        conn.close()
        return jsonify({'favorited': False})
    else:
        conn.execute('INSERT INTO favorites (user_id, city_id) VALUES (?,?)', (session['user_id'], city['id']))
        conn.commit()
        conn.close()
        _push_notification(session['user_id'], f"'{city_name}' favorilerine eklendi ❤️")
        return jsonify({'favorited': True})


@app.route('/api/favorites/<city_name>/status', methods=['GET'])
def favorite_status(city_name):
    if 'user_id' not in session:
        return jsonify({'favorited': False})
    conn = get_db()
    city = conn.execute('SELECT id FROM cities WHERE name = ?', (city_name,)).fetchone()
    if not city:
        conn.close()
        return jsonify({'favorited': False})
    exists = conn.execute(
        'SELECT 1 FROM favorites WHERE user_id = ? AND city_id = ?',
        (session['user_id'], city['id'])
    ).fetchone()
    conn.close()
    return jsonify({'favorited': bool(exists)})


# ── Yorum Beğeni ──────────────────────────────────────────────────────────
@app.route('/api/reviews/<int:review_id>/like', methods=['POST'])
def toggle_like(review_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Giriş yapmalısın'}), 401
    conn = get_db()
    review = conn.execute('SELECT id, user_id FROM reviews WHERE id = ?', (review_id,)).fetchone()
    if not review:
        conn.close()
        return jsonify({'error': 'Yorum bulunamadı'}), 404
    existing = conn.execute(
        'SELECT id FROM review_likes WHERE user_id = ? AND review_id = ?',
        (session['user_id'], review_id)
    ).fetchone()
    if existing:
        conn.execute('DELETE FROM review_likes WHERE id = ?', (existing['id'],))
        liked = False
    else:
        conn.execute('INSERT INTO review_likes (user_id, review_id) VALUES (?,?)', (session['user_id'], review_id))
        liked = True
        if review['user_id'] and review['user_id'] != session['user_id']:
            _push_notification(review['user_id'], f"{session['username']} yorumunu beğendi 👍")
    count = conn.execute('SELECT COUNT(*) FROM review_likes WHERE review_id = ?', (review_id,)).fetchone()[0]
    conn.commit()
    conn.close()
    return jsonify({'liked': liked, 'count': count})


# ── Profil ────────────────────────────────────────────────────────────────
@app.route('/api/profile', methods=['GET'])
def get_profile():
    if 'user_id' not in session:
        return jsonify({'error': 'Giriş yapmalısın'}), 401
    conn = get_db()
    user = conn.execute(
        'SELECT id, username, email, bio, location, avatar_color, role, created_at FROM users WHERE id = ?',
        (session['user_id'],)
    ).fetchone()
    fav_count    = conn.execute('SELECT COUNT(*) FROM favorites WHERE user_id = ?', (session['user_id'],)).fetchone()[0]
    review_count = conn.execute('SELECT COUNT(*) FROM reviews WHERE user_id = ?', (session['user_id'],)).fetchone()[0]
    trip_count   = conn.execute('SELECT COUNT(*) FROM trips WHERE user_id = ?', (session['user_id'],)).fetchone()[0]
    conn.close()
    d = dict(user)
    d['fav_count']    = fav_count
    d['review_count'] = review_count
    d['trip_count']   = trip_count
    return jsonify(d)


@app.route('/api/profile', methods=['PUT'])
def update_profile():
    if 'user_id' not in session:
        return jsonify({'error': 'Giriş yapmalısın'}), 401
    data     = request.get_json(silent=True) or {}
    bio      = str(data.get('bio',      '')).strip()[:300]
    location = str(data.get('location', '')).strip()[:100]
    color    = str(data.get('avatar_color', '#C1272D')).strip()
    conn = get_db()
    conn.execute(
        'UPDATE users SET bio = ?, location = ?, avatar_color = ? WHERE id = ?',
        (bio, location, color, session['user_id'])
    )
    conn.commit()
    conn.close()
    return jsonify({'success': True})


# ── Seyahat Planları ──────────────────────────────────────────────────────
@app.route('/api/trips', methods=['GET'])
def get_trips():
    if 'user_id' not in session:
        return jsonify([])
    conn = get_db()
    trips = conn.execute(
        'SELECT * FROM trips WHERE user_id = ? ORDER BY created_at DESC',
        (session['user_id'],)
    ).fetchall()
    result = []
    for t in trips:
        d = dict(t)
        stops = conn.execute(
            'SELECT * FROM trip_stops WHERE trip_id = ? ORDER BY stop_order',
            (t['id'],)
        ).fetchall()
        d['stops'] = [dict(s) for s in stops]
        result.append(d)
    conn.close()
    return jsonify(result)


@app.route('/api/trips', methods=['POST'])
def create_trip():
    if 'user_id' not in session:
        return jsonify({'error': 'Giriş yapmalısın'}), 401
    data  = request.get_json(silent=True) or {}
    title = str(data.get('title', '')).strip()
    if not title:
        return jsonify({'error': 'Plan adı gerekli'}), 400
    conn = get_db()
    cur = conn.execute(
        'INSERT INTO trips (user_id, title, start_date, end_date, description) VALUES (?,?,?,?,?)',
        (session['user_id'], title, data.get('start_date'), data.get('end_date'), data.get('description',''))
    )
    conn.commit()
    trip_id = cur.lastrowid
    conn.close()
    _push_notification(session['user_id'], f"Yeni seyahat planı oluşturuldu: '{title}' 🗺️")
    return jsonify({'success': True, 'id': trip_id}), 201


@app.route('/api/trips/<int:trip_id>', methods=['DELETE'])
def delete_trip(trip_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Giriş yapmalısın'}), 401
    conn = get_db()
    trip = conn.execute('SELECT user_id FROM trips WHERE id = ?', (trip_id,)).fetchone()
    if not trip or trip['user_id'] != session['user_id']:
        conn.close()
        return jsonify({'error': 'Yetkisiz'}), 403
    conn.execute('DELETE FROM trips WHERE id = ?', (trip_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})


@app.route('/api/trips/<int:trip_id>/stops', methods=['POST'])
def add_stop(trip_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Giriş yapmalısın'}), 401
    data      = request.get_json(silent=True) or {}
    city_name = str(data.get('city_name', '')).strip()
    notes     = str(data.get('notes', '')).strip()[:500]
    conn = get_db()
    trip = conn.execute('SELECT user_id FROM trips WHERE id = ?', (trip_id,)).fetchone()
    if not trip or trip['user_id'] != session['user_id']:
        conn.close()
        return jsonify({'error': 'Yetkisiz'}), 403
    city = conn.execute('SELECT id FROM cities WHERE name = ?', (city_name,)).fetchone()
    if not city:
        conn.close()
        return jsonify({'error': 'Şehir bulunamadı'}), 404
    order = (conn.execute('SELECT MAX(stop_order) FROM trip_stops WHERE trip_id = ?', (trip_id,)).fetchone()[0] or 0) + 1
    cur = conn.execute(
        'INSERT INTO trip_stops (trip_id, city_id, city_name, stop_order, notes) VALUES (?,?,?,?,?)',
        (trip_id, city['id'], city_name, order, notes)
    )
    conn.commit()
    stop_id = cur.lastrowid
    conn.close()
    return jsonify({'success': True, 'id': stop_id}), 201


@app.route('/api/trips/<int:trip_id>/stops/<int:stop_id>', methods=['DELETE'])
def delete_stop(trip_id, stop_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Giriş yapmalısın'}), 401
    conn = get_db()
    trip = conn.execute('SELECT user_id FROM trips WHERE id = ?', (trip_id,)).fetchone()
    if not trip or trip['user_id'] != session['user_id']:
        conn.close()
        return jsonify({'error': 'Yetkisiz'}), 403
    conn.execute('DELETE FROM trip_stops WHERE id = ? AND trip_id = ?', (stop_id, trip_id))
    conn.commit()
    conn.close()
    return jsonify({'success': True})


# ── Fotoğraflar ───────────────────────────────────────────────────────────
@app.route('/api/photos/<city_name>', methods=['GET'])
def get_photos(city_name):
    conn = get_db()
    rows = conn.execute(
        '''SELECT p.id, p.file_path, p.caption, p.created_at, u.username
           FROM photos p JOIN users u ON p.user_id = u.id
           WHERE p.city_name = ? ORDER BY p.created_at DESC''',
        (city_name,)
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route('/api/photos', methods=['POST'])
def upload_photo():
    if 'user_id' not in session:
        return jsonify({'error': 'Giriş yapmalısın'}), 401
    if 'photo' not in request.files:
        return jsonify({'error': 'Fotoğraf seçilmedi'}), 400
    file      = request.files['photo']
    city_name = request.form.get('city_name', '').strip()
    caption   = request.form.get('caption', '').strip()[:200]
    if not file.filename or not allowed_file(file.filename):
        return jsonify({'error': 'Geçersiz dosya (jpg/png/webp)'}), 400
    conn = get_db()
    city = conn.execute('SELECT id FROM cities WHERE name = ?', (city_name,)).fetchone()
    if not city:
        conn.close()
        return jsonify({'error': 'Şehir bulunamadı'}), 404
    ext      = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{session['user_id']}_{city['id']}_{secrets.token_hex(6)}.{ext}"
    file.save(os.path.join(UPLOAD_DIR, filename))
    cur = conn.execute(
        'INSERT INTO photos (user_id, city_id, city_name, file_path, caption) VALUES (?,?,?,?,?)',
        (session['user_id'], city['id'], city_name, filename, caption)
    )
    conn.commit()
    conn.close()
    _push_notification(session['user_id'], f"'{city_name}' için fotoğraf yüklendi 📷")
    return jsonify({'success': True, 'file': filename}), 201


@app.route('/api/photos/<int:photo_id>', methods=['DELETE'])
def delete_photo(photo_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Giriş yapmalısın'}), 401
    conn = get_db()
    photo = conn.execute('SELECT user_id, file_path FROM photos WHERE id = ?', (photo_id,)).fetchone()
    if not photo:
        conn.close()
        return jsonify({'error': 'Bulunamadı'}), 404
    if photo['user_id'] != session['user_id'] and session.get('role') != 'admin':
        conn.close()
        return jsonify({'error': 'Yetkisiz'}), 403
    fpath = os.path.join(UPLOAD_DIR, photo['file_path'])
    if os.path.exists(fpath):
        os.remove(fpath)
    conn.execute('DELETE FROM photos WHERE id = ?', (photo_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})


@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_DIR, filename)


# ── Bildirimler ───────────────────────────────────────────────────────────
def _push_notification(user_id, message, link=None):
    conn = get_db()
    conn.execute('INSERT INTO notifications (user_id, message, link) VALUES (?,?,?)', (user_id, message, link))
    conn.commit()
    conn.close()


@app.route('/api/notifications', methods=['GET'])
def get_notifications():
    if 'user_id' not in session:
        return jsonify([])
    conn = get_db()
    rows = conn.execute(
        'SELECT * FROM notifications WHERE user_id = ? ORDER BY created_at DESC LIMIT 30',
        (session['user_id'],)
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route('/api/notifications/read-all', methods=['PUT'])
def read_all_notifications():
    if 'user_id' not in session:
        return jsonify({'error': 'Giriş yapmalısın'}), 401
    conn = get_db()
    conn.execute('UPDATE notifications SET is_read = 1 WHERE user_id = ?', (session['user_id'],))
    conn.commit()
    conn.close()
    return jsonify({'success': True})


# ── Admin ─────────────────────────────────────────────────────────────────
def require_admin(f):
    from functools import wraps
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Giriş yapmalısın'}), 401
        conn = get_db()
        user = conn.execute('SELECT role FROM users WHERE id = ?', (session['user_id'],)).fetchone()
        conn.close()
        if not user or user['role'] != 'admin':
            return jsonify({'error': 'Admin yetkisi gerekli'}), 403
        return f(*args, **kwargs)
    return wrapper


@app.route('/api/admin/users', methods=['GET'])
@require_admin
def admin_get_users():
    conn = get_db()
    rows = conn.execute(
        '''SELECT u.id, u.username, u.email, u.role, u.location, u.created_at,
                  COUNT(DISTINCT r.id) AS review_count,
                  COUNT(DISTINCT f.id) AS fav_count,
                  COUNT(DISTINCT t.id) AS trip_count
           FROM users u
           LEFT JOIN reviews   r ON r.user_id = u.id
           LEFT JOIN favorites f ON f.user_id = u.id
           LEFT JOIN trips     t ON t.user_id = u.id
           GROUP BY u.id ORDER BY u.created_at DESC'''
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route('/api/admin/users/<int:user_id>/role', methods=['PUT'])
@require_admin
def admin_set_role(user_id):
    data = request.get_json(silent=True) or {}
    role = data.get('role', 'user')
    if role not in ('user', 'admin'):
        return jsonify({'error': 'Geçersiz rol'}), 400
    if user_id == session['user_id']:
        return jsonify({'error': 'Kendi rolünü değiştiremezsin'}), 400
    conn = get_db()
    conn.execute('UPDATE users SET role = ? WHERE id = ?', (role, user_id))
    conn.commit()
    conn.close()
    return jsonify({'success': True})


@app.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
@require_admin
def admin_delete_user(user_id):
    if user_id == session['user_id']:
        return jsonify({'error': 'Kendini silemezsin'}), 400
    conn = get_db()
    conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})


@app.route('/api/admin/reviews', methods=['GET'])
@require_admin
def admin_get_reviews():
    conn = get_db()
    rows = conn.execute(
        '''SELECT r.id, r.city_name, r.reviewer_name, r.rating, r.text, r.created_at,
                  u.username, COUNT(l.id) AS like_count
           FROM reviews r
           LEFT JOIN users u ON r.user_id = u.id
           LEFT JOIN review_likes l ON l.review_id = r.id
           GROUP BY r.id ORDER BY r.created_at DESC'''
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route('/api/admin/reviews/<int:review_id>', methods=['DELETE'])
@require_admin
def admin_delete_review(review_id):
    conn = get_db()
    conn.execute('DELETE FROM reviews WHERE id = ?', (review_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})


@app.route('/api/admin/stats', methods=['GET'])
@require_admin
def admin_stats():
    conn = get_db()
    data = {
        'users':     conn.execute('SELECT COUNT(*) FROM users').fetchone()[0],
        'reviews':   conn.execute('SELECT COUNT(*) FROM reviews').fetchone()[0],
        'favorites': conn.execute('SELECT COUNT(*) FROM favorites').fetchone()[0],
        'photos':    conn.execute('SELECT COUNT(*) FROM photos').fetchone()[0],
        'trips':     conn.execute('SELECT COUNT(*) FROM trips').fetchone()[0],
        'top_cities': [dict(r) for r in conn.execute(
            '''SELECT c.name, cv.view_count,
                      COUNT(DISTINCT r.id) AS reviews,
                      COUNT(DISTINCT f.id) AS favorites
               FROM cities c
               LEFT JOIN city_views cv ON cv.city_id = c.id
               LEFT JOIN reviews    r  ON r.city_id  = c.id
               LEFT JOIN favorites  f  ON f.city_id  = c.id
               GROUP BY c.id ORDER BY cv.view_count DESC LIMIT 5'''
        ).fetchall()],
    }
    conn.close()
    return jsonify(data)


@app.route('/admin')
def admin_page():
    return send_from_directory('.', 'admin.html')


# ── İstatistikler ──────────────────────────────────────────────────────────
@app.route('/api/stats', methods=['GET'])
def get_stats():
    conn = get_db()
    city_count   = conn.execute('SELECT COUNT(*) FROM cities').fetchone()[0]
    place_count  = conn.execute('SELECT COUNT(*) FROM places').fetchone()[0]
    review_count = conn.execute('SELECT COUNT(*) FROM reviews').fetchone()[0]
    avg_rating   = conn.execute('SELECT ROUND(AVG(rating),1) FROM reviews').fetchone()[0]
    conn.close()
    return jsonify({
        'cities':  city_count,
        'places':  place_count,
        'reviews': review_count,
        'avg_rating': avg_rating or 0,
    })


init_db()

if __name__ == '__main__':
    print('✓ Veritabanı hazır:', DB_PATH)
    print('✓ Sunucu başlatılıyor → http://localhost:5000')
    app.run(debug=False, port=5000)
