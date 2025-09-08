from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db, limiter
from app.models.user import User
from app.models.journal import Journal
from app.models.proxy_config import ProxyConfig
from app.services.proxy_service import ProxyService
from app.services.journal_service import JournalService

proxy_bp = Blueprint('proxy', __name__)
proxy_service = ProxyService()
journal_service = JournalService()

@proxy_bp.route('/generate', methods=['POST'])
@jwt_required()
@limiter.limit("5 per minute")
def generate_proxy_config():
    """Generate new proxy configuration"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        journal_id = data.get('journal_id')
        
        if not journal_id:
            return jsonify({'error': 'Journal ID is required'}), 400
        
        journal = Journal.query.get(journal_id)
        
        if not journal:
            return jsonify({'error': 'Journal not found'}), 404
        
        if not journal.is_active:
            return jsonify({'error': 'Journal is not available'}), 403
        
        # Generate proxy configuration
        proxy_config = journal_service.generate_proxy_config(journal, user)
        
        if not proxy_config:
            return jsonify({'error': 'Failed to generate proxy configuration'}), 500
        
        return jsonify({
            'message': 'Proxy configuration generated successfully',
            'config': proxy_config.to_dict(),
            'access_url': journal.get_proxy_url(request.host)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to generate proxy configuration', 'details': str(e)}), 500

@proxy_bp.route('/<int:config_id>', methods=['DELETE'])
@jwt_required()
def remove_proxy_config(config_id):
    """Remove proxy configuration"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        proxy_config = ProxyConfig.query.get(config_id)
        
        if not proxy_config:
            return jsonify({'error': 'Proxy configuration not found'}), 404
        
        # Check if user owns this config or is admin
        if proxy_config.user_id != user_id and not user.is_admin:
            return jsonify({'error': 'Access denied'}), 403
        
        # Remove configuration
        success = proxy_service.remove_proxy_config(proxy_config)
        
        if not success:
            return jsonify({'error': 'Failed to remove proxy configuration'}), 500
        
        # Delete from database
        db.session.delete(proxy_config)
        db.session.commit()
        
        return jsonify({
            'message': 'Proxy configuration removed successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to remove proxy configuration', 'details': str(e)}), 500

@proxy_bp.route('/status', methods=['GET'])
@jwt_required()
def get_proxy_status():
    """Get proxy service status"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get proxy status
        status = proxy_service.get_config_status()
        
        # Get user's active configurations
        user_configs = ProxyConfig.query.filter_by(
            user_id=user_id,
            is_active=True
        ).all()
        
        return jsonify({
            'proxy_status': status,
            'user_configs': [config.to_dict() for config in user_configs]
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get proxy status', 'details': str(e)}), 500

@proxy_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_proxy_stats():
    """Get HAProxy statistics"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Only admins can view detailed stats
        if not user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        
        stats = proxy_service.get_haproxy_stats()
        
        return jsonify({
            'haproxy_stats': stats
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get proxy stats', 'details': str(e)}), 500

@proxy_bp.route('/cleanup', methods=['POST'])
@jwt_required()
def cleanup_expired_configs():
    """Clean up expired proxy configurations"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Only admins can cleanup
        if not user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        
        cleaned_count = proxy_service.cleanup_expired_configs()
        
        return jsonify({
            'message': f'Cleaned up {cleaned_count} expired configurations'
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to cleanup configurations', 'details': str(e)}), 500

@proxy_bp.route('/reload', methods=['POST'])
@jwt_required()
def reload_proxy():
    """Reload HAProxy configuration with dynamic journal configurations"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Only admins can reload
        if not user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        
        # Update HAProxy configuration with all active journals
        success = proxy_service.update_main_haproxy_config()
        
        if not success:
            return jsonify({'error': 'Failed to update HAProxy configuration'}), 500
        
        # Reload HAProxy
        reload_success = proxy_service.reload_haproxy()
        
        if not reload_success:
            return jsonify({'error': 'HAProxy configuration updated but reload failed'}), 500
        
        return jsonify({
            'message': 'HAProxy configuration dynamically updated and reloaded successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to reload HAProxy', 'details': str(e)}), 500

@proxy_bp.route('/configs', methods=['GET'])
@jwt_required()
def get_user_configs():
    """Get user's proxy configurations"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Get user's configurations
        configs = ProxyConfig.query.filter_by(user_id=user_id)\
            .order_by(ProxyConfig.created_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'configs': [config.to_dict() for config in configs.items],
            'pagination': {
                'page': configs.page,
                'pages': configs.pages,
                'per_page': configs.per_page,
                'total': configs.total,
                'has_next': configs.has_next,
                'has_prev': configs.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get configurations', 'details': str(e)}), 500
