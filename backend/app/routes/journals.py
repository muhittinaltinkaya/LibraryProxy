from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db, limiter
from app.models.journal import Journal
from app.models.user import User
from app.services.journal_service import JournalService
from app.utils.validators import validate_journal_slug, validate_url, sanitize_string

journals_bp = Blueprint('journals', __name__)
journal_service = JournalService()

@journals_bp.route('', methods=['GET'])
@jwt_required()
def get_journals():
    """Get list of available journals"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')
        subject_area = request.args.get('subject_area', '')
        access_level = request.args.get('access_level', '')
        
        # Build query
        query = Journal.query.filter_by(is_active=True)
        
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

@journals_bp.route('/<int:journal_id>', methods=['GET'])
@jwt_required()
def get_journal(journal_id):
    """Get specific journal details"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        journal = Journal.query.get(journal_id)
        
        if not journal:
            return jsonify({'error': 'Journal not found'}), 404
        
        if not journal.is_active:
            return jsonify({'error': 'Journal is not available'}), 403
        
        return jsonify({
            'journal': journal.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get journal', 'details': str(e)}), 500

@journals_bp.route('/<int:journal_id>/access', methods=['POST'])
@jwt_required()
@limiter.limit("10 per minute")
def request_access(journal_id):
    """Request access to a journal"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        journal = Journal.query.get(journal_id)
        
        if not journal:
            return jsonify({'error': 'Journal not found'}), 404
        
        if not journal.is_active:
            return jsonify({'error': 'Journal is not available'}), 403
        
        # Check access level
        if journal.access_level == 'admin' and not user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        
        # Generate proxy configuration
        proxy_config = journal_service.generate_proxy_config(journal, user)
        
        if not proxy_config:
            return jsonify({'error': 'Failed to generate proxy configuration'}), 500
        
        # Generate access URL
        access_url = journal.get_proxy_url(request.host)
        
        return jsonify({
            'message': 'Access granted',
            'journal': journal.to_dict(),
            'access_url': access_url,
            'proxy_config': proxy_config.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to request access', 'details': str(e)}), 500

@journals_bp.route('/<int:journal_id>/proxy-url', methods=['GET'])
@jwt_required()
def get_proxy_url(journal_id):
    """Get proxy URL for journal access"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        journal = Journal.query.get(journal_id)
        
        if not journal:
            return jsonify({'error': 'Journal not found'}), 404
        
        if not journal.is_active:
            return jsonify({'error': 'Journal is not available'}), 403
        
        # Generate proxy URL
        proxy_url = journal.get_proxy_url(request.host)
        
        return jsonify({
            'proxy_url': proxy_url,
            'journal': {
                'id': journal.id,
                'name': journal.name,
                'slug': journal.slug
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get proxy URL', 'details': str(e)}), 500

@journals_bp.route('/search', methods=['GET'])
@jwt_required()
def search_journals():
    """Search journals with advanced filters"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get search parameters
        query_text = request.args.get('q', '')
        publisher = request.args.get('publisher', '')
        issn = request.args.get('issn', '')
        subject_areas = request.args.getlist('subject_areas')
        access_level = request.args.get('access_level', '')
        
        # Build search query
        query = Journal.query.filter_by(is_active=True)
        
        if query_text:
            query = query.filter(
                Journal.name.ilike(f'%{query_text}%') |
                Journal.description.ilike(f'%{query_text}%') |
                Journal.publisher.ilike(f'%{query_text}%')
            )
        
        if publisher:
            query = query.filter(Journal.publisher.ilike(f'%{publisher}%'))
        
        if issn:
            query = query.filter(
                (Journal.issn == issn) | (Journal.e_issn == issn)
            )
        
        if subject_areas:
            for subject in subject_areas:
                query = query.filter(Journal.subject_areas.contains([subject]))
        
        if access_level:
            query = query.filter(Journal.access_level == access_level)
        
        # Execute query
        journals = query.limit(50).all()
        
        return jsonify({
            'journals': [journal.to_dict() for journal in journals],
            'total': len(journals)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to search journals', 'details': str(e)}), 500

@journals_bp.route('/subject-areas', methods=['GET'])
@jwt_required()
def get_subject_areas():
    """Get list of available subject areas"""
    try:
        # Get all unique subject areas from journals
        journals = Journal.query.filter_by(is_active=True).all()
        subject_areas = set()
        
        for journal in journals:
            if journal.subject_areas:
                subject_areas.update(journal.subject_areas)
        
        return jsonify({
            'subject_areas': sorted(list(subject_areas))
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get subject areas', 'details': str(e)}), 500
