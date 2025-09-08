# LibProxy - Dinamik Proxy Sistemiyle Elektronik Dergi Erişimi

Bu proje, OpenAthens benzeri bir sistemin temel bileşenlerini oluşturmaya odaklanmaktadır: kullanıcı kimlik doğrulama, dinamik proxy yönetimi ve elektronik kaynaklara erişim.

## 🚀 Özellikler

### Kullanıcı Yönetimi
- ✅ Kullanıcı kaydı ve girişi
- ✅ JWT tabanlı kimlik doğrulama
- ✅ Admin paneli ile kullanıcı yönetimi
- ✅ Kullanıcı şifre güncelleme (admin)
- ✅ Kullanıcı aktif/pasif durumu yönetimi

### Dergi Yönetimi
- ✅ Dergi ekleme, düzenleme ve silme
- ✅ Dergi kategorileri ve konu alanları
- ✅ Erişim seviyeleri (public, restricted, admin)
- ✅ Proxy yolu yapılandırması

### Proxy Sistemi
- ✅ HAProxy ile dinamik proxy yönetimi
- ✅ Dış dergi sitelerine proxy erişimi
- ✅ SSL/HTTPS desteği
- ✅ Path-based routing

### Admin Paneli
- ✅ Kullanıcı yönetimi
- ✅ Dergi yönetimi
- ✅ Erişim logları
- ✅ Sistem istatistikleri

## 🏗️ Sistem Mimarisi

### Ana Bileşenler
1. **Kimlik Doğrulama Katmanı** - Kullanıcı girişi ve yetkilendirme
2. **Dinamik Proxy Yönetim Katmanı** - HAProxy ile dinamik proxy oluşturma
3. **Veri Tabanı** - Kullanıcı, dergi ve erişim logları
4. **Admin Paneli** - Sistem yönetimi

### Teknoloji Stack
- **Backend**: Python Flask + SQLAlchemy
- **Frontend**: React.js + TypeScript
- **Database**: PostgreSQL
- **Cache**: Redis
- **Proxy**: HAProxy
- **Authentication**: JWT tokens
- **Containerization**: Docker & Docker Compose

## 📁 Proje Yapısı

```
LibProxy/
├── backend/                 # Flask API backend
│   ├── app/
│   │   ├── models/         # Veritabanı modelleri
│   │   ├── routes/         # API endpointleri
│   │   ├── services/       # İş mantığı servisleri
│   │   └── utils/          # Yardımcı fonksiyonlar
│   ├── config/             # Yapılandırma dosyaları
│   └── requirements.txt    # Python bağımlılıkları
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React bileşenleri
│   │   ├── pages/          # Sayfa bileşenleri
│   │   ├── services/       # API servisleri
│   │   └── utils/          # Yardımcı fonksiyonlar
│   └── package.json
├── database/               # Veritabanı yapılandırması
├── proxy/                  # HAProxy yapılandırması
├── docker-compose.yml      # Container orchestration
└── README.md
```

## 🚀 Kurulum ve Çalıştırma

### Gereksinimler
- Docker ve Docker Compose
- Node.js 18+ (geliştirme için)
- Python 3.9+ (geliştirme için)

### Hızlı Başlangıç

1. **Projeyi klonlayın:**
```bash
git clone <repository-url>
cd LibProxy
```

2. **Environment dosyasını oluşturun:**
```bash
cp env.example .env
```

3. **Tüm servisleri başlatın:**
```bash
docker-compose up -d
```

4. **Veritabanı migrasyonlarını çalıştırın:**
```bash
docker-compose exec backend flask db upgrade
```

5. **Uygulamaya erişin:**
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5001/api
- **Proxy**: http://localhost:80

### Varsayılan Admin Hesabı
- **Kullanıcı adı**: `admin`
- **Şifre**: `admin123`

## 🌐 Erişim URL'leri

### Frontend
- **Ana Sayfa**: http://localhost:3000
- **Giriş**: http://localhost:3000/login
- **Kayıt**: http://localhost:3000/register
- **Admin Paneli**: http://localhost:3000/admin

### Backend API
- **API Base URL**: http://localhost:5001/api
- **Health Check**: http://localhost:5001/api/health

### Proxy Erişimi
- **Nature**: http://localhost/nature
- **Science**: http://localhost/science
- **Lancet**: http://localhost/lancet
- **JAMA**: http://localhost/jama

## 📚 API Dokümantasyonu

### Kimlik Doğrulama
- `POST /api/auth/login` - Kullanıcı girişi
- `POST /api/auth/register` - Kullanıcı kaydı
- `POST /api/auth/logout` - Oturum kapatma
- `GET /api/auth/profile` - Kullanıcı profili
- `PUT /api/auth/profile` - Profil güncelleme

### Dergi Yönetimi
- `GET /api/journals` - Dergi listesi
- `GET /api/journals/{id}` - Dergi detayları
- `GET /api/journals/subject-areas` - Konu alanları

### Admin API
- `GET /api/admin/users` - Kullanıcı listesi
- `POST /api/admin/users` - Kullanıcı oluşturma
- `PUT /api/admin/users/{id}` - Kullanıcı güncelleme
- `PUT /api/admin/users/{id}/password` - Şifre güncelleme
- `GET /api/admin/journals` - Dergi listesi (admin)
- `POST /api/admin/journals` - Dergi oluşturma
- `PUT /api/admin/journals/{id}` - Dergi güncelleme
- `GET /api/admin/stats` - Sistem istatistikleri
- `GET /api/admin/access-logs` - Erişim logları

## 🔒 Güvenlik

- JWT tabanlı kimlik doğrulama
- Şifre hash'leme (bcrypt)
- CORS yapılandırması
- Rate limiting
- XSS ve CSRF koruması
- Admin yetkilendirme

## 🛠️ Geliştirme

### Backend Geliştirme
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
flask run
```

### Frontend Geliştirme
```bash
cd frontend
npm install
npm start
```

### Veritabanı Yönetimi
```bash
# Migration oluşturma
docker-compose exec backend flask db migrate -m "Migration message"

# Migration uygulama
docker-compose exec backend flask db upgrade

# Veritabanı shell
docker-compose exec db psql -U libproxy_user -d libproxy
```

## 🐳 Docker Servisleri

- **frontend**: React uygulaması (port 3000)
- **backend**: Flask API (port 5001)
- **db**: PostgreSQL veritabanı (port 5432)
- **redis**: Cache ve session (port 6379)
- **haproxy**: Proxy sunucusu (port 80)

## 📝 Kullanım

1. **Admin olarak giriş yapın** (admin/admin123)
2. **Kullanıcıları yönetin** - Admin panelinde kullanıcı ekleyin/düzenleyin
3. **Dergileri yönetin** - Dergi ekleyin ve proxy yollarını yapılandırın
4. **Proxy erişimini test edin** - http://localhost/{proxy_path} ile dergi içeriklerine erişin

## 🐛 Sorun Giderme

### Servisleri Yeniden Başlatma
```bash
docker-compose restart
```

### Logları Görüntüleme
```bash
docker-compose logs -f [service_name]
```

### Veritabanını Sıfırlama
```bash
docker-compose down -v
docker-compose up -d
docker-compose exec backend flask db upgrade
```

## 📄 Lisans

MIT License

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit yapın (`git commit -m 'Add amazing feature'`)
4. Push yapın (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun