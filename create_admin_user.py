#!/usr/bin/env python3
"""
Admin kullanıcısı oluşturma scripti
Production sunucusunda admin kullanıcısını oluşturmak için kullanılır.
"""

import os
import sys
from datetime import datetime

# Flask app context'ini oluştur
sys.path.append('/app')
from app import create_app, db, bcrypt
from app.models.user import User

def create_admin_user():
    """Admin kullanıcısını oluştur veya güncelle"""
    
    app = create_app()
    
    with app.app_context():
        try:
            # Mevcut admin kullanıcısını kontrol et
            admin_user = User.query.filter_by(username='admin').first()
            
            if admin_user:
                print("🔍 Admin kullanıcısı bulundu, şifre güncelleniyor...")
                # Şifreyi güncelle (bcrypt kullanarak)
                admin_user.set_password('admin123')
                admin_user.updated_at = datetime.utcnow()
            else:
                print("👤 Yeni admin kullanıcısı oluşturuluyor...")
                # Yeni admin kullanıcısı oluştur
                admin_user = User(
                    username='admin',
                    email='admin@libproxy.local',
                    password='admin123',
                    first_name='Admin',
                    last_name='User',
                    is_admin=True,
                    is_active=True
                )
                db.session.add(admin_user)
            
            # Değişiklikleri kaydet
            db.session.commit()
            
            print("✅ Admin kullanıcısı başarıyla oluşturuldu/güncellendi!")
            print("📋 Admin bilgileri:")
            print(f"   Kullanıcı adı: admin")
            print(f"   Şifre: admin123")
            print(f"   Email: admin@libproxy.local")
            print(f"   Admin yetkisi: Evet")
            print(f"   Aktif: Evet")
            
            # Tüm admin kullanıcılarını listele
            admin_users = User.query.filter_by(is_admin=True).all()
            print(f"\n📊 Toplam admin kullanıcı sayısı: {len(admin_users)}")
            for user in admin_users:
                print(f"   - {user.username} ({user.email}) - Aktif: {user.is_active}")
                
        except Exception as e:
            print(f"❌ Hata oluştu: {str(e)}")
            db.session.rollback()
            return False
            
    return True

if __name__ == '__main__':
    print("🚀 Admin kullanıcısı oluşturma scripti başlatılıyor...")
    success = create_admin_user()
    
    if success:
        print("\n🎉 İşlem başarıyla tamamlandı!")
        print("\n🔗 Giriş yapmak için:")
        print("   Frontend: http://80.251.40.216:3000/login")
        print("   Kullanıcı adı: admin")
        print("   Şifre: admin123")
    else:
        print("\n💥 İşlem başarısız oldu!")
        sys.exit(1)
