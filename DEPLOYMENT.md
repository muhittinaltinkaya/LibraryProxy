# LibProxy Production Deployment Guide

Bu rehber, LibProxy uygulamasını **80.251.40.216** IP adresindeki production sunucusuna kurulum için hazırlanmıştır.

## 📋 Gereksinimler

- Ubuntu 20.04+ veya benzer Linux dağıtımı
- En az 4GB RAM
- En az 20GB disk alanı
- Root veya sudo yetkisi

## 🚀 Hızlı Kurulum

### 1. Sunucu Hazırlığı

```bash
# Sunucuya bağlanın
ssh user@80.251.40.216

# Proje dosyalarını sunucuya kopyalayın (local makinenizden)
scp -r LibProxy/ user@80.251.40.216:/tmp/

# Sunucuda proje dizinine geçin
sudo mv /tmp/LibProxy /opt/libproxy
sudo chown -R $USER:$USER /opt/libproxy
cd /opt/libproxy
```

### 2. Sunucu Kurulumu

```bash
# Sunucu setup scriptini çalıştırın
./server-setup.sh
```

Bu script şunları yapacak:
- Docker ve Docker Compose kurulumu
- Firewall yapılandırması
- Güvenlik ayarları (fail2ban)
- Log rotation
- Backup sistemi
- Monitoring araçları

### 3. Güvenlik Yapılandırması

```bash
# env.production dosyasını düzenleyin
nano env.production
```

**ÖNEMLİ**: Aşağıdaki değerleri değiştirin:
```bash
# Güçlü şifreler oluşturun
POSTGRES_PASSWORD=your-strong-database-password-2024
JWT_SECRET_KEY=your-very-strong-jwt-secret-key-2024
SECRET_KEY=your-very-strong-secret-key-2024
```

### 4. Uygulamayı Başlatın

```bash
# Birleştirilmiş deployment scripti (önerilen)
./scripts/deployment.sh deploy

# Veya eski yöntem
./deploy.sh
```

### 5. Sorun Giderme

**Tüm sorunları çözmek için:**
```bash
# Detaylı debug
./scripts/deployment.sh debug

# Admin sorunlarını çöz
./scripts/deployment.sh admin

# Frontend'i yeniden build et
./scripts/deployment.sh frontend

# Servis durumlarını kontrol et
./scripts/deployment.sh status

# Logları izle
./scripts/deployment.sh logs
```

**Manuel admin yönetimi:**
```bash
# Admin kullanıcısı oluştur/güncelle
docker-compose -f docker-compose.prod.yml exec -T backend python /app/scripts/admin_tools.py create

# Admin kullanıcısını zorla oluştur
docker-compose -f docker-compose.prod.yml exec -T backend python /app/scripts/admin_tools.py force

# Veritabanı durumunu kontrol et
docker-compose -f docker-compose.prod.yml exec -T backend python /app/scripts/admin_tools.py check
```

## 🌐 Erişim URL'leri

Deployment tamamlandıktan sonra:

- **Frontend**: http://80.251.40.216:3000
- **Backend API**: http://80.251.40.216:5001/api
- **HAProxy Stats**: http://80.251.40.216:8404/stats
- **Journal Proxy**: http://80.251.40.216

## 🔧 Yönetim Komutları

```bash
# Servisleri görüntüle
docker-compose -f docker-compose.prod.yml ps

# Logları görüntüle
docker-compose -f docker-compose.prod.yml logs -f

# Servisleri yeniden başlat
docker-compose -f docker-compose.prod.yml restart

# Servisleri durdur
docker-compose -f docker-compose.prod.yml down

# Veritabanı backup
/opt/libproxy-backups/backup.sh
```

## 📊 İzleme ve Monitoring

### Sistem Monitoring
```bash
# Sistem kaynaklarını izle
htop
iotop
nethogs

# Disk kullanımı
df -h

# Docker container durumu
docker stats
```

### Log Monitoring
```bash
# Uygulama logları
tail -f /var/log/libproxy/*.log

# Docker logları
docker-compose -f docker-compose.prod.yml logs -f

# Sistem logları
tail -f /var/log/syslog
```

## 🔒 Güvenlik Önlemleri

### 1. SSL/HTTPS Kurulumu (Önerilen)

```bash
# Let's Encrypt ile SSL sertifikası
sudo apt install certbot
sudo certbot --nginx -d 80.251.40.216
```

### 2. Firewall Kontrolü

```bash
# Firewall durumu
sudo ufw status

# Sadece gerekli portları açık tutun
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw allow 3000  # Frontend
sudo ufw allow 5001  # Backend API
sudo ufw allow 8404  # HAProxy Stats
```

### 3. Fail2ban Kontrolü

```bash
# Fail2ban durumu
sudo fail2ban-client status
sudo fail2ban-client status sshd
```

## 💾 Backup ve Restore

### Otomatik Backup
- Günlük backup: Her gün 02:00'da otomatik çalışır
- Backup lokasyonu: `/opt/libproxy-backups/`
- 7 günlük backup saklanır

### Manuel Backup
```bash
# Veritabanı backup
/opt/libproxy-backups/backup.sh

# Tüm uygulama backup
tar -czf libproxy-full-backup-$(date +%Y%m%d).tar.gz /opt/libproxy/
```

### Restore İşlemi
```bash
# Veritabanı restore
gunzip -c backup_file.sql.gz | docker-compose -f docker-compose.prod.yml exec -T db psql -U libproxy_user libproxy
```

## 🔧 Sorun Giderme

### Yaygın Sorunlar

1. **Servisler başlamıyor**
   ```bash
   # Logları kontrol edin
   docker-compose -f docker-compose.prod.yml logs
   
   # Port kullanımını kontrol edin
   sudo netstat -tulpn
   ```

2. **Veritabanı bağlantı sorunu**
   ```bash
   # PostgreSQL container durumu
   docker-compose -f docker-compose.prod.yml exec db psql -U libproxy_user -d libproxy -c "SELECT 1;"
   ```

3. **CORS hataları**
   ```bash
   # env.production dosyasında CORS_ORIGINS ayarını kontrol edin
   nano env.production
   ```

### Log Dosyaları

- Uygulama logları: `/var/log/libproxy/`
- Docker logları: `docker-compose logs`
- Sistem logları: `/var/log/syslog`
- Backup logları: `/var/log/libproxy/backup.log`

## 📈 Performance Optimizasyonu

### 1. PostgreSQL Optimizasyonu
```sql
-- PostgreSQL ayarlarını optimize edin
-- /var/lib/docker/volumes/postgres_data/_data/postgresql.conf
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
```

### 2. HAProxy Optimizasyonu
- `maxconn` değerini sunucu kapasitesine göre ayarlayın
- Health check sürelerini optimize edin

### 3. Docker Resource Limits
```yaml
# docker-compose.prod.yml içinde resource limits ekleyin
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 2G
    reservations:
      cpus: '0.5'
      memory: 512M
```

## 🆙 Güncelleme İşlemi

```bash
# Yeni kodu çekin
git pull origin main

# Production build
./deploy.sh

# Veritabanı migration (gerekirse)
docker-compose -f docker-compose.prod.yml exec backend flask db upgrade
```

## 📞 Destek

Sorun yaşadığınızda:

1. Logları kontrol edin
2. Servis durumlarını kontrol edin
3. Firewall ayarlarını kontrol edin
4. Backup'lardan restore yapın (gerekirse)

## ✅ Deployment Checklist

- [ ] Sunucu kurulumu tamamlandı
- [ ] Güvenlik ayarları yapıldı
- [ ] Güçlü şifreler ayarlandı
- [ ] Firewall yapılandırıldı
- [ ] SSL sertifikası kuruldu (opsiyonel)
- [ ] Backup sistemi test edildi
- [ ] Monitoring araçları kuruldu
- [ ] Uygulama test edildi
- [ ] Performans optimizasyonu yapıldı
- [ ] Dokümantasyon okundu

🎉 **Deployment başarıyla tamamlandı!**
