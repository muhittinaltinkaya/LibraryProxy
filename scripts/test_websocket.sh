#!/bin/bash

# WebSocket test scripti
# Frontend WebSocket bağlantılarını test eder

echo "🧪 WebSocket test scripti başlatılıyor..."

# Frontend container environment variables
echo "1️⃣ Frontend environment variables:"
docker-compose -f docker-compose.prod.yml exec frontend env | grep -E "(WDS|REACT)"

echo ""
echo "2️⃣ Frontend container durumu:"
docker-compose -f docker-compose.prod.yml ps frontend

echo ""
echo "3️⃣ Frontend erişilebilirlik testi:"
curl -I http://localhost:3000 2>/dev/null | head -1 || echo "   ❌ Frontend erişilemiyor"

echo ""
echo "4️⃣ Frontend logları (WebSocket ile ilgili):"
docker-compose -f docker-compose.prod.yml logs --tail=20 frontend | grep -E "(webpack|socket|ws|WebSocket|compiled|started)" || echo "   ℹ️  WebSocket log bulunamadı"

echo ""
echo "5️⃣ React development server durumu:"
docker-compose -f docker-compose.prod.yml exec frontend ps aux | grep -E "(node|npm)" || echo "   ❌ React server bulunamadı"

echo ""
echo "6️⃣ Port 3000 dinleme durumu:"
docker-compose -f docker-compose.prod.yml exec frontend netstat -tlnp | grep :3000 || echo "   ❌ Port 3000 dinlenmiyor"

echo ""
echo "✅ Test tamamlandı!"
echo ""
echo "🔗 Test etmek için:"
echo "   1. Tarayıcıda http://80.251.40.216:3000 adresine gidin"
echo "   2. Firefox Developer Tools'u açın (F12)"
echo "   3. Console sekmesini kontrol edin"
echo "   4. WebSocket bağlantı hatalarını kontrol edin"
echo ""
echo "📝 WebSocket hataları genellikle:"
echo "   - Hot reload için kullanılır"
echo "   - Production'da gerekli değildir"
echo "   - Uygulama çalışmasını etkilemez"
echo ""
