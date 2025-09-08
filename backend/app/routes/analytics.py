from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from app import db
from app.models.user import User
from app.models.analytics_log import AnalyticsLog
from app.services.analytics_service import AnalyticsService

analytics_bp = Blueprint('analytics', __name__)
analytics_service = AnalyticsService()

@analytics_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard_stats():
    """Ana dashboard istatistikleri"""
    try:
        # Admin kontrolü
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        if not current_user or not current_user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        
        # Tarih filtreleri
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if start_date:
            start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        if end_date:
            end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        # Son 30 gün varsayılan
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()
        
        # Genel istatistikler
        stats = analytics_service.get_usage_statistics(start_date, end_date)
        
        # En çok kullanılan kaynaklar (top 10)
        top_resources = analytics_service.get_resource_usage_report(start_date, end_date, 10)
        
        # En aktif kullanıcılar (top 10)
        top_users = analytics_service.get_user_activity_report(start_date, end_date, 10)
        
        # Saatlik kullanım paterni
        hourly_pattern = analytics_service.get_hourly_usage_pattern(start_date, end_date)
        
        # Günlük trend (son 30 gün)
        daily_trend = analytics_service.get_daily_usage_trend(30)
        
        return jsonify({
            'general_stats': stats,
            'top_resources': top_resources,
            'top_users': top_users,
            'hourly_pattern': hourly_pattern,
            'daily_trend': daily_trend
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get dashboard stats', 'details': str(e)}), 500

@analytics_bp.route('/resources', methods=['GET'])
@jwt_required()
def get_resource_report():
    """Kaynak kullanım raporu"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        if not current_user or not current_user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        limit = int(request.args.get('limit', 50))
        
        if start_date:
            start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        if end_date:
            end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        resources = analytics_service.get_resource_usage_report(start_date, end_date, limit)
        
        return jsonify({
            'resources': resources,
            'total_count': len(resources)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get resource report', 'details': str(e)}), 500

@analytics_bp.route('/users', methods=['GET'])
@jwt_required()
def get_user_report():
    """Kullanıcı aktivite raporu"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        if not current_user or not current_user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        limit = int(request.args.get('limit', 50))
        
        if start_date:
            start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        if end_date:
            end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        users = analytics_service.get_user_activity_report(start_date, end_date, limit)
        
        return jsonify({
            'users': users,
            'total_count': len(users)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get user report', 'details': str(e)}), 500

@analytics_bp.route('/departments', methods=['GET'])
@jwt_required()
def get_department_report():
    """Departman kullanım raporu"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        if not current_user or not current_user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if start_date:
            start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        if end_date:
            end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        departments = analytics_service.get_department_usage_report(start_date, end_date)
        
        return jsonify({
            'departments': departments,
            'total_count': len(departments)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get department report', 'details': str(e)}), 500

@analytics_bp.route('/geographic', methods=['GET'])
@jwt_required()
def get_geographic_report():
    """Coğrafi kullanım raporu"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        if not current_user or not current_user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if start_date:
            start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        if end_date:
            end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        geographic = analytics_service.get_geographic_usage_report(start_date, end_date)
        
        return jsonify({
            'geographic': geographic,
            'total_count': len(geographic)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get geographic report', 'details': str(e)}), 500

@analytics_bp.route('/failures', methods=['GET'])
@jwt_required()
def get_failure_analysis():
    """Başarısız erişim analizi"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        if not current_user or not current_user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if start_date:
            start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        if end_date:
            end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        failures = analytics_service.get_failed_access_analysis(start_date, end_date)
        
        return jsonify({
            'failures': failures,
            'total_count': len(failures)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get failure analysis', 'details': str(e)}), 500

@analytics_bp.route('/turn-aways', methods=['GET'])
@jwt_required()
def get_turn_away_analysis():
    """Erişim reddi analizi (Turn-away analysis)"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        if not current_user or not current_user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if start_date:
            start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        if end_date:
            end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        turn_aways = analytics_service.get_turn_away_analysis(start_date, end_date)
        
        return jsonify({
            'turn_aways': turn_aways,
            'total_count': len(turn_aways)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get turn-away analysis', 'details': str(e)}), 500

@analytics_bp.route('/breakdown', methods=['GET'])
@jwt_required()
def get_breakdown_report():
    """Özelleştirilebilir kırılım raporu"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        if not current_user or not current_user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        
        breakdown_field = request.args.get('field')
        if not breakdown_field:
            return jsonify({'error': 'Breakdown field is required'}), 400
        
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if start_date:
            start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        if end_date:
            end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        breakdown = analytics_service.get_custom_breakdown_report(
            breakdown_field, start_date, end_date
        )
        
        return jsonify({
            'breakdown': breakdown,
            'field': breakdown_field,
            'total_count': len(breakdown)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get breakdown report', 'details': str(e)}), 500

@analytics_bp.route('/logs', methods=['GET'])
@jwt_required()
def get_analytics_logs():
    """Detaylı analitik logları"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        if not current_user or not current_user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        user_id = request.args.get('user_id')
        resource_name = request.args.get('resource_name')
        
        query = AnalyticsLog.query
        
        if start_date:
            start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            query = query.filter(AnalyticsLog.access_timestamp >= start_date)
        if end_date:
            end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            query = query.filter(AnalyticsLog.access_timestamp <= end_date)
        if user_id:
            query = query.filter(AnalyticsLog.user_id == user_id)
        if resource_name:
            query = query.filter(AnalyticsLog.resource_name.ilike(f'%{resource_name}%'))
        
        logs = query.order_by(desc(AnalyticsLog.access_timestamp)).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'logs': [log.to_dict() for log in logs.items],
            'pagination': {
                'page': logs.page,
                'pages': logs.pages,
                'per_page': logs.per_page,
                'total': logs.total,
                'has_next': logs.has_next,
                'has_prev': logs.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get analytics logs', 'details': str(e)}), 500

@analytics_bp.route('/export', methods=['GET'])
@jwt_required()
def export_analytics_data():
    """Analitik verileri CSV formatında export"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        if not current_user or not current_user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        
        report_type = request.args.get('type', 'usage')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if start_date:
            start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        if end_date:
            end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        # Bu endpoint CSV export için hazırlanabilir
        # Şimdilik JSON formatında döndürüyoruz
        if report_type == 'usage':
            data = analytics_service.get_usage_statistics(start_date, end_date)
        elif report_type == 'resources':
            data = analytics_service.get_resource_usage_report(start_date, end_date)
        elif report_type == 'users':
            data = analytics_service.get_user_activity_report(start_date, end_date)
        else:
            data = analytics_service.get_usage_statistics(start_date, end_date)
        
        return jsonify({
            'data': data,
            'export_type': report_type,
            'exported_at': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to export analytics data', 'details': str(e)}), 500
