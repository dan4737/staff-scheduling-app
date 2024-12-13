from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), nullable=False)  # 'manager' or 'staff'
    staff_id = db.Column(db.String(20), unique=True, nullable=True)  # Only for staff members
    phone = db.Column(db.String(20), nullable=True)  # Add phone field
    is_active = db.Column(db.Boolean, default=True)  # Add is_active field
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_manager(self):
        return self.role == 'manager'
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'staff_id': self.staff_id,
            'phone': self.phone,
            'is_active': self.is_active
        }
