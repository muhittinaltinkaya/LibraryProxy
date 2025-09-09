#!/usr/bin/env python3
"""
Veritabanı durumunu kontrol etme scripti
Production sunucusunda veritabanı bağlantısını ve kullanıcıları kontrol eder.
"""

import os
import sys
from datetime import datetime

# Flask app context'ini oluştur
sys.path.append('/app')
from app import create_app, db
from app.models.user import User

def check_database():
    """Veritabanı durumunu kontrol et"""
    
    app = create_app()
    
    with app.app_context():
        try:
            print("🔍 Veritabanı bağlantısı kontrol ediliyor...")
            
            # Veritabanı bağlantısını test et
            db.engine.execute('SELECT 1')
            print("✅ Veritabanı bağlantısı başarılı!")
            
            # Tabloları kontrol et
            print("\n📋 Tablo durumları:")
            tables = db.engine.table_names()
            for table in tables:
                print(f"   ✓ {table}")
            
            # Kullanıcıları listele
            print("\n👥 Kullanıcı listesi:")
            users = User.query.all()
            
            if not users:
                print("   ⚠️  Hiç kullanıcı bulunamadı!")
                return False
            
            for user in users:
                admin_status = "Admin" if user.is_admin else "Kullanıcı"
                active_status = "Aktif" if user.is_active else "Pasif"
                print(f"   - {user.username} ({user.email}) - {admin_status} - {active_status}")
            
            # Admin kullanıcısını özel olarak kontrol et
            admin_user = User.query.filter_by(username='admin').first()
            
            if admin_user:
                print(f"\n✅ Admin kullanıcısı bulundu!")
                print(f"   ID: {admin_user.id}")
                print(f"   Email: {admin_user.email}")
                print(f"   Admin: {admin_user.is_admin}")
                print(f"   Aktif: {admin_user.is_active}")
                print(f"   Oluşturulma: {admin_user.created_at}")
                print(f"   Son güncelleme: {admin_user.updated_at}")
                
                # Şifre hash'ini kontrol et (güvenlik için sadece varlığını)
                if admin_user.password_hash:
                    print(f"   Şifre hash: Mevcut (uzunluk: {len(admin_user.password_hash)})")
                else:
                    print(f"   ⚠️  Şifre hash: YOK!")
                    return False
            else:
                print(f"\n❌ Admin kullanıcısı bulunamadı!")
                return False
                
        except Exception as e:
            print(f"❌ Veritabanı hatası: {str(e)}")
            return False
            
    return True

def test_login():
    """Admin girişini test et"""
    
    app = create_app()
    
    with app.app_context():
        try:
            from werkzeug.security import check_password_hash
            
            admin_user = User.query.filter_by(username='admin').first()
            
            if not admin_user:
                print("❌ Admin kullanıcısı bulunamadı!")
                return False
            
            # Şifre kontrolü
            if check_password_hash(admin_user.password_hash, 'admin123'):
                print("✅ Şifre doğrulaması başarılı!")
                return True
            else:
                print("❌ Şifre doğrulaması başarısız!")
                return False
                
        except Exception as e:
            print(f"❌ Giriş testi hatası: {str(e)}")
            return False

if __name__ == '__main__':
    print("🔍 Veritabanı kontrol scripti başlatılıyor...")
    
    # Veritabanını kontrol et
    db_ok = check_database()
    
    if db_ok:
        print("\n🧪 Giriş testi yapılıyor...")
        login_ok = test_login()
        
        if login_ok:
            print("\n🎉 Tüm kontroller başarılı!")
            print("\n🔗 Giriş bilgileri:")
            print("   URL: http://80.251.40.216:3000/login")
            print("   Kullanıcı adı: admin")
            print("   Şifre: admin123")
        else:
            print("\n⚠️  Giriş testi başarısız! Admin kullanıcısını yeniden oluşturun.")
    else:
        print("\n💥 Veritabanı kontrolleri başarısız!")
        
    print("\n" + "="*50)
