#!/usr/bin/env python3
"""
Admin araçları - Birleştirilmiş admin yönetim scripti
Production sunucusunda admin kullanıcısı yönetimi için kullanılır.
"""

import os
import sys
from datetime import datetime

# Flask app context'ini oluştur
sys.path.append('/app')
from app import create_app, db, bcrypt
from app.models.user import User
from app.services.auth_service import AuthService

def check_database():
    """Veritabanı durumunu kontrol et"""
    
    app = create_app()
    
    with app.app_context():
        try:
            print("🔍 Veritabanı bağlantısı kontrol ediliyor...")
            
            # Veritabanı bağlantısını test et
            db.engine.execute('SELECT 1')
            print("✅ Veritabanı bağlantısı başarılı!")
            
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
                
                # Şifre hash'ini kontrol et
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

def force_create_admin():
    """Admin kullanıcısını zorla oluştur"""
    
    app = create_app()
    
    with app.app_context():
        try:
            print("🔍 Mevcut admin kullanıcıları kontrol ediliyor...")
            
            # Tüm admin kullanıcılarını listele
            admin_users = User.query.filter_by(is_admin=True).all()
            print(f"📊 Toplam admin kullanıcı sayısı: {len(admin_users)}")
            
            for user in admin_users:
                print(f"   - {user.username} ({user.email}) - Aktif: {user.is_active}")
            
            # Mevcut admin kullanıcısını sil
            existing_admin = User.query.filter_by(username='admin').first()
            if existing_admin:
                print(f"🗑️  Mevcut admin kullanıcısı siliniyor: {existing_admin.username}")
                db.session.delete(existing_admin)
                db.session.commit()
                print("✅ Mevcut admin kullanıcısı silindi")
            
            # Yeni admin kullanıcısı oluştur
            print("👤 Yeni admin kullanıcısı oluşturuluyor...")
            
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
            db.session.commit()
            
            print("✅ Yeni admin kullanıcısı oluşturuldu!")
            
            # Oluşturulan kullanıcıyı kontrol et
            created_admin = User.query.filter_by(username='admin').first()
            
            if created_admin:
                print(f"📋 Oluşturulan admin bilgileri:")
                print(f"   ID: {created_admin.id}")
                print(f"   Username: {created_admin.username}")
                print(f"   Email: {created_admin.email}")
                print(f"   First Name: {created_admin.first_name}")
                print(f"   Last Name: {created_admin.last_name}")
                print(f"   Is Admin: {created_admin.is_admin}")
                print(f"   Is Active: {created_admin.is_active}")
                print(f"   Created: {created_admin.created_at}")
                print(f"   Updated: {created_admin.updated_at}")
                
                # Şifre hash'ini kontrol et
                print(f"   Password Hash: {created_admin.password_hash[:50]}...")
                
                # Şifre doğrulamasını test et
                if created_admin.check_password('admin123'):
                    print("✅ Şifre doğrulaması başarılı!")
                else:
                    print("❌ Şifre doğrulaması başarısız!")
                    return False
                
            else:
                print("❌ Admin kullanıcısı oluşturulamadı!")
                return False
                
        except Exception as e:
            print(f"❌ Hata oluştu: {str(e)}")
            db.session.rollback()
            return False
            
    return True

def test_login():
    """Giriş testi yap"""
    
    app = create_app()
    
    with app.app_context():
        try:
            auth_service = AuthService()
            user = auth_service.authenticate_user('admin', 'admin123')
            
            if user:
                print("✅ Auth service ile giriş testi başarılı!")
                print(f"   Kullanıcı: {user.username}")
                print(f"   Admin: {user.is_admin}")
                print(f"   Aktif: {user.is_active}")
                return True
            else:
                print("❌ Auth service ile giriş testi başarısız!")
                return False
                
        except Exception as e:
            print(f"❌ Giriş testi hatası: {str(e)}")
            return False

def main():
    """Ana fonksiyon"""
    if len(sys.argv) < 2:
        print("Kullanım: python admin_tools.py <komut>")
        print("Komutlar:")
        print("  check     - Veritabanı durumunu kontrol et")
        print("  create    - Admin kullanıcısı oluştur/güncelle")
        print("  force     - Admin kullanıcısını zorla oluştur")
        print("  test      - Giriş testi yap")
        print("  all       - Tüm işlemleri sırayla yap")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'check':
        check_database()
    elif command == 'create':
        create_admin_user()
    elif command == 'force':
        force_create_admin()
    elif command == 'test':
        test_login()
    elif command == 'all':
        print("🚀 Tüm admin işlemleri başlatılıyor...")
        check_database()
        print("\n" + "="*50)
        create_admin_user()
        print("\n" + "="*50)
        test_login()
    else:
        print(f"❌ Bilinmeyen komut: {command}")
        sys.exit(1)

if __name__ == '__main__':
    main()
