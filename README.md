# ✈️ Turkey Travel Database

Türkiye'nin şehirlerini keşfetmek için geliştirilmiş tam özellikli bir **seyahat rehberi ve sosyal platform**. Flask tabanlı REST API, kullanıcı kimlik doğrulama, favori şehirler, yorum sistemi ve seyahat planlama özelliklerini bir arada sunar.

---

## 🌟 Özellikler

- 🏙️ **Şehir Rehberi** — Türkiye'nin 10 şehrini bölge ve etiketlerle keşfet
- 📍 **Turistik Yerler** — Şehirlere göre gezilecek mekanlar ve puanları
- ⭐ **Yorum & Puanlama** — 1-5 arası puanlama, beğeni ve yorum sistemi
- ❤️ **Favori Şehirler** — Beğendiğin şehirleri kaydet
- 🗺️ **Seyahat Planı** — Tarih aralıklı seyahat oluştur, duraklar ekle
- 📸 **Fotoğraf Galerisi** — Şehirlere fotoğraf yükle ve görüntüle
- 🔔 **Bildirim Sistemi** — Aktivite bildirimleri
- 🔍 **Arama** — Şehir, mekan ve içeriklerde çoklu alan arama
- 👤 **Profil Yönetimi** — Kullanıcı profili düzenleme
- 🛡️ **Admin Paneli** — Kullanıcı yönetimi, içerik moderasyonu, platform istatistikleri

---

## 🛠️ Teknolojiler

| Katman      | Teknoloji                             |
|-------------|---------------------------------------|
| Backend     | Python 3, Flask, Flask-CORS           |
| Veritabanı  | SQLite                                |
| Güvenlik    | Werkzeug Security (PBKDF2:SHA256), Flask Session |
| Sunucu      | Gunicorn (production)                 |
| Frontend    | HTML / CSS / JavaScript (SPA)         |
| Dosya Yükleme | Werkzeug secure_filename            |

---

## 📁 Proje Yapısı

```
travel-Db-/
├── app.py                        # Flask uygulaması & tüm API endpoint'leri
├── gunicorn.conf.py              # Production sunucu yapılandırması
├── turkey_travel.db              # SQLite veritabanı
├── turkey_travel(12).html        # Ana arayüz (SPA)
├── login.html                    # Giriş & kayıt sayfası
├── admin.html                    # Admin paneli
├── database_design_document.html # Veritabanı şeması dokümantasyonu
├── fotograflar/                  # Fotoğraf klasörü
└── .gitignore
```

---

## ⚙️ Kurulum & Çalıştırma

### 1. Bağımlılıkları Yükle

```bash
pip install flask flask-cors werkzeug
```

### 2. Geliştirme Sunucusu

```bash
python app.py
```

### 3. Production (Gunicorn)

```bash
gunicorn -c gunicorn.conf.py app:app
```

### 4. Tarayıcıda Aç

```
http://localhost:5000
```

---

## 🗄️ Veritabanı Şeması

```
cities ──────────────────────────────────────────┐
  id, name, region, description, tags             │
                                                   │
users ──────┬──────────────────────────────────────┤
  id, username, email, password, role, bio        │
  location, avatar_color, created_at              │
            │                                      │
            ├── favorites (M:N) ──────────────── cities
            │     user_id, city_id, created_at
            │
            ├── reviews ────────────────────── cities
            │     id, user_id, city_id
            │     rating (1-5), text, created_at
            │         └── review_likes (M:N)
            │               user_id, review_id
            │
            ├── trips
            │     id, user_id, title
            │     start_date, end_date, created_at
            │         └── trip_stops ──────── cities
            │               trip_id, city_id
            │               stop_order, notes
            │
            ├── photos ─────────────────────── cities
            │     id, user_id, city_id
            │     file_path, caption, created_at
            │
            └── notifications
                  user_id, message, link
                  is_read, created_at

places ─────────────────────────────────────── cities
  id, name, city_id, category, rating
  description, icon, img_key

city_views ─────────────────────────────────── cities
  city_id, view_count
```

