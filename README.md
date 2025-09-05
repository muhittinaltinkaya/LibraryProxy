# LibProxy - Dinamik Proxy Sistemiyle Elektronik Dergi Erişimi

Bu proje, OpenAthens benzeri bir sistemin temel bileşenlerini oluşturmaya odaklanmaktadır: kullanıcı kimlik doğrulama, dinamik proxy yönetimi ve elektronik kaynaklara erişim.

## Sistem Mimarisi

### Ana Bileşenler
1. **Kimlik Doğrulama Katmanı** - Kullanıcı girişi ve yetkilendirme
2. **Dinamik Proxy Yönetim Katmanı** - HAProxy/Nginx ile dinamik proxy oluşturma
3. **Veri Tabanı** - Kullanıcı, dergi ve erişim logları

### Teknoloji Stack
- **Backend**: Python Flask + SQLAlchemy
- **Frontend**: React.js + TypeScript
- **Database**: PostgreSQL
- **Proxy**: HAProxy (Runtime API ile dinamik yapılandırma)
- **Authentication**: JWT tokens
- **Containerization**: Docker

## Proje Yapısı

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

## Kurulum ve Çalıştırma

### Gereksinimler
- Docker ve Docker Compose
- Node.js 18+ (geliştirme için)
- Python 3.9+ (geliştirme için)

### Hızlı Başlangıç
```bash
# Tüm servisleri başlat
docker-compose up -d

# Veritabanı migrasyonları
docker-compose exec backend flask db upgrade

# Frontend geliştirme sunucusu
cd frontend && npm start
```

## API Dokümantasyonu

### Kimlik Doğrulama
- `POST /api/auth/login` - Kullanıcı girişi
- `POST /api/auth/logout` - Oturum kapatma
- `GET /api/auth/profile` - Kullanıcı profili

### Dergi Yönetimi
- `GET /api/journals` - Dergi listesi
- `GET /api/journals/{id}` - Dergi detayları
- `POST /api/journals/{id}/access` - Dergi erişim talebi

### Proxy Yönetimi
- `POST /api/proxy/generate` - Dinamik proxy kuralı oluştur
- `DELETE /api/proxy/{id}` - Proxy kuralını sil
- `GET /api/proxy/status` - Proxy durumu

## Güvenlik

- JWT tabanlı kimlik doğrulama
- Şifre hash'leme (bcrypt)
- CORS yapılandırması
- Rate limiting
- XSS ve CSRF koruması

## Geliştirme

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

## Lisans

MIT License
