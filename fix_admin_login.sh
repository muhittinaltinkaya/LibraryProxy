#!/bin/bash

# Admin giriş sorunu çözme scripti
# Production sunucusunda admin kullanıcısı sorunlarını çözer

echo "🔧 Admin giriş sorunu çözülüyor..."

# Docker container'ların çalışıp çalışmadığını kontrol et
echo "📋 Container durumları:"
docker-compose -f docker-compose.prod.yml ps

echo ""
echo "🔍 Veritabanı durumu kontrol ediliyor..."

# Veritabanı kontrol scriptini çalıştır
echo "1️⃣ Veritabanı bağlantısı ve kullanıcılar kontrol ediliyor..."
docker-compose -f docker-compose.prod.yml exec -T backend python /app/check_database.py

echo ""
echo "2️⃣ Admin kullanıcısının şifre hash'i güncelleniyor..."

# Admin hash güncelleme scriptini çalıştır
docker-compose -f docker-compose.prod.yml exec -T backend python /app/update_admin_hash.py

echo ""
echo "2️⃣b Admin kullanıcısı oluşturuluyor/güncelleniyor..."

# Admin kullanıcısı oluşturma scriptini çalıştır
docker-compose -f docker-compose.prod.yml exec -T backend python /app/create_admin_user.py

echo ""
echo "3️⃣ Veritabanı migration kontrol ediliyor..."

# Migration'ları çalıştır
docker-compose -f docker-compose.prod.yml exec -T backend flask db upgrade

echo ""
echo "4️⃣ Final kontrol yapılıyor..."

# Son kontrol
docker-compose -f docker-compose.prod.yml exec -T backend python /app/check_database.py

echo ""
echo "5️⃣ Backend servisini yeniden başlatıyor..."

# Backend'i yeniden başlat
docker-compose -f docker-compose.prod.yml restart backend

echo ""
echo "⏳ Servisin başlaması için bekleniyor..."
sleep 10

echo ""
echo "✅ İşlem tamamlandı!"
echo ""
echo "🔗 Giriş bilgileri:"
echo "   URL: http://80.251.40.216:3000/login"
echo "   Kullanıcı adı: admin"
echo "   Şifre: admin123"
echo ""
echo "🧪 Test etmek için:"
echo "   1. Frontend'e gidin: http://80.251.40.216:3000/login"
echo "   2. admin / admin123 ile giriş yapın"
echo ""
echo "📊 Logları kontrol etmek için:"
echo "   docker-compose -f docker-compose.prod.yml logs backend"
echo ""

# Backend loglarını göster
echo "📋 Son backend logları:"
docker-compose -f docker-compose.prod.yml logs --tail=20 backend
