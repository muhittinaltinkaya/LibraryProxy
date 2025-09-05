from app.models.user import User
from app import db

class AuthService:
    """Authentication service for user management"""
    
    def authenticate_user(self, username, password):
        """Authenticate user with username/email and password"""
        # Try to find user by username or email
        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()
        
        if user and user.check_password(password):
            return user
        
        return None
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        return User.query.get(user_id)
    
    def get_user_by_username(self, username):
        """Get user by username"""
        return User.query.filter_by(username=username).first()
    
    def get_user_by_email(self, email):
        """Get user by email"""
        return User.query.filter_by(email=email).first()
    
    def create_user(self, username, email, password, first_name, last_name, is_admin=False):
        """Create a new user"""
        user = User(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_admin=is_admin
        )
        
        db.session.add(user)
        db.session.commit()
        
        return user
    
    def update_user(self, user_id, **kwargs):
        """Update user information"""
        user = self.get_user_by_id(user_id)
        
        if not user:
            return None
        
        # Update allowed fields
        allowed_fields = ['first_name', 'last_name', 'email', 'is_active', 'is_admin']
        for field, value in kwargs.items():
            if field in allowed_fields and hasattr(user, field):
                setattr(user, field, value)
        
        db.session.commit()
        return user
    
    def deactivate_user(self, user_id):
        """Deactivate user account"""
        user = self.get_user_by_id(user_id)
        
        if not user:
            return None
        
        user.is_active = False
        db.session.commit()
        
        return user
    
    def activate_user(self, user_id):
        """Activate user account"""
        user = self.get_user_by_id(user_id)
        
        if not user:
            return None
        
        user.is_active = True
        db.session.commit()
        
        return user
