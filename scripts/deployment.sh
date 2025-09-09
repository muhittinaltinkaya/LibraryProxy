#!/bin/bash

# LibProxy Deployment Script - Birleştirilmiş deployment scripti
# Production sunucusunda tüm deployment işlemlerini yönetir

set -e  # Hata durumunda scripti durdur

# Renkli output için
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Log fonksiyonu
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Yardım fonksiyonu
show_help() {
    echo "LibProxy Deployment Script"
    echo ""
    echo "Kullanım: $0 <komut>"
    echo ""
    echo "Komutlar:"
    echo "  deploy          - Tam deployment (önerilen)"
    echo "  frontend        - Sadece frontend'i yeniden build et"
    echo "  admin           - Admin kullanıcısı sorunlarını çöz"
    echo "  debug           - Detaylı debug yap"
    echo "  logs            - Logları göster"
    echo "  status          - Servis durumlarını göster"
    echo "  restart         - Tüm servisleri yeniden başlat"
    echo "  stop            - Tüm servisleri durdur"
    echo "  clean           - Gereksiz dosyaları temizle"
    echo "  help            - Bu yardım mesajını göster"
    echo ""
}

# Deployment fonksiyonu
deploy() {
    log "🚀 LibProxy production deployment başlatılıyor..."
    
    # Docker ve Docker Compose kontrolü
    if ! command -v docker &> /dev/null; then
        error "Docker kurulu değil!"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose kurulu değil!"
        exit 1
    fi
    
    # Environment dosyasını kontrol et
    if [ ! -f "env.production" ]; then
        warning "env.production dosyası bulunamadı, env.example'dan kopyalanıyor..."
        cp env.example env.production
    fi
    
    # Mevcut container'ları durdur
    log "🛑 Mevcut container'lar durduruluyor..."
    docker-compose -f docker-compose.prod.yml down || true
    
    # Gereksiz image'ları temizle
    log "🧹 Gereksiz image'lar temizleniyor..."
    docker system prune -f || true
    
    # Servisleri başlat
    log "🔨 Servisler build ediliyor ve başlatılıyor..."
    docker-compose -f docker-compose.prod.yml up --build -d
    
    # Servislerin başlamasını bekle
    log "⏳ Servislerin başlaması bekleniyor..."
    sleep 30
    
    # Servis durumlarını kontrol et
    log "🔍 Servis durumları kontrol ediliyor..."
    docker-compose -f docker-compose.prod.yml ps
    
    # Veritabanı migration'larını çalıştır
    log "📊 Veritabanı migration'ları çalıştırılıyor..."
    docker-compose -f docker-compose.prod.yml exec -T backend flask db upgrade || true
    
    # Admin kullanıcısını oluştur
    log "👤 Admin kullanıcısı oluşturuluyor..."
    docker-compose -f docker-compose.prod.yml exec -T backend python /app/scripts/admin_tools.py create || true
    
    # Final kontrol
    log "✅ Final kontrol yapılıyor..."
    docker-compose -f docker-compose.prod.yml exec -T backend python /app/scripts/admin_tools.py test || true
    
    success "🎉 Deployment tamamlandı!"
    echo ""
    echo "🌐 Erişim URL'leri:"
    echo "   Frontend: http://80.251.40.216:3000"
    echo "   Backend API: http://80.251.40.216:5001/api"
    echo "   HAProxy Stats: http://80.251.40.216:8404/stats"
    echo ""
    echo "🔑 Admin giriş bilgileri:"
    echo "   Kullanıcı adı: admin"
    echo "   Şifre: admin123"
}

# Frontend yeniden build
frontend() {
    log "🔄 Frontend yeniden build ediliyor..."
    
    # Config dosyasını güncelle
    log "📝 Config dosyası güncelleniyor..."
    cat > frontend/public/config.js << 'EOF'
// Runtime configuration for production
window.APP_CONFIG = {
  API_URL: 'http://80.251.40.216:5001/api'
};
EOF
    
    # Frontend container'ını durdur
    log "🛑 Frontend container'ı durduruluyor..."
    docker-compose -f docker-compose.prod.yml stop frontend
    
    # Frontend container'ını kaldır
    log "🗑️  Frontend container'ı kaldırılıyor..."
    docker-compose -f docker-compose.prod.yml rm -f frontend
    
    # Frontend image'ını kaldır
    log "🧹 Frontend image'ı kaldırılıyor..."
    docker rmi libproxy_frontend 2>/dev/null || true
    
    # Frontend'i yeniden build et
    log "🔨 Frontend yeniden build ediliyor..."
    docker-compose -f docker-compose.prod.yml up --build -d frontend
    
    # Container'ın başlamasını bekle
    log "⏳ Container'ın başlaması bekleniyor..."
    sleep 15
    
    # Frontend container durumunu kontrol et
    log "🔍 Frontend container durumu:"
    docker-compose -f docker-compose.prod.yml ps frontend
    
    success "✅ Frontend yeniden build tamamlandı!"
}

# Admin sorunlarını çöz
admin() {
    log "🔧 Admin sorunları çözülüyor..."
    
    # Admin kullanıcısını zorla oluştur
    log "👤 Admin kullanıcısı zorla oluşturuluyor..."
    docker-compose -f docker-compose.prod.yml exec -T backend python /app/scripts/admin_tools.py force
    
    # Backend'i yeniden başlat
    log "🔄 Backend yeniden başlatılıyor..."
    docker-compose -f docker-compose.prod.yml restart backend
    
    # Backend'in başlamasını bekle
    log "⏳ Backend'in başlamasını bekleniyor..."
    sleep 15
    
    # Test et
    log "🧪 Test ediliyor..."
    docker-compose -f docker-compose.prod.yml exec -T backend python /app/scripts/admin_tools.py test
    
    success "✅ Admin sorunları çözüldü!"
}

# Debug yap
debug() {
    log "🔍 Detaylı debug yapılıyor..."
    
    # Servis durumları
    log "📊 Servis durumları:"
    docker-compose -f docker-compose.prod.yml ps
    
    # Backend logları
    log "📋 Backend logları:"
    docker-compose -f docker-compose.prod.yml logs --tail=20 backend
    
    # Veritabanı kontrolü
    log "🗄️  Veritabanı kontrolü:"
    docker-compose -f docker-compose.prod.yml exec -T backend python /app/scripts/admin_tools.py check
    
    # Test login
    log "🧪 Test login:"
    curl -X POST http://80.251.40.216:5001/api/auth/login \
      -H "Content-Type: application/json" \
      -d '{"username": "admin", "password": "admin123"}' \
      -v || true
}

# Logları göster
logs() {
    local service=${1:-""}
    
    if [ -n "$service" ]; then
        log "📋 $service logları:"
        docker-compose -f docker-compose.prod.yml logs -f "$service"
    else
        log "📋 Tüm servis logları:"
        docker-compose -f docker-compose.prod.yml logs -f
    fi
}

# Servis durumlarını göster
status() {
    log "📊 Servis durumları:"
    docker-compose -f docker-compose.prod.yml ps
    
    log "📈 Container kaynak kullanımı:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"
}

# Servisleri yeniden başlat
restart() {
    log "🔄 Tüm servisler yeniden başlatılıyor..."
    docker-compose -f docker-compose.prod.yml restart
    
    log "⏳ Servislerin başlaması bekleniyor..."
    sleep 15
    
    status
}

# Servisleri durdur
stop() {
    log "🛑 Tüm servisler durduruluyor..."
    docker-compose -f docker-compose.prod.yml down
}

# Temizlik yap
clean() {
    log "🧹 Temizlik yapılıyor..."
    
    # Durdurulmuş container'ları kaldır
    docker container prune -f
    
    # Kullanılmayan image'ları kaldır
    docker image prune -f
    
    # Kullanılmayan volume'ları kaldır
    docker volume prune -f
    
    # Kullanılmayan network'leri kaldır
    docker network prune -f
    
    success "✅ Temizlik tamamlandı!"
}

# Ana fonksiyon
main() {
    case "${1:-help}" in
        deploy)
            deploy
            ;;
        frontend)
            frontend
            ;;
        admin)
            admin
            ;;
        debug)
            debug
            ;;
        logs)
            logs "$2"
            ;;
        status)
            status
            ;;
        restart)
            restart
            ;;
        stop)
            stop
            ;;
        clean)
            clean
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            error "Bilinmeyen komut: $1"
            show_help
            exit 1
            ;;
    esac
}

# Script'i çalıştır
main "$@"
