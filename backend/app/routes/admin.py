from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.models.user import User
from app.models.schedule import Schedule
from app import db
from datetime import datetime

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    if not current_user.role == 'manager':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.index'))
    
    staff_count = User.query.filter(User.role != 'manager').count()
    schedule_count = Schedule.query.count()
    pending_count = 0  # You can implement this based on your requirements
    
    return render_template('admin/dashboard.html', 
                         staff_count=staff_count,
                         schedule_count=schedule_count,
                         pending_count=pending_count)

@admin_bp.route('/staff', methods=['GET'])
@login_required
def manage_staff():
    if not current_user.role == 'manager':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.index'))
    
    staff = User.query.filter(User.role != 'manager').all()
    return render_template('admin/staff.html', staff=staff)

@admin_bp.route('/staff/add', methods=['POST'])
@login_required
def add_staff():
    if not current_user.role == 'manager':
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    phone = data.get('phone')
    
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    new_staff = User(
        username=username,
        email=email,
        phone=phone,
        role='staff',
        is_active=True
    )
    new_staff.set_password(password)
    
    db.session.add(new_staff)
    db.session.commit()
    
    return jsonify({
        'message': 'Staff member added successfully',
        'staff': {
            'id': new_staff.id,
            'username': new_staff.username,
            'email': new_staff.email,
            'phone': new_staff.phone,
            'is_active': new_staff.is_active
        }
    })

@admin_bp.route('/staff/<int:staff_id>', methods=['PUT'])
@login_required
def update_staff(staff_id):
    if not current_user.role == 'manager':
        return jsonify({'error': 'Access denied'}), 403
    
    staff = User.query.get_or_404(staff_id)
    data = request.json
    
    if 'username' in data and data['username'] != staff.username:
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already exists'}), 400
        staff.username = data['username']
    
    if 'email' in data and data['email'] != staff.email:
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 400
        staff.email = data['email']
    
    if 'phone' in data:
        staff.phone = data['phone']
    
    if 'is_active' in data:
        staff.is_active = data['is_active']
    
    if 'password' in data and data['password']:
        staff.set_password(data['password'])
    
    db.session.commit()
    
    return jsonify({
        'message': 'Staff member updated successfully',
        'staff': {
            'id': staff.id,
            'username': staff.username,
            'email': staff.email,
            'phone': staff.phone,
            'is_active': staff.is_active
        }
    })

@admin_bp.route('/staff/<int:staff_id>', methods=['DELETE'])
@login_required
def delete_staff(staff_id):
    if not current_user.role == 'manager':
        return jsonify({'error': 'Access denied'}), 403
    
    staff = User.query.get_or_404(staff_id)
    db.session.delete(staff)
    db.session.commit()
    
    return jsonify({'message': 'Staff member deleted successfully'})

@admin_bp.route('/schedules', methods=['GET'])
@login_required
def manage_schedules():
    if not current_user.role == 'manager':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.index'))
    
    schedules = Schedule.query.all()
    staff = User.query.filter(User.role != 'manager').all()
    return render_template('admin/schedules.html', schedules=schedules, staff=staff)

@admin_bp.route('/schedules/view', methods=['GET'])
@login_required
def view_schedules():
    if not current_user.role == 'manager':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.index'))
    
    # Get all schedules ordered by date and start time
    schedules = Schedule.query.order_by(Schedule.date.asc(), Schedule.start_time.asc()).all()
    return render_template('admin/schedule_view.html', schedules=schedules)

@admin_bp.route('/schedules/add', methods=['POST'])
@login_required
def add_schedule():
    if not current_user.role == 'manager':
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        staff_id = request.form.get('staff_id')
        date = datetime.strptime(request.form.get('date'), '%Y-%m-%d').date()
        start_time = datetime.strptime(request.form.get('start_time'), '%H:%M').time()
        end_time = datetime.strptime(request.form.get('end_time'), '%H:%M').time()
        break_start = datetime.strptime(request.form.get('break_start'), '%H:%M').time() if request.form.get('break_start') else None
        break_end = datetime.strptime(request.form.get('break_end'), '%H:%M').time() if request.form.get('break_end') else None
        
        # Combine date and time
        start_datetime = datetime.combine(date, start_time)
        end_datetime = datetime.combine(date, end_time)
        break_start_datetime = datetime.combine(date, break_start) if break_start else None
        break_end_datetime = datetime.combine(date, break_end) if break_end else None
        
        new_schedule = Schedule(
            staff_id=staff_id,
            date=date,
            start_time=start_datetime,
            end_time=end_datetime,
            break_start=break_start_datetime,
            break_end=break_end_datetime
        )
        
        db.session.add(new_schedule)
        db.session.commit()
        
        flash('Schedule created successfully!', 'success')
        return redirect(url_for('admin.manage_schedules'))
        
    except Exception as e:
        flash(f'Error creating schedule: {str(e)}', 'error')
        return redirect(url_for('admin.manage_schedules'))

@admin_bp.route('/schedules/update/<int:schedule_id>', methods=['POST'])
@login_required
def update_schedule(schedule_id):
    if not current_user.role == 'manager':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.index'))
    
    try:
        schedule = Schedule.query.get_or_404(schedule_id)
        
        date = datetime.strptime(request.form.get('date'), '%Y-%m-%d').date()
        start_time = datetime.strptime(request.form.get('start_time'), '%H:%M').time()
        end_time = datetime.strptime(request.form.get('end_time'), '%H:%M').time()
        break_start = datetime.strptime(request.form.get('break_start'), '%H:%M').time() if request.form.get('break_start') else None
        break_end = datetime.strptime(request.form.get('break_end'), '%H:%M').time() if request.form.get('break_end') else None
        
        # Combine date and time
        schedule.date = date
        schedule.start_time = datetime.combine(date, start_time)
        schedule.end_time = datetime.combine(date, end_time)
        schedule.break_start = datetime.combine(date, break_start) if break_start else None
        schedule.break_end = datetime.combine(date, break_end) if break_end else None
        schedule.staff_id = request.form.get('staff_id')
        
        db.session.commit()
        flash('Schedule updated successfully!', 'success')
        return redirect(url_for('admin.manage_schedules'))
        
    except Exception as e:
        flash(f'Error updating schedule: {str(e)}', 'error')
        return redirect(url_for('admin.manage_schedules'))

@admin_bp.route('/schedules/delete/<int:schedule_id>', methods=['POST'])
@login_required
def delete_schedule(schedule_id):
    if not current_user.role == 'manager':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.index'))
    
    try:
        schedule = Schedule.query.get_or_404(schedule_id)
        db.session.delete(schedule)
        db.session.commit()
        flash('Schedule deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting schedule: {str(e)}', 'error')
    
    return redirect(url_for('admin.manage_schedules'))
