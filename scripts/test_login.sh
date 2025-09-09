#!/bin/bash

# Login test scripti
# Frontend ve backend arasındaki bağlantıyı test eder

echo "🧪 Login test scripti başlatılıyor..."

# Backend API testi
echo "1️⃣ Backend API testi (localhost):"
curl -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}' \
  -s | jq .message

echo ""
echo "2️⃣ Backend API testi (production IP):"
curl -X POST http://80.251.40.216:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}' \
  -s | jq .message

echo ""
echo "3️⃣ Frontend config kontrolü:"
echo "Host config:"
cat frontend/public/config.js

echo ""
echo "Container config:"
docker-compose -f docker-compose.prod.yml exec frontend cat /usr/share/nginx/html/config.js

echo ""
echo "4️⃣ Servis durumları:"
docker-compose -f docker-compose.prod.yml ps

echo ""
echo "5️⃣ Backend logları (son 10 satır):"
docker-compose -f docker-compose.prod.yml logs --tail=10 backend

echo ""
echo "6️⃣ Frontend logları (son 10 satır):"
docker-compose -f docker-compose.prod.yml logs --tail=10 frontend

echo ""
echo "✅ Test tamamlandı!"
echo ""
echo "🔗 Test etmek için:"
echo "   Frontend: http://80.251.40.216:3000/login"
echo "   Kullanıcı adı: admin"
echo "   Şifre: admin123"
echo ""
echo "📊 Tarayıcı konsolunda Network sekmesini kontrol edin:"
echo "   - API istekleri 80.251.40.216:5001'e gitmeli"
echo "   - 200 OK yanıtı almalısınız"