---

## 📡 API Endpoint'leri

### 🔐 Kimlik Doğrulama
| Method | Endpoint             | Açıklama              |
|--------|----------------------|-----------------------|
| POST   | `/api/auth/register` | Hesap oluştur         |
| POST   | `/api/auth/login`    | Giriş yap             |
| POST   | `/api/auth/logout`   | Çıkış yap             |
| GET    | `/api/auth/me`       | Mevcut kullanıcı bilgisi |

### 🏙️ Şehirler & Mekanlar
| Method | Endpoint                    | Açıklama                  |
|--------|-----------------------------|---------------------------|
| GET    | `/api/cities`               | Tüm şehirler              |
| GET    | `/api/cities/<name>`        | Şehir detayı              |
| POST   | `/api/cities/<name>/view`   | Görüntülenme sayacı       |
| GET    | `/api/places`               | Turistik yerler           |
| GET    | `/api/search`               | Çoklu alan arama          |

### ⭐ Yorumlar & Beğeniler
| Method | Endpoint                    | Açıklama                  |
|--------|-----------------------------|---------------------------|
| GET    | `/api/reviews/<city>`       | Şehir yorumları           |
| POST   | `/api/reviews/<city>`       | Yorum ekle (giriş gerekli) |
| PUT    | `/api/reviews/<id>`         | Yorum düzenle             |
| DELETE | `/api/reviews/<id>`         | Yorum sil                 |

### ❤️ Favoriler & Profil
| Method | Endpoint                    | Açıklama                  |
|--------|-----------------------------|---------------------------|
| GET    | `/api/favorites`            | Favori şehirler           |
| POST   | `/api/favorites/<city>`     | Favori ekle/kaldır        |
| GET    | `/api/profile`              | Profil bilgisi            |
| PUT    | `/api/profile`              | Profil güncelle           |

### 🗺️ Seyahat Planları
| Method | Endpoint                        | Açıklama              |
|--------|---------------------------------|-----------------------|
| GET    | `/api/trips`                    | Seyahat planları      |
| POST   | `/api/trips`                    | Plan oluştur          |
| POST   | `/api/trips/<id>/stops`         | Durak ekle            |
| DELETE | `/api/trips/<id>/stops/<stop>`  | Durak sil             |

### 📸 Fotoğraflar
| Method | Endpoint                | Açıklama              |
|--------|-------------------------|-----------------------|
| GET    | `/api/photos/<city>`    | Şehir galerisi        |
| POST   | `/api/photos`           | Fotoğraf yükle        |
| DELETE | `/api/photos/<id>`      | Fotoğraf sil          |

### 🛡️ Admin
| Method | Endpoint                        | Açıklama              |
|--------|---------------------------------|-----------------------|
| GET    | `/api/admin/users`              | Kullanıcı listesi     |
| PUT    | `/api/admin/users/<id>/role`    | Rol değiştir          |
| DELETE | `/api/admin/users/<id>`         | Kullanıcı sil         |
| GET    | `/api/admin/reviews`            | Tüm yorumlar          |
| DELETE | `/api/admin/reviews/<id>`       | Yorum sil             |
| GET    | `/api/admin/stats`              | Platform istatistikleri |

---

## 🏙️ Desteklenen Şehirler

| Şehir       | Bölge        |
|-------------|--------------|
| İstanbul    | Marmara      |
| Ankara      | İç Anadolu   |
| İzmir       | Ege          |
| Antalya     | Akdeniz      |
| Kapadokya   | İç Anadolu   |
| Trabzon     | Karadeniz    |
| Efes        | Ege          |
| Pamukkale   | Ege          |
| Bodrum      | Ege          |
| Mardin      | Güneydoğu    |

---

## 📝 Lisans

MIT License — özgürce kullanabilirsiniz.
