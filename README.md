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
