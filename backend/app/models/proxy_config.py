from datetime import datetime
from app import db

class ProxyConfig(db.Model):
    __tablename__ = 'proxy_configs'
    
    id = db.Column(db.Integer, primary_key=True)
    journal_id = db.Column(db.Integer, db.ForeignKey('journals.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Proxy configuration
    config_name = db.Column(db.String(100), nullable=False)
    haproxy_rule = db.Column(db.Text, nullable=False)  # HAProxy configuration rule
    nginx_rule = db.Column(db.Text)  # Nginx configuration rule
    
    # Access control
    ip_address = db.Column(db.String(45))  # IPv4 or IPv6
    user_agent = db.Column(db.String(500))
    referer = db.Column(db.String(500))
    
    # Status and metadata
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    expires_at = db.Column(db.DateTime)  # When this config expires
    last_used = db.Column(db.DateTime)
    usage_count = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, journal_id, config_name, haproxy_rule, user_id=None, **kwargs):
        self.journal_id = journal_id
        self.config_name = config_name
        self.haproxy_rule = haproxy_rule
        self.user_id = user_id
        
        # Set optional fields
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def is_expired(self):
        """Check if this configuration has expired"""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at
    
    def update_usage(self):
        """Update usage statistics"""
        self.last_used = datetime.utcnow()
        self.usage_count += 1
        db.session.commit()
    
    def generate_haproxy_rule(self, journal, user=None):
        """Generate HAProxy configuration rule"""
        rule_parts = [
            f"acl is_{self.config_name} path_beg /{journal.proxy_path}",
            f"use_backend {journal.slug}_backend if is_{self.config_name}"
        ]
        
        # Add user-specific rules if user is provided
        if user:
            rule_parts.append(f"acl user_{user.id} hdr(X-User-ID) {user.id}")
            rule_parts.append(f"use_backend {journal.slug}_backend if is_{self.config_name} user_{user.id}")
        
        return "\n".join(rule_parts)
    
    def generate_nginx_rule(self, journal, user=None):
        """Generate Nginx configuration rule"""
        location_block = f"""
    location /{journal.proxy_path} {{
        proxy_pass {journal.base_url};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
"""
        
        # Add user-specific headers
        if user:
            location_block += f"        proxy_set_header X-User-ID {user.id};\n"
            location_block += f"        proxy_set_header X-User-Name {user.username};\n"
        
        # Add custom headers from journal
        if journal.custom_headers:
            for header, value in journal.custom_headers.items():
                location_block += f"        proxy_set_header {header} {value};\n"
        
        location_block += "    }"
        return location_block
    
    def to_dict(self):
        """Convert proxy config to dictionary"""
        return {
            'id': self.id,
            'journal_id': self.journal_id,
            'user_id': self.user_id,
            'config_name': self.config_name,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'referer': self.referer,
            'is_active': self.is_active,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'last_used': self.last_used.isoformat() if self.last_used else None,
            'usage_count': self.usage_count,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<ProxyConfig {self.config_name}>'
