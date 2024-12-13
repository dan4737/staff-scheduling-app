from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.schedule import Schedule
from app.models.user import User
from app import db
from datetime import datetime

schedules_bp = Blueprint('schedules', __name__)

@schedules_bp.route('/schedules', methods=['POST'])
@jwt_required()
def create_schedule():
    current_user = User.query.get(get_jwt_identity())
    if current_user.role != 'manager':
        return jsonify({'message': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    schedule = Schedule(
        staff_id=data['staff_id'],
        date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
        start_time=datetime.strptime(data['start_time'], '%H:%M').time(),
        end_time=datetime.strptime(data['end_time'], '%H:%M').time(),
        break_start=datetime.strptime(data['break_start'], '%H:%M').time() if data.get('break_start') else None,
        break_end=datetime.strptime(data['break_end'], '%H:%M').time() if data.get('break_end') else None,
        published=data.get('published', False)
    )
    
    db.session.add(schedule)
    db.session.commit()
    
    return jsonify({'message': 'Schedule created successfully', 'schedule': schedule.to_dict()}), 201

@schedules_bp.route('/schedules/<int:schedule_id>', methods=['PUT'])
@jwt_required()
def update_schedule(schedule_id):
    current_user = User.query.get(get_jwt_identity())
    if current_user.role != 'manager':
        return jsonify({'message': 'Unauthorized'}), 403
    
    schedule = Schedule.query.get_or_404(schedule_id)
    data = request.get_json()
    
    schedule.date = datetime.strptime(data['date'], '%Y-%m-%d').date()
    schedule.start_time = datetime.strptime(data['start_time'], '%H:%M').time()
    schedule.end_time = datetime.strptime(data['end_time'], '%H:%M').time()
    schedule.break_start = datetime.strptime(data['break_start'], '%H:%M').time() if data.get('break_start') else None
    schedule.break_end = datetime.strptime(data['break_end'], '%H:%M').time() if data.get('break_end') else None
    schedule.published = data.get('published', schedule.published)
    
    db.session.commit()
    
    return jsonify({'message': 'Schedule updated successfully', 'schedule': schedule.to_dict()}), 200

@schedules_bp.route('/schedules/<int:schedule_id>', methods=['DELETE'])
@jwt_required()
def delete_schedule(schedule_id):
    current_user = User.query.get(get_jwt_identity())
    if current_user.role != 'manager':
        return jsonify({'message': 'Unauthorized'}), 403
    
    schedule = Schedule.query.get_or_404(schedule_id)
    db.session.delete(schedule)
    db.session.commit()
    
    return jsonify({'message': 'Schedule deleted successfully'}), 200

@schedules_bp.route('/schedules', methods=['GET'])
@jwt_required()
def get_schedules():
    current_user = User.query.get(get_jwt_identity())
    
    if current_user.role == 'manager':
        schedules = Schedule.query.all()
    else:
        schedules = Schedule.query.filter_by(staff_id=current_user.id, published=True).all()
    
    return jsonify({
        'schedules': [schedule.to_dict() for schedule in schedules]
    }), 200
