#!/usr/bin/env python3
"""
Admin hash güncelleme scripti
Veritabanındaki admin kullanıcısının şifre hash'ini bcrypt ile günceller.
"""

import sys
sys.path.append('/app')
from app import create_app, db, bcrypt

def update_admin_hash():
    """Admin kullanıcısının şifre hash'ini güncelle"""
    
    app = create_app()
    
    with app.app_context():
        try:
            # Bcrypt hash oluştur
            password = 'admin123'
            bcrypt_hash = bcrypt.generate_password_hash(password).decode('utf-8')
            
            print(f"🔐 Yeni bcrypt hash: {bcrypt_hash}")
            
            # SQL komutu ile güncelle
            result = db.engine.execute(
                "UPDATE users SET password_hash = %s WHERE username = 'admin'",
                (bcrypt_hash,)
            )
            
            print(f"✅ {result.rowcount} kullanıcı güncellendi")
            
            # Kontrol et
            admin_check = db.engine.execute(
                "SELECT username, password_hash, is_admin, is_active FROM users WHERE username = 'admin'"
            ).fetchone()
            
            if admin_check:
                print(f"📋 Admin kullanıcı bilgileri:")
                print(f"   Kullanıcı adı: {admin_check[0]}")
                print(f"   Hash: {admin_check[1][:50]}...")
                print(f"   Admin: {admin_check[2]}")
                print(f"   Aktif: {admin_check[3]}")
                
                # Hash'i test et
                if bcrypt.check_password_hash(admin_check[1], password):
                    print("✅ Şifre hash doğrulaması başarılı!")
                else:
                    print("❌ Şifre hash doğrulaması başarısız!")
            else:
                print("❌ Admin kullanıcısı bulunamadı!")
                
        except Exception as e:
            print(f"❌ Hata: {str(e)}")
            return False
            
    return True

if __name__ == '__main__':
    print("🔧 Admin hash güncelleme scripti başlatılıyor...")
    success = update_admin_hash()
    
    if success:
        print("\n🎉 Hash güncelleme tamamlandı!")
    else:
        print("\n💥 Hash güncelleme başarısız!")
        sys.exit(1)
