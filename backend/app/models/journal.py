from datetime import datetime
from app import db

class Journal(db.Model):
    __tablename__ = 'journals'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    base_url = db.Column(db.String(500), nullable=False)
    proxy_path = db.Column(db.String(100), unique=True, nullable=False, index=True)
    
    # Proxy configuration
    requires_auth = db.Column(db.Boolean, default=True, nullable=False)
    auth_method = db.Column(db.String(50), default='ip')  # ip, username, token
    custom_headers = db.Column(db.JSON)  # Custom headers for proxy requests
    timeout = db.Column(db.Integer, default=30)  # Request timeout in seconds
    
    # Access control
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    access_level = db.Column(db.String(20), default='public')  # public, restricted, admin
    
    # Metadata
    publisher = db.Column(db.String(200))
    issn = db.Column(db.String(20))
    e_issn = db.Column(db.String(20))
    subject_areas = db.Column(db.JSON)  # List of subject areas
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    proxy_configs = db.relationship('ProxyConfig', backref='journal', lazy='dynamic')
    access_logs = db.relationship('AccessLog', backref='journal', lazy='dynamic')
    
    def __init__(self, name, slug, base_url, proxy_path, **kwargs):
        self.name = name
        self.slug = slug
        self.base_url = base_url.rstrip('/')
        self.proxy_path = proxy_path.lstrip('/')
        
        # Set optional fields
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def get_proxy_url(self, request_host=None):
        """Generate proxy URL for this journal"""
        if request_host:
            return f"http://{request_host}/{self.proxy_path}"
        return f"/{self.proxy_path}"
    
    def get_full_url(self, path=''):
        """Get full URL for journal access"""
        if path:
            return f"{self.base_url}/{path.lstrip('/')}"
        return self.base_url
    
    def to_dict(self):
        """Convert journal to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'base_url': self.base_url,
            'proxy_path': self.proxy_path,
            'requires_auth': self.requires_auth,
            'auth_method': self.auth_method,
            'custom_headers': self.custom_headers,
            'timeout': self.timeout,
            'is_active': self.is_active,
            'access_level': self.access_level,
            'publisher': self.publisher,
            'issn': self.issn,
            'e_issn': self.e_issn,
            'subject_areas': self.subject_areas,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Journal {self.name}>'
