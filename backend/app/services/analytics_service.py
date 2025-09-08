from datetime import datetime, timedelta
from sqlalchemy import func, desc, and_, or_
from app import db
from app.models.analytics_log import AnalyticsLog
from app.models.user import User
from app.models.journal import Journal

class AnalyticsService:
    """OpenAthens benzeri analitik ve raporlama servisi"""
    
    def __init__(self):
        self.db = db
    
    def get_usage_statistics(self, start_date=None, end_date=None, filters=None):
        """Genel kullanım istatistikleri"""
        query = AnalyticsLog.query
        
        # Tarih filtresi
        if start_date:
            query = query.filter(AnalyticsLog.access_timestamp >= start_date)
        if end_date:
            query = query.filter(AnalyticsLog.access_timestamp <= end_date)
        
        # Diğer filtreler
        if filters:
            if filters.get('user_id'):
                query = query.filter(AnalyticsLog.user_id == filters['user_id'])
            if filters.get('department'):
                query = query.filter(AnalyticsLog.department == filters['department'])
            if filters.get('resource_type'):
                query = query.filter(AnalyticsLog.resource_type == filters['resource_type'])
            if filters.get('account_type'):
                query = query.filter(AnalyticsLog.account_type == filters['account_type'])
        
        # Temel istatistikler
        total_accesses = query.count()
        unique_users = query.filter(AnalyticsLog.user_id.isnot(None)).distinct(AnalyticsLog.user_id).count()
        unique_resources = query.distinct(AnalyticsLog.resource_name).count()
        
        # Başarılı/başarısız erişimler
        successful_accesses = query.filter(AnalyticsLog.auth_success == True).count()
        failed_accesses = query.filter(AnalyticsLog.auth_success == False).count()
        
        # Erişim reddi
        denied_accesses = query.filter(AnalyticsLog.access_denied == True).count()
        
        return {
            'total_accesses': total_accesses,
            'unique_users': unique_users,
            'unique_resources': unique_resources,
            'successful_accesses': successful_accesses,
            'failed_accesses': failed_accesses,
            'denied_accesses': denied_accesses,
            'success_rate': (successful_accesses / total_accesses * 100) if total_accesses > 0 else 0
        }
    
    def get_resource_usage_report(self, start_date=None, end_date=None, limit=50):
        """En çok kullanılan kaynaklar raporu"""
        query = AnalyticsLog.query.filter(AnalyticsLog.resource_name.isnot(None))
        
        if start_date:
            query = query.filter(AnalyticsLog.access_timestamp >= start_date)
        if end_date:
            query = query.filter(AnalyticsLog.access_timestamp <= end_date)
        
        resource_stats = query.with_entities(
            AnalyticsLog.resource_name,
            AnalyticsLog.resource_type,
            AnalyticsLog.resource_provider,
            func.count(AnalyticsLog.id).label('access_count'),
            func.count(func.distinct(AnalyticsLog.user_id)).label('unique_users'),
            func.sum(AnalyticsLog.page_views).label('total_page_views'),
            func.sum(AnalyticsLog.downloads).label('total_downloads'),
            func.sum(AnalyticsLog.searches).label('total_searches')
        ).group_by(
            AnalyticsLog.resource_name,
            AnalyticsLog.resource_type,
            AnalyticsLog.resource_provider
        ).order_by(desc('access_count')).limit(limit).all()
        
        return [
            {
                'resource_name': stat.resource_name,
                'resource_type': stat.resource_type,
                'resource_provider': stat.resource_provider,
                'access_count': stat.access_count,
                'unique_users': stat.unique_users,
                'total_page_views': stat.total_page_views or 0,
                'total_downloads': stat.total_downloads or 0,
                'total_searches': stat.total_searches or 0
            }
            for stat in resource_stats
        ]
    
    def get_user_activity_report(self, start_date=None, end_date=None, limit=50):
        """En aktif kullanıcılar raporu"""
        query = AnalyticsLog.query.filter(AnalyticsLog.user_id.isnot(None))
        
        if start_date:
            query = query.filter(AnalyticsLog.access_timestamp >= start_date)
        if end_date:
            query = query.filter(AnalyticsLog.access_timestamp <= end_date)
        
        user_stats = query.with_entities(
            AnalyticsLog.user_id,
            AnalyticsLog.department,
            AnalyticsLog.academic_unit,
            AnalyticsLog.account_type,
            func.count(AnalyticsLog.id).label('access_count'),
            func.count(func.distinct(AnalyticsLog.resource_name)).label('unique_resources'),
            func.sum(AnalyticsLog.page_views).label('total_page_views'),
            func.sum(AnalyticsLog.downloads).label('total_downloads'),
            func.min(AnalyticsLog.access_timestamp).label('first_access'),
            func.max(AnalyticsLog.access_timestamp).label('last_access')
        ).group_by(
            AnalyticsLog.user_id,
            AnalyticsLog.department,
            AnalyticsLog.academic_unit,
            AnalyticsLog.account_type
        ).order_by(desc('access_count')).limit(limit).all()
        
        # Kullanıcı bilgilerini al
        user_ids = [stat.user_id for stat in user_stats]
        users = {u.id: u for u in User.query.filter(User.id.in_(user_ids)).all()}
        
        return [
            {
                'user_id': stat.user_id,
                'username': users.get(stat.user_id, {}).username if users.get(stat.user_id) else 'Unknown',
                'email': users.get(stat.user_id, {}).email if users.get(stat.user_id) else 'Unknown',
                'first_name': users.get(stat.user_id, {}).first_name if users.get(stat.user_id) else '',
                'last_name': users.get(stat.user_id, {}).last_name if users.get(stat.user_id) else '',
                'department': stat.department,
                'academic_unit': stat.academic_unit,
                'account_type': stat.account_type,
                'access_count': stat.access_count,
                'unique_resources': stat.unique_resources,
                'total_page_views': stat.total_page_views or 0,
                'total_downloads': stat.total_downloads or 0,
                'first_access': stat.first_access.isoformat() if stat.first_access else None,
                'last_access': stat.last_access.isoformat() if stat.last_access else None
            }
            for stat in user_stats
        ]
    
    def get_department_usage_report(self, start_date=None, end_date=None):
        """Departman bazlı kullanım raporu"""
        query = AnalyticsLog.query.filter(AnalyticsLog.department.isnot(None))
        
        if start_date:
            query = query.filter(AnalyticsLog.access_timestamp >= start_date)
        if end_date:
            query = query.filter(AnalyticsLog.access_timestamp <= end_date)
        
        dept_stats = query.with_entities(
            AnalyticsLog.department,
            AnalyticsLog.academic_unit,
            func.count(AnalyticsLog.id).label('access_count'),
            func.count(func.distinct(AnalyticsLog.user_id)).label('unique_users'),
            func.count(func.distinct(AnalyticsLog.resource_name)).label('unique_resources'),
            func.sum(AnalyticsLog.page_views).label('total_page_views'),
            func.sum(AnalyticsLog.downloads).label('total_downloads')
        ).group_by(
            AnalyticsLog.department,
            AnalyticsLog.academic_unit
        ).order_by(desc('access_count')).all()
        
        return [
            {
                'department': stat.department,
                'academic_unit': stat.academic_unit,
                'access_count': stat.access_count,
                'unique_users': stat.unique_users,
                'unique_resources': stat.unique_resources,
                'total_page_views': stat.total_page_views or 0,
                'total_downloads': stat.total_downloads or 0
            }
            for stat in dept_stats
        ]
    
    def get_hourly_usage_pattern(self, start_date=None, end_date=None):
        """Saatlik kullanım paterni"""
        query = AnalyticsLog.query
        
        if start_date:
            query = query.filter(AnalyticsLog.access_timestamp >= start_date)
        if end_date:
            query = query.filter(AnalyticsLog.access_timestamp <= end_date)
        
        hourly_stats = query.with_entities(
            func.extract('hour', AnalyticsLog.access_timestamp).label('hour'),
            func.count(AnalyticsLog.id).label('access_count'),
            func.count(func.distinct(AnalyticsLog.user_id)).label('unique_users')
        ).group_by(
            func.extract('hour', AnalyticsLog.access_timestamp)
        ).order_by('hour').all()
        
        return [
            {
                'hour': int(stat.hour),
                'access_count': stat.access_count,
                'unique_users': stat.unique_users
            }
            for stat in hourly_stats
        ]
    
    def get_daily_usage_trend(self, days=30):
        """Günlük kullanım trendi"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        query = AnalyticsLog.query.filter(
            and_(
                AnalyticsLog.access_timestamp >= start_date,
                AnalyticsLog.access_timestamp <= end_date
            )
        )
        
        daily_stats = query.with_entities(
            func.date(AnalyticsLog.access_timestamp).label('date'),
            func.count(AnalyticsLog.id).label('access_count'),
            func.count(func.distinct(AnalyticsLog.user_id)).label('unique_users'),
            func.count(func.distinct(AnalyticsLog.resource_name)).label('unique_resources')
        ).group_by(
            func.date(AnalyticsLog.access_timestamp)
        ).order_by('date').all()
        
        return [
            {
                'date': stat.date.isoformat(),
                'access_count': stat.access_count,
                'unique_users': stat.unique_users,
                'unique_resources': stat.unique_resources
            }
            for stat in daily_stats
        ]
    
    def get_failed_access_analysis(self, start_date=None, end_date=None):
        """Başarısız erişim analizi"""
        query = AnalyticsLog.query.filter(AnalyticsLog.auth_success == False)
        
        if start_date:
            query = query.filter(AnalyticsLog.access_timestamp >= start_date)
        if end_date:
            query = query.filter(AnalyticsLog.access_timestamp <= end_date)
        
        failure_stats = query.with_entities(
            AnalyticsLog.auth_failure_reason,
            AnalyticsLog.denial_reason,
            func.count(AnalyticsLog.id).label('failure_count'),
            func.count(func.distinct(AnalyticsLog.user_id)).label('affected_users')
        ).group_by(
            AnalyticsLog.auth_failure_reason,
            AnalyticsLog.denial_reason
        ).order_by(desc('failure_count')).all()
        
        return [
            {
                'auth_failure_reason': stat.auth_failure_reason,
                'denial_reason': stat.denial_reason,
                'failure_count': stat.failure_count,
                'affected_users': stat.affected_users
            }
            for stat in failure_stats
        ]
    
    def get_geographic_usage_report(self, start_date=None, end_date=None):
        """Coğrafi kullanım raporu"""
        query = AnalyticsLog.query.filter(AnalyticsLog.country.isnot(None))
        
        if start_date:
            query = query.filter(AnalyticsLog.access_timestamp >= start_date)
        if end_date:
            query = query.filter(AnalyticsLog.access_timestamp <= end_date)
        
        geo_stats = query.with_entities(
            AnalyticsLog.country,
            AnalyticsLog.region,
            AnalyticsLog.city,
            func.count(AnalyticsLog.id).label('access_count'),
            func.count(func.distinct(AnalyticsLog.user_id)).label('unique_users'),
            func.count(func.distinct(AnalyticsLog.ip_address)).label('unique_ips')
        ).group_by(
            AnalyticsLog.country,
            AnalyticsLog.region,
            AnalyticsLog.city
        ).order_by(desc('access_count')).all()
        
        return [
            {
                'country': stat.country,
                'region': stat.region,
                'city': stat.city,
                'access_count': stat.access_count,
                'unique_users': stat.unique_users,
                'unique_ips': stat.unique_ips
            }
            for stat in geo_stats
        ]
    
    def get_turn_away_analysis(self, start_date=None, end_date=None):
        """Erişim reddi analizi (Turn-away analysis)"""
        query = AnalyticsLog.query.filter(AnalyticsLog.access_denied == True)
        
        if start_date:
            query = query.filter(AnalyticsLog.access_timestamp >= start_date)
        if end_date:
            query = query.filter(AnalyticsLog.access_timestamp <= end_date)
        
        turn_away_stats = query.with_entities(
            AnalyticsLog.resource_name,
            AnalyticsLog.denial_reason,
            func.count(AnalyticsLog.id).label('denial_count'),
            func.count(func.distinct(AnalyticsLog.user_id)).label('affected_users')
        ).group_by(
            AnalyticsLog.resource_name,
            AnalyticsLog.denial_reason
        ).order_by(desc('denial_count')).all()
        
        return [
            {
                'resource_name': stat.resource_name,
                'denial_reason': stat.denial_reason,
                'denial_count': stat.denial_count,
                'affected_users': stat.affected_users
            }
            for stat in turn_away_stats
        ]
    
    def get_custom_breakdown_report(self, breakdown_field, start_date=None, end_date=None):
        """Özelleştirilebilir kırılım raporu"""
        query = AnalyticsLog.query
        
        if start_date:
            query = query.filter(AnalyticsLog.access_timestamp >= start_date)
        if end_date:
            query = query.filter(AnalyticsLog.access_timestamp <= end_date)
        
        # Dinamik alan seçimi
        field = getattr(AnalyticsLog, breakdown_field, None)
        if not field:
            return []
        
        breakdown_stats = query.with_entities(
            field,
            func.count(AnalyticsLog.id).label('access_count'),
            func.count(func.distinct(AnalyticsLog.user_id)).label('unique_users'),
            func.count(func.distinct(AnalyticsLog.resource_name)).label('unique_resources')
        ).group_by(field).order_by(desc('access_count')).all()
        
        return [
            {
                'breakdown_value': getattr(stat, breakdown_field),
                'access_count': stat.access_count,
                'unique_users': stat.unique_users,
                'unique_resources': stat.unique_resources
            }
            for stat in breakdown_stats
        ]
