from datetime import datetime
from app import db

class AccessLog(db.Model):
    __tablename__ = 'access_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    journal_id = db.Column(db.Integer, db.ForeignKey('journals.id'), nullable=False)
    proxy_config_id = db.Column(db.Integer, db.ForeignKey('proxy_configs.id'), nullable=True)
    
    # Request information
    ip_address = db.Column(db.String(45), nullable=False)
    user_agent = db.Column(db.String(500))
    referer = db.Column(db.String(500))
    request_method = db.Column(db.String(10), default='GET')
    request_path = db.Column(db.String(500))
    request_query = db.Column(db.String(1000))
    
    # Response information
    response_status = db.Column(db.Integer)
    response_size = db.Column(db.Integer)
    response_time = db.Column(db.Float)  # Response time in milliseconds
    
    # Session information
    session_id = db.Column(db.String(100))
    request_id = db.Column(db.String(100))  # Unique request identifier
    
    # Timestamps
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def __init__(self, journal_id, ip_address, **kwargs):
        self.journal_id = journal_id
        self.ip_address = ip_address
        
        # Set optional fields
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    @classmethod
    def log_access(cls, user_id, journal_id, ip_address, request_data=None, response_data=None):
        """Create a new access log entry"""
        log_entry = cls(
            user_id=user_id,
            journal_id=journal_id,
            ip_address=ip_address
        )
        
        if request_data:
            log_entry.user_agent = request_data.get('user_agent')
            log_entry.referer = request_data.get('referer')
            log_entry.request_method = request_data.get('method', 'GET')
            log_entry.request_path = request_data.get('path')
            log_entry.request_query = request_data.get('query_string')
            log_entry.session_id = request_data.get('session_id')
            log_entry.request_id = request_data.get('request_id')
        
        if response_data:
            log_entry.response_status = response_data.get('status_code')
            log_entry.response_size = response_data.get('content_length')
            log_entry.response_time = response_data.get('response_time')
        
        db.session.add(log_entry)
        db.session.commit()
        
        return log_entry
    
    def to_dict(self):
        """Convert access log to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'journal_id': self.journal_id,
            'proxy_config_id': self.proxy_config_id,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'referer': self.referer,
            'request_method': self.request_method,
            'request_path': self.request_path,
            'request_query': self.request_query,
            'response_status': self.response_status,
            'response_size': self.response_size,
            'response_time': self.response_time,
            'session_id': self.session_id,
            'request_id': self.request_id,
            'timestamp': self.timestamp.isoformat()
        }
    
    def __repr__(self):
        return f'<AccessLog {self.id} - {self.journal_id}>'
