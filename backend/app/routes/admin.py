from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db, limiter
from app.models.user import User
from app.models.journal import Journal
from app.models.proxy_config import ProxyConfig
from app.models.access_log import AccessLog
from app.services.journal_service import JournalService
from app.services.proxy_service import ProxyService
from app.utils.validators import validate_journal_slug, validate_url, sanitize_string, validate_password

admin_bp = Blueprint('admin', __name__)
journal_service = JournalService()
proxy_service = ProxyService()

def admin_required(f):
    """Decorator to require admin access"""
    def decorated_function(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or not user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        
        return f(*args, **kwargs)
    
    decorated_function.__name__ = f.__name__
    return decorated_function

@admin_bp.route('/users', methods=['GET', 'POST'])
@jwt_required()
@admin_required
def get_users():
    """Get all users or create new user (admin only)"""
    if request.method == 'GET':
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            search = request.args.get('search', '')
            
            query = User.query
            
            if search:
                query = query.filter(
                    User.username.ilike(f'%{search}%') |
                    User.email.ilike(f'%{search}%') |
                    User.first_name.ilike(f'%{search}%') |
                    User.last_name.ilike(f'%{search}%')
                )
            
            users = query.paginate(page=page, per_page=per_page, error_out=False)
            
            return jsonify({
                'users': [user.to_dict() for user in users.items],
                'pagination': {
                    'page': users.page,
                    'pages': users.pages,
                    'per_page': users.per_page,
                    'total': users.total,
                    'has_next': users.has_next,
                    'has_prev': users.has_prev
                }
            }), 200
            
        except Exception as e:
            return jsonify({'error': 'Failed to get users', 'details': str(e)}), 500
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            # Validate required fields
            required_fields = ['username', 'email', 'password']
            for field in required_fields:
                if not data.get(field):
                    return jsonify({'error': f'{field} is required'}), 400
            
            # Check if username already exists
            if User.query.filter_by(username=data['username']).first():
                return jsonify({'error': 'Username already exists'}), 400
            
            # Check if email already exists
            if User.query.filter_by(email=data['email']).first():
                return jsonify({'error': 'Email already exists'}), 400
            
            # Create new user
            user = User(
                username=data['username'],
                email=data['email'],
                password=data['password'],
                first_name=data.get('first_name', ''),
                last_name=data.get('last_name', ''),
                is_admin=data.get('is_admin', False),
                is_active=data.get('is_active', True)
            )
            
            db.session.add(user)
            db.session.commit()
            
            return jsonify({
                'message': 'User created successfully',
                'user': user.to_dict()
            }), 201
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Failed to create user', 'details': str(e)}), 500

@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_user(user_id):
    """Update user (admin only)"""
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update allowed fields
        allowed_fields = ['first_name', 'last_name', 'email', 'is_active', 'is_admin']
        for field, value in data.items():
            if field in allowed_fields and hasattr(user, field):
                setattr(user, field, value)
        
        db.session.commit()
        
        return jsonify({
            'message': 'User updated successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update user', 'details': str(e)}), 500

@admin_bp.route('/journals', methods=['GET'])
@jwt_required()
@admin_required
def get_journals():
    """Get list of journals (admin only)"""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')
        subject_area = request.args.get('subject_area', '')
        access_level = request.args.get('access_level', '')
        
        # Build query
        query = Journal.query
        
        # Apply filters
        if search:
            query = query.filter(
                Journal.name.ilike(f'%{search}%') |
                Journal.description.ilike(f'%{search}%') |
                Journal.publisher.ilike(f'%{search}%')
            )
        
        if subject_area:
            query = query.filter(Journal.subject_areas.contains([subject_area]))
        
        if access_level:
            query = query.filter(Journal.access_level == access_level)
        
        # Paginate results
        journals = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return jsonify({
            'journals': [journal.to_dict() for journal in journals.items],
            'pagination': {
                'page': journals.page,
                'pages': journals.pages,
                'per_page': journals.per_page,
                'total': journals.total,
                'has_next': journals.has_next,
                'has_prev': journals.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get journals', 'details': str(e)}), 500

@admin_bp.route('/journals', methods=['POST'])
@jwt_required()
@admin_required
def create_journal():
    """Create new journal (admin only)"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['name', 'slug', 'base_url', 'proxy_path']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Validate slug
        slug_validation = validate_journal_slug(data['slug'])
        if not slug_validation['valid']:
            return jsonify({'error': slug_validation['message']}), 400
        
        # Validate URL
        if not validate_url(data['base_url']):
            return jsonify({'error': 'Invalid base URL format'}), 400
        
        # Check if slug already exists
        if Journal.query.filter_by(slug=data['slug']).first():
            return jsonify({'error': 'Slug already exists'}), 409
        
        # Check if proxy_path already exists
        if Journal.query.filter_by(proxy_path=data['proxy_path']).first():
            return jsonify({'error': 'Proxy path already exists'}), 409
        
        # Create journal
        journal = journal_service.create_journal(
            name=sanitize_string(data['name'], 200),
            slug=data['slug'],
            base_url=data['base_url'],
            proxy_path=data['proxy_path'],
            description=sanitize_string(data.get('description', ''), 1000),
            publisher=sanitize_string(data.get('publisher', ''), 200),
            issn=data.get('issn', ''),
            e_issn=data.get('e_issn', ''),
            subject_areas=data.get('subject_areas', []),
            access_level=data.get('access_level', 'public'),
            requires_auth=data.get('requires_auth', True),
            auth_method=data.get('auth_method', 'ip'),
            custom_headers=data.get('custom_headers', {}),
            timeout=data.get('timeout', 30)
        )
        
        return jsonify({
            'message': 'Journal created successfully',
            'journal': journal.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create journal', 'details': str(e)}), 500

@admin_bp.route('/journals/<int:journal_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_journal(journal_id):
    """Update journal (admin only)"""
    try:
        journal = Journal.query.get(journal_id)
        
        if not journal:
            return jsonify({'error': 'Journal not found'}), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate slug if provided
        if 'slug' in data:
            slug_validation = validate_journal_slug(data['slug'])
            if not slug_validation['valid']:
                return jsonify({'error': slug_validation['message']}), 400
            
            # Check if slug already exists (excluding current journal)
            existing = Journal.query.filter_by(slug=data['slug']).first()
            if existing and existing.id != journal_id:
                return jsonify({'error': 'Slug already exists'}), 409
        
        # Validate URL if provided
        if 'base_url' in data and not validate_url(data['base_url']):
            return jsonify({'error': 'Invalid base URL format'}), 400
        
        # Update journal
        updated_journal = journal_service.update_journal(journal_id, **data)
        
        if not updated_journal:
            return jsonify({'error': 'Failed to update journal'}), 500
        
        return jsonify({
            'message': 'Journal updated successfully',
            'journal': updated_journal.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update journal', 'details': str(e)}), 500

@admin_bp.route('/journals/<int:journal_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_journal(journal_id):
    """Delete journal (admin only)"""
    try:
        journal = Journal.query.get(journal_id)
        
        if not journal:
            return jsonify({'error': 'Journal not found'}), 404
        
        # Soft delete
        deleted_journal = journal_service.delete_journal(journal_id)
        
        if not deleted_journal:
            return jsonify({'error': 'Failed to delete journal'}), 500
        
        return jsonify({
            'message': 'Journal deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete journal', 'details': str(e)}), 500

@admin_bp.route('/stats', methods=['GET'])
@jwt_required()
@admin_required
def get_admin_stats():
    """Get admin statistics"""
    try:
        # User statistics
        total_users = User.query.count()
        active_users = User.query.filter_by(is_active=True).count()
        admin_users = User.query.filter_by(is_admin=True).count()
        
        # Journal statistics
        total_journals = Journal.query.count()
        active_journals = Journal.query.filter_by(is_active=True).count()
        
        # Proxy configuration statistics
        total_configs = ProxyConfig.query.count()
        active_configs = ProxyConfig.query.filter_by(is_active=True).count()
        
        # Access log statistics
        total_access_logs = AccessLog.query.count()
        
        # Recent activity
        recent_logs = AccessLog.query.order_by(AccessLog.timestamp.desc()).limit(10).all()
        
        return jsonify({
            'users': {
                'total': total_users,
                'active': active_users,
                'admins': admin_users
            },
            'journals': {
                'total': total_journals,
                'active': active_journals
            },
            'proxy_configs': {
                'total': total_configs,
                'active': active_configs
            },
            'access_logs': {
                'total': total_access_logs
            },
            'recent_activity': [log.to_dict() for log in recent_logs]
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get admin stats', 'details': str(e)}), 500

@admin_bp.route('/access-logs', methods=['GET'])
@jwt_required()
@admin_required
def get_access_logs():
    """Get access logs (admin only)"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        user_id = request.args.get('user_id', type=int)
        journal_id = request.args.get('journal_id', type=int)
        
        query = AccessLog.query
        
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        if journal_id:
            query = query.filter_by(journal_id=journal_id)
        
        logs = query.order_by(AccessLog.timestamp.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
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
        return jsonify({'error': 'Failed to get access logs', 'details': str(e)}), 500

@admin_bp.route('/users/<int:user_id>/password', methods=['PUT'])
@jwt_required()
def update_user_password(user_id):
    """Update user password (admin only)"""
    try:
        # Check if current user is admin
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        if not current_user or not current_user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        new_password = data.get('password')
        if not new_password:
            return jsonify({'error': 'Password is required'}), 400
        
        # Validate password strength
        password_validation = validate_password(new_password)
        if not password_validation['valid']:
            return jsonify({'error': password_validation['message']}), 400
        
        # Get target user
        target_user = User.query.get(user_id)
        if not target_user:
            return jsonify({'error': 'User not found'}), 404
        
        # Update password
        target_user.set_password(new_password)
        db.session.commit()
        
        return jsonify({
            'message': 'Password updated successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update password', 'details': str(e)}), 500
