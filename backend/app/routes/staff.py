from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app import db

staff_bp = Blueprint('staff', __name__)

@staff_bp.route('/staff', methods=['GET'])
@jwt_required()
def get_staff():
    current_user = User.query.get(get_jwt_identity())
    if current_user.role != 'manager':
        return jsonify({'message': 'Unauthorized'}), 403
    
    staff = User.query.filter_by(role='staff').all()
    return jsonify({
        'staff': [user.to_dict() for user in staff]
    }), 200

@staff_bp.route('/staff/<int:staff_id>', methods=['PUT'])
@jwt_required()
def update_staff(staff_id):
    current_user = User.query.get(get_jwt_identity())
    if current_user.role != 'manager':
        return jsonify({'message': 'Unauthorized'}), 403
    
    staff = User.query.get_or_404(staff_id)
    if staff.role != 'staff':
        return jsonify({'message': 'Not a staff member'}), 400
    
    data = request.get_json()
    
    if 'username' in data and data['username'] != staff.username:
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'message': 'Username already exists'}), 400
        staff.username = data['username']
    
    if 'email' in data and data['email'] != staff.email:
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'message': 'Email already exists'}), 400
        staff.email = data['email']
    
    if 'password' in data:
        staff.set_password(data['password'])
    
    if 'staff_id' in data:
        staff.staff_id = data['staff_id']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Staff member updated successfully',
        'staff': staff.to_dict()
    }), 200

@staff_bp.route('/staff/<int:staff_id>', methods=['DELETE'])
@jwt_required()
def delete_staff(staff_id):
    current_user = User.query.get(get_jwt_identity())
    if current_user.role != 'manager':
        return jsonify({'message': 'Unauthorized'}), 403
    
    staff = User.query.get_or_404(staff_id)
    if staff.role != 'staff':
        return jsonify({'message': 'Not a staff member'}), 400
    
    db.session.delete(staff)
    db.session.commit()
    
    return jsonify({'message': 'Staff member deleted successfully'}), 200
