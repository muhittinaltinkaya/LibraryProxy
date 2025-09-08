from datetime import datetime, timedelta
from app import db
from app.models.journal import Journal
from app.models.proxy_config import ProxyConfig
from app.models.access_log import AccessLog
from app.services.proxy_service import ProxyService

class JournalService:
    """Service for journal management and access control"""
    
    def __init__(self):
        self.proxy_service = ProxyService()
    
    def get_journal_by_id(self, journal_id):
        """Get journal by ID"""
        return Journal.query.get(journal_id)
    
    def get_journal_by_slug(self, slug):
        """Get journal by slug"""
        return Journal.query.filter_by(slug=slug).first()
    
    def create_journal(self, name, slug, base_url, proxy_path, **kwargs):
        """Create a new journal and automatically create its proxy configuration"""
        journal = Journal(
            name=name,
            slug=slug,
            base_url=base_url,
            proxy_path=proxy_path,
            **kwargs
        )
        
        db.session.add(journal)
        db.session.commit()
        
        # Automatically update HAProxy configuration with all active journals
        try:
            success = self.proxy_service.update_main_haproxy_config()
            if success:
                # Reload HAProxy to apply changes
                self.proxy_service.reload_haproxy()
                print(f"HAProxy configuration automatically updated for new journal: {journal.slug}")
            else:
                print(f"Warning: Failed to update HAProxy config for journal {journal.slug}")
        except Exception as e:
            print(f"Warning: Failed to update HAProxy config for journal {journal.slug}: {str(e)}")
        
        return journal
    
    def update_journal(self, journal_id, **kwargs):
        """Update journal information"""
        journal = self.get_journal_by_id(journal_id)
        
        if not journal:
            return None
        
        # Update allowed fields
        allowed_fields = [
            'name', 'description', 'base_url', 'proxy_path',
            'requires_auth', 'auth_method', 'custom_headers', 'timeout',
            'is_active', 'access_level', 'publisher', 'issn', 'e_issn',
            'subject_areas'
        ]
        
        for field, value in kwargs.items():
            if field in allowed_fields and hasattr(journal, field):
                setattr(journal, field, value)
        
        journal.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Automatically update HAProxy configuration when journal is updated
        try:
            success = self.proxy_service.update_main_haproxy_config()
            if success:
                # Reload HAProxy to apply changes
                self.proxy_service.reload_haproxy()
                print(f"HAProxy configuration automatically updated for journal update: {journal.slug}")
        except Exception as e:
            print(f"Warning: Failed to update HAProxy config for journal update {journal.slug}: {str(e)}")
        
        return journal
    
    def delete_journal(self, journal_id):
        """Delete journal (soft delete)"""
        journal = self.get_journal_by_id(journal_id)
        
        if not journal:
            return None
        
        journal.is_active = False
        journal.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Automatically update HAProxy configuration when journal is deleted
        try:
            success = self.proxy_service.update_main_haproxy_config()
            if success:
                # Reload HAProxy to apply changes
                self.proxy_service.reload_haproxy()
                print(f"HAProxy configuration automatically updated for journal deletion: {journal.slug}")
        except Exception as e:
            print(f"Warning: Failed to update HAProxy config for journal deletion {journal.slug}: {str(e)}")
        
        return journal
    
    def generate_proxy_config(self, journal, user):
        """Generate proxy configuration for journal access"""
        try:
            # Create proxy configuration
            config_name = f"{journal.slug}_{user.id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            # Generate HAProxy rule
            haproxy_rule = self.proxy_service.generate_haproxy_rule(journal, user)
            
            # Create proxy config record
            proxy_config = ProxyConfig(
                journal_id=journal.id,
                user_id=user.id,
                config_name=config_name,
                haproxy_rule=haproxy_rule,
                expires_at=datetime.utcnow() + timedelta(hours=24)  # 24 hour expiry
            )
            
            db.session.add(proxy_config)
            db.session.commit()
            
            # Apply proxy configuration
            self.proxy_service.apply_proxy_config(proxy_config)
            
            return proxy_config
            
        except Exception as e:
            db.session.rollback()
            raise e
    
    def create_global_proxy_config(self, journal):
        """Create a global proxy configuration for a journal that doesn't require user authentication"""
        try:
            # Create a global configuration name
            config_name = f"{journal.slug}_global_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            # Generate HAProxy rule without user-specific authentication
            haproxy_rule = self.proxy_service.generate_global_haproxy_rule(journal)
            
            # Create proxy config record without user_id (global access)
            proxy_config = ProxyConfig(
                journal_id=journal.id,
                user_id=None,  # Global configuration, no specific user
                config_name=config_name,
                haproxy_rule=haproxy_rule,
                expires_at=None  # Global configs don't expire
            )
            
            db.session.add(proxy_config)
            db.session.commit()
            
            # Apply proxy configuration
            self.proxy_service.apply_global_proxy_config(proxy_config)
            
            return proxy_config
            
        except Exception as e:
            db.session.rollback()
            raise e
    
    def log_access(self, journal_id, user_id, ip_address, request_data=None, response_data=None):
        """Log journal access"""
        try:
            access_log = AccessLog.log_access(
                user_id=user_id,
                journal_id=journal_id,
                ip_address=ip_address,
                request_data=request_data,
                response_data=response_data
            )
            
            return access_log
            
        except Exception as e:
            # Log error but don't fail the request
            print(f"Failed to log access: {str(e)}")
            return None
    
    def get_user_access_logs(self, user_id, limit=50):
        """Get access logs for a user"""
        return AccessLog.query.filter_by(user_id=user_id)\
            .order_by(AccessLog.timestamp.desc())\
            .limit(limit).all()
    
    def get_journal_access_logs(self, journal_id, limit=50):
        """Get access logs for a journal"""
        return AccessLog.query.filter_by(journal_id=journal_id)\
            .order_by(AccessLog.timestamp.desc())\
            .limit(limit).all()
    
    def get_popular_journals(self, limit=10):
        """Get most accessed journals"""
        from sqlalchemy import func
        
        popular_journals = db.session.query(
            Journal,
            func.count(AccessLog.id).label('access_count')
        ).join(AccessLog)\
        .filter(Journal.is_active == True)\
        .group_by(Journal.id)\
        .order_by(func.count(AccessLog.id).desc())\
        .limit(limit).all()
        
        return [journal for journal, count in popular_journals]
    
    def search_journals(self, query_text, filters=None):
        """Search journals with text and filters"""
        query = Journal.query.filter_by(is_active=True)
        
        if query_text:
            query = query.filter(
                Journal.name.ilike(f'%{query_text}%') |
                Journal.description.ilike(f'%{query_text}%') |
                Journal.publisher.ilike(f'%{query_text}%')
            )
        
        if filters:
            if 'subject_areas' in filters:
                for subject in filters['subject_areas']:
                    query = query.filter(Journal.subject_areas.contains([subject]))
            
            if 'access_level' in filters:
                query = query.filter(Journal.access_level == filters['access_level'])
            
            if 'publisher' in filters:
                query = query.filter(Journal.publisher.ilike(f'%{filters["publisher"]}%'))
        
        return query.all()
