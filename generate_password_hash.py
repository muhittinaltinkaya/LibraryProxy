#!/usr/bin/env python3
"""
Şifre hash'i oluşturma scripti
Admin kullanıcısı için doğru şifre hash'ini oluşturur.
"""

from werkzeug.security import generate_password_hash, check_password_hash

def generate_admin_hash():
    """Admin şifresi için hash oluştur"""
    
    password = 'admin123'
    
    print("🔐 Şifre hash'i oluşturuluyor...")
    print(f"Şifre: {password}")
    
    # Werkzeug ile hash oluştur
    hash1 = generate_password_hash(password)
    print(f"Werkzeug Hash: {hash1}")
    
    # Hash'i test et
    if check_password_hash(hash1, password):
        print("✅ Werkzeug hash doğrulaması başarılı!")
    else:
        print("❌ Werkzeug hash doğrulaması başarısız!")
    
    # Mevcut hash'i test et
    existing_hash = '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/9yQK8i2'
    print(f"\nMevcut hash: {existing_hash}")
    
    if check_password_hash(existing_hash, password):
        print("✅ Mevcut hash doğrulaması başarılı!")
    else:
        print("❌ Mevcut hash doğrulaması başarısız!")
        
    # Farklı şifreler dene
    test_passwords = ['admin123', 'admin', 'password', '123456']
    print(f"\n🧪 Mevcut hash ile farklı şifreler test ediliyor:")
    
    for test_pwd in test_passwords:
        result = check_password_hash(existing_hash, test_pwd)
        status = "✅" if result else "❌"
        print(f"   {status} '{test_pwd}': {result}")
    
    print(f"\n📋 SQL Update komutu:")
    print(f"UPDATE users SET password_hash = '{hash1}' WHERE username = 'admin';")
    
    return hash1

if __name__ == '__main__':
    generate_admin_hash()
