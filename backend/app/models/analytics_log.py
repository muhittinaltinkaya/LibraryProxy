from datetime import datetime
from app import db
import json

class AnalyticsLog(db.Model):
    """OpenAthens benzeri kapsamlı analitik log modeli"""
    __tablename__ = 'analytics_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Kullanıcı ve Hesap Bilgileri
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    user_identifier = db.Column(db.String(255))  # Anonimleştirilmiş kullanıcı kimliği
    account_status = db.Column(db.String(50))  # active, inactive, suspended, expired
    account_type = db.Column(db.String(50))  # student, faculty, staff, guest
    department = db.Column(db.String(255))  # Departman/Fakülte
    academic_unit = db.Column(db.String(255))  # Akademik bölüm
    user_status = db.Column(db.String(100))  # Lisans, yüksek lisans, doktora
    location = db.Column(db.String(255))  # Fiziksel konum
    institution = db.Column(db.String(255))  # Kurum bilgisi
    
    # IP ve Coğrafi Bilgiler
    ip_address = db.Column(db.String(45), nullable=False)
    country = db.Column(db.String(100))
    city = db.Column(db.String(100))
    region = db.Column(db.String(100))
    
    # Kaynak Erişim Bilgileri
    resource_name = db.Column(db.String(500), nullable=False)  # Erişilen kaynak adı
    resource_type = db.Column(db.String(100))  # journal, database, ebook
    resource_provider = db.Column(db.String(255))  # Yayıncı/Provider
    resource_url = db.Column(db.String(1000))  # Kaynak URL'i
    access_count = db.Column(db.Integer, default=1)  # Erişim sayısı (transfers)
    
    # Oturum ve Kimlik Doğrulama
    session_id = db.Column(db.String(100))
    auth_success = db.Column(db.Boolean, default=True)
    auth_failure_reason = db.Column(db.String(255))  # Başarısız giriş nedeni
    identity_provider = db.Column(db.String(100))  # IdP bilgisi
    auth_method = db.Column(db.String(50))  # password, sso, oauth
    
    # Erişim Detayları
    access_timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    access_duration = db.Column(db.Integer)  # Erişim süresi (saniye)
    page_views = db.Column(db.Integer, default=1)  # Sayfa görüntüleme sayısı
    downloads = db.Column(db.Integer, default=0)  # İndirme sayısı
    searches = db.Column(db.Integer, default=0)  # Arama sayısı
    
    # HTTP Detayları
    request_method = db.Column(db.String(10), default='GET')
    request_path = db.Column(db.String(500))
    request_query = db.Column(db.String(1000))
    user_agent = db.Column(db.String(1000))
    referer = db.Column(db.String(1000))
    
    # Response Bilgileri
    response_status = db.Column(db.Integer)
    response_size = db.Column(db.Integer)
    response_time = db.Column(db.Float)  # Response time in milliseconds
    
    # Özel Öznitelikler (Custom Attributes)
    custom_attributes = db.Column(db.Text)  # JSON formatında özel veriler
    
    # Erişim Kısıtlamaları
    access_denied = db.Column(db.Boolean, default=False)
    denial_reason = db.Column(db.String(255))  # Erişim reddi nedeni
    license_restriction = db.Column(db.Boolean, default=False)
    
    # Raporlama için ek alanlar
    report_period = db.Column(db.String(20))  # daily, weekly, monthly
    report_category = db.Column(db.String(100))  # Kategori bilgisi
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    @classmethod
    def log_resource_access(cls, user_id, resource_name, ip_address, **kwargs):
        """Kaynak erişim logu oluştur"""
        log_entry = cls(
            user_id=user_id,
            resource_name=resource_name,
            ip_address=ip_address,
            access_timestamp=datetime.utcnow()
        )
        
        # Ek parametreleri ayarla
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        db.session.add(log_entry)
        db.session.commit()
        
        return log_entry
    
    @classmethod
    def log_auth_attempt(cls, user_id, ip_address, success=True, **kwargs):
        """Kimlik doğrulama denemesi logu"""
        log_entry = cls(
            user_id=user_id,
            ip_address=ip_address,
            auth_success=success,
            access_timestamp=datetime.utcnow()
        )
        
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        db.session.add(log_entry)
        db.session.commit()
        
        return log_entry
    
    def set_custom_attributes(self, attributes):
        """Özel öznitelikleri ayarla"""
        if isinstance(attributes, dict):
            self.custom_attributes = json.dumps(attributes)
        else:
            self.custom_attributes = attributes
    
    def get_custom_attributes(self):
        """Özel öznitelikleri al"""
        if self.custom_attributes:
            try:
                return json.loads(self.custom_attributes)
            except:
                return {}
        return {}
    
    def to_dict(self):
        """Log'u dictionary'e çevir"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_identifier': self.user_identifier,
            'account_status': self.account_status,
            'account_type': self.account_type,
            'department': self.department,
            'academic_unit': self.academic_unit,
            'user_status': self.user_status,
            'location': self.location,
            'institution': self.institution,
            'ip_address': self.ip_address,
            'country': self.country,
            'city': self.city,
            'region': self.region,
            'resource_name': self.resource_name,
            'resource_type': self.resource_type,
            'resource_provider': self.resource_provider,
            'resource_url': self.resource_url,
            'access_count': self.access_count,
            'session_id': self.session_id,
            'auth_success': self.auth_success,
            'auth_failure_reason': self.auth_failure_reason,
            'identity_provider': self.identity_provider,
            'auth_method': self.auth_method,
            'access_timestamp': self.access_timestamp.isoformat(),
            'access_duration': self.access_duration,
            'page_views': self.page_views,
            'downloads': self.downloads,
            'searches': self.searches,
            'request_method': self.request_method,
            'request_path': self.request_path,
            'request_query': self.request_query,
            'user_agent': self.user_agent,
            'referer': self.referer,
            'response_status': self.response_status,
            'response_size': self.response_size,
            'response_time': self.response_time,
            'custom_attributes': self.get_custom_attributes(),
            'access_denied': self.access_denied,
            'denial_reason': self.denial_reason,
            'license_restriction': self.license_restriction,
            'report_period': self.report_period,
            'report_category': self.report_category
        }
    
    def __repr__(self):
        return f'<AnalyticsLog {self.id} - {self.resource_name}>'
