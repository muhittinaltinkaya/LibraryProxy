#!/bin/bash

# Dergi proxy URL test scripti
# Frontend'de dergi proxy URL'lerinin doğru oluşturulduğunu test eder

echo "🧪 Dergi proxy URL test scripti başlatılıyor..."

# Frontend container'ındaki JournalDetail.tsx dosyasını kontrol et
echo "1️⃣ Frontend JournalDetail.tsx kontrolü:"
docker-compose -f docker-compose.prod.yml exec frontend grep -A 10 "Generate proxy URL" /app/src/pages/JournalDetail.tsx

echo ""
echo "2️⃣ Frontend config kontrolü:"
docker-compose -f docker-compose.prod.yml exec frontend cat /app/public/config.js

echo ""
echo "3️⃣ Dergi listesi kontrolü:"
curl -s http://localhost:5001/api/journals | jq '.journals[0:3] | .[] | {id, name, proxy_path}'

echo ""
echo "4️⃣ Örnek proxy URL'ler:"
echo "   Eski format: http://localhost:80/nature"
echo "   Yeni format: http://80.251.40.216/nature"

echo ""
echo "5️⃣ Frontend container'ında test:"
docker-compose -f docker-compose.prod.yml exec frontend node -e "
const config = { API_URL: 'http://80.251.40.216:5001/api' };
const baseUrl = config.API_URL?.replace('/api', '').replace(':5001', '') || 'http://80.251.40.216';
const proxyPath = 'nature';
const proxyUrl = \`\${baseUrl}/\${proxyPath}\`;
console.log('Generated proxy URL:', proxyUrl);
"

echo ""
echo "6️⃣ HAProxy proxy testi:"
echo "   Test URL: http://80.251.40.216/nature"
curl -I http://80.251.40.216/nature 2>/dev/null | head -1 || echo "   ❌ HAProxy proxy erişilemiyor"

echo ""
echo "✅ Test tamamlandı!"
echo ""
echo "🔗 Test etmek için:"
echo "   1. Frontend'e gidin: http://80.251.40.216:3000"
echo "   2. Bir dergiye tıklayın"
echo "   3. 'View Journal Content' butonuna basın"
echo "   4. Yeni sekmede http://80.251.40.216/[proxy_path] açılmalı"
echo ""
