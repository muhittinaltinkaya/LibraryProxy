#!/bin/bash

# Frontend yeniden build scripti
# Production sunucusunda frontend'i doğru API URL ile yeniden build eder

echo "🔄 Frontend yeniden build ediliyor..."

# Frontend container'ını durdur
echo "1️⃣ Frontend container'ı durduruluyor..."
docker-compose -f docker-compose.prod.yml stop frontend

# Frontend container'ını kaldır
echo "2️⃣ Frontend container'ı kaldırılıyor..."
docker-compose -f docker-compose.prod.yml rm -f frontend

# Frontend image'ını kaldır
echo "3️⃣ Frontend image'ı kaldırılıyor..."
docker rmi libproxy_frontend 2>/dev/null || true

# Config dosyasını güncelle
echo "4️⃣ Config dosyası güncelleniyor..."
cat > frontend/public/config.js << 'EOF'
// Runtime configuration for production
window.APP_CONFIG = {
  API_URL: 'http://80.251.40.216:5001/api'
};
EOF

# Frontend'i yeniden build et ve başlat
echo "5️⃣ Frontend yeniden build ediliyor ve başlatılıyor..."
docker-compose -f docker-compose.prod.yml up --build -d frontend

# Container'ın başlamasını bekle
echo "6️⃣ Container'ın başlaması bekleniyor..."
sleep 15

# Frontend container durumunu kontrol et
echo "7️⃣ Frontend container durumu kontrol ediliyor..."
docker-compose -f docker-compose.prod.yml ps frontend

# Frontend loglarını göster
echo "8️⃣ Frontend logları:"
docker-compose -f docker-compose.prod.yml logs --tail=20 frontend

echo ""
echo "✅ Frontend yeniden build tamamlandı!"
echo ""
echo "🔗 Test etmek için:"
echo "   Frontend: http://80.251.40.216:3000"
echo "   Backend API: http://80.251.40.216:5001/api"
echo ""
echo "🧪 Tarayıcı konsolunda API isteklerini kontrol edin:"
echo "   Network sekmesinde localhost:5001 yerine 80.251.40.216:5001 görmelisiniz"
echo ""
