#!/bin/bash

# Hızlı frontend API URL düzeltme scripti
# Mevcut container'da config dosyasını günceller

echo "🔧 Frontend API URL hızlı düzeltme..."

# Config dosyasını güncelle
echo "1️⃣ Config dosyası güncelleniyor..."
cat > frontend/public/config.js << 'EOF'
// Runtime configuration for production
window.APP_CONFIG = {
  API_URL: 'http://80.251.40.216:5001/api'
};
EOF

# Frontend container'ına config dosyasını kopyala
echo "2️⃣ Config dosyası container'a kopyalanıyor..."
docker cp frontend/public/config.js $(docker-compose -f docker-compose.prod.yml ps -q frontend):/app/public/config.js

# Frontend container'ını yeniden başlat
echo "3️⃣ Frontend container'ı yeniden başlatılıyor..."
docker-compose -f docker-compose.prod.yml restart frontend

# Container'ın başlamasını bekle
echo "4️⃣ Container'ın başlaması bekleniyor..."
sleep 10

# Frontend container durumunu kontrol et
echo "5️⃣ Frontend container durumu:"
docker-compose -f docker-compose.prod.yml ps frontend

echo ""
echo "✅ Hızlı düzeltme tamamlandı!"
echo ""
echo "🔗 Test etmek için:"
echo "   Frontend: http://80.251.40.216:3000"
echo "   Tarayıcı konsolunda Network sekmesini kontrol edin"
echo "   API istekleri artık 80.251.40.216:5001'e gitmeli"
echo ""
