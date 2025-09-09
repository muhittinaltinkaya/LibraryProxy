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
- ✅ Dergi ekleme, düzenleme ve silme (tam fonksiyonel)
- ✅ Dergi kategorileri ve konu alanları
- ✅ Erişim seviyeleri (public, restricted, admin)
- ✅ Proxy yolu yapılandırması
- ✅ ISSN/E-ISSN yönetimi
- ✅ Yayıncı bilgileri
- ✅ Timeout ve auth method ayarları

### Dinamik Proxy Sistemi
- ✅ HAProxy ile tamamen dinamik proxy yönetimi
- ✅ Otomatik HAProxy konfigürasyonu güncellemesi
- ✅ Yeni dergi eklendiğinde anında erişim
- ✅ Path rewriting ve CORS desteği
- ✅ Dış dergi sitelerine seamless proxy erişimi
- ✅ SSL/HTTPS desteği
- ✅ Health check ve failover

### Admin Paneli
- ✅ Kullanıcı yönetimi (ekleme, düzenleme, şifre güncelleme)
- ✅ Dergi yönetimi (tüm alanları düzenlenebilir)
- ✅ Erişim logları ve analytics
- ✅ Sistem istatistikleri ve dashboard
- ✅ Real-time proxy konfigürasyonu yönetimi

## 🏗️ Sistem Mimarisi

### Ana Bileşenler
1. **Kimlik Doğrulama Katmanı** - JWT tabanlı kullanıcı girişi ve yetkilendirme
2. **Dinamik Proxy Yönetim Katmanı** - HAProxy ile otomatik proxy konfigürasyonu
3. **Veri Tabanı** - Kullanıcı, dergi ve erişim logları (PostgreSQL)
4. **Cache Katmanı** - Redis ile session ve rate limiting
5. **Admin Paneli** - React tabanlı sistem yönetimi arayüzü
6. **Analytics Sistemi** - Erişim logları ve kullanım istatistikleri

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

### Hızlı Başlangıç (Development)

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

### 🌐 Production Deployment

Production sunucusuna (80.251.40.216) kurulum için:

1. **Deployment dosyalarını hazırlayın:**
```bash
# Production environment dosyasını düzenleyin
cp env.production .env.prod
# Güçlü şifreler ve güvenlik anahtarları ayarlayın
```

2. **Sunucu kurulumu:**
```bash
# Sunucuda çalıştırın
./server-setup.sh
```

3. **Production deployment:**
```bash
# Birleştirilmiş deployment scripti
./scripts/deployment.sh deploy

# Veya eski yöntem
./deploy.sh
```

4. **Production erişim:**
- **Frontend**: http://80.251.40.216:3000
- **Backend API**: http://80.251.40.216:5001/api
- **HAProxy Stats**: http://80.251.40.216:8404/stats
- **Proxy**: http://80.251.40.216

**Detaylı kurulum rehberi**: [DEPLOYMENT.md](./DEPLOYMENT.md)

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
Sistemde kayıtlı olan tüm aktif dergiler dinamik olarak proxy üzerinden erişilebilir:
- **Format**: http://localhost/{proxy_path}
- **Örnekler**:
  - **Nature**: http://localhost/nature
  - **Science**: http://localhost/science
  - **Lancet**: http://localhost/lancet
  - **JAMA**: http://localhost/jama
  - **DSpace**: http://localhost/dspace

**Not**: Yeni dergi eklendiğinde otomatik olarak proxy konfigürasyonu oluşturulur ve anında erişim sağlanır.

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
- `PUT /api/admin/journals/{id}` - Dergi güncelleme (tüm alanlar)
- `DELETE /api/admin/journals/{id}` - Dergi silme
- `GET /api/admin/stats` - Sistem istatistikleri
- `GET /api/admin/access-logs` - Erişim logları

### Proxy API
- `POST /api/proxy/generate` - Proxy konfigürasyonu oluşturma
- `POST /api/proxy/reload` - HAProxy yeniden yükleme
- `DELETE /api/proxy/{id}` - Proxy konfigürasyonu silme
- `GET /api/proxy/status` - Proxy durumu
- `POST /api/proxy/cleanup` - Süresi dolmuş konfigürasyonları temizleme

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

### Temel Kullanım Adımları

1. **Admin olarak giriş yapın** (admin/admin123)
2. **Kullanıcıları yönetin** - Admin panelinde kullanıcı ekleyin/düzenleyin/şifre güncelleyin
3. **Dergileri yönetin** - Dergi ekleyin ve tüm alanları düzenleyin:
   - Dergi adı, slug, publisher bilgileri
   - Base URL ve proxy path
   - ISSN/E-ISSN numaraları
   - Subject areas (konu alanları)
   - Access level ve authentication ayarları
   - Timeout ve diğer proxy ayarları
4. **Proxy erişimini test edin** - http://localhost/{proxy_path} ile dergi içeriklerine anında erişin

### Dinamik Proxy Özelliği

- ✅ Yeni dergi eklediğinizde HAProxy konfigürasyonu otomatik güncellenir
- ✅ Dergi bilgilerini düzenlediğinizde proxy ayarları anında yansır
- ✅ Dergi sildiğinizde proxy erişimi otomatik kaldırılır
- ✅ Manuel HAProxy konfigürasyonu gerektirmez

### Admin Paneli Özellikleri

- **Dashboard**: Sistem istatistikleri ve genel bakış
- **User Management**: Kullanıcı ekleme, düzenleme, aktif/pasif yapma
- **Journal Management**: Dergi yönetimi (tüm alanlar düzenlenebilir)
- **Analytics**: Erişim logları ve kullanım raporları

## 🐛 Sorun Giderme

### Servisleri Yeniden Başlatma
```bash
docker-compose restart
```

### Logları Görüntüleme
```bash
# Tüm servisler
docker-compose logs -f

# Belirli servis
docker-compose logs -f [service_name]

# Örnek: HAProxy logları
docker-compose logs -f haproxy
```

### Veritabanını Sıfırlama
```bash
docker-compose down -v
docker-compose up -d
docker-compose exec backend flask db upgrade
```

### HAProxy Konfigürasyon Sorunları
```bash
# HAProxy konfigürasyonunu manuel yenile
curl -X POST http://localhost:5001/api/proxy/reload

# HAProxy durumunu kontrol et
docker-compose logs haproxy

# HAProxy konfigürasyon dosyasını kontrol et
cat proxy/haproxy-simple.cfg
```

### Yaygın Sorunlar ve Çözümleri

1. **Journal edit etmek işe yaramıyor**
   - ✅ Bu sorun çözüldü! Artık tüm journal alanları düzenlenebilir.

2. **Yeni dergi eklendikten sonra proxy erişimi çalışmıyor**
   - ✅ Bu sorun çözüldü! Dinamik konfigürasyon otomatik çalışır.

3. **CORS hataları**
   - CORS ayarları docker-compose.yml'de yapılandırıldı
   - Frontend ve backend arasında tam uyumluluk sağlandı

## 📄 Lisans

MIT License

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit yapın (`git commit -m 'Add amazing feature'`)
4. Push yapın (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun