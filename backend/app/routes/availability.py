from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models.availability import Availability, TimeOffRequest, ShiftTrade, Overtime
from app.models.schedule import Schedule
from datetime import datetime, time

availability_bp = Blueprint('availability', __name__)

@availability_bp.route('/availability', methods=['GET', 'POST'])
@login_required
def manage_availability():
    if request.method == 'POST':
        # Clear existing availability
        Availability.query.filter_by(staff_id=current_user.id).delete()
        
        # Add new availability
        for day in range(7):  # 0-6 for Monday-Sunday
            start_time = request.form.get(f'start_time_{day}')
            end_time = request.form.get(f'end_time_{day}')
            
            if start_time and end_time:
                start = datetime.strptime(start_time, '%H:%M').time()
                end = datetime.strptime(end_time, '%H:%M').time()
                
                availability = Availability(
                    staff_id=current_user.id,
                    day_of_week=day,
                    start_time=start,
                    end_time=end
                )
                db.session.add(availability)
        
        db.session.commit()
        flash('Availability updated successfully', 'success')
        return redirect(url_for('availability.manage_availability'))
    
    availabilities = {a.day_of_week: a for a in current_user.availabilities}
    return render_template('availability/manage.html', availabilities=availabilities)

@availability_bp.route('/time-off', methods=['GET', 'POST'])
@login_required
def request_time_off():
    if request.method == 'POST':
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()
        reason = request.form.get('reason', '')
        
        request = TimeOffRequest(
            staff_id=current_user.id,
            start_date=start_date,
            end_date=end_date,
            reason=reason
        )
        db.session.add(request)
        db.session.commit()
        
        flash('Time-off request submitted successfully', 'success')
        return redirect(url_for('availability.request_time_off'))
    
    requests = TimeOffRequest.query.filter_by(staff_id=current_user.id).order_by(TimeOffRequest.created_at.desc()).all()
    return render_template('availability/time_off.html', requests=requests)

@availability_bp.route('/shift-trade', methods=['GET', 'POST'])
@login_required
def request_shift_trade():
    if request.method == 'POST':
        schedule_id = request.form.get('schedule_id')
        target_staff_id = request.form.get('target_staff_id')
        
        trade = ShiftTrade(
            schedule_id=schedule_id,
            requesting_staff_id=current_user.id,
            target_staff_id=target_staff_id
        )
        db.session.add(trade)
        db.session.commit()
        
        flash('Shift trade request submitted successfully', 'success')
        return redirect(url_for('availability.request_shift_trade'))
    
    # Get current user's schedules and other staff members
    schedules = Schedule.query.filter_by(staff_id=current_user.id).all()
    trades = ShiftTrade.query.filter(
        (ShiftTrade.requesting_staff_id == current_user.id) |
        (ShiftTrade.target_staff_id == current_user.id)
    ).order_by(ShiftTrade.created_at.desc()).all()
    
    return render_template('availability/shift_trade.html', schedules=schedules, trades=trades)

@availability_bp.route('/overtime', methods=['GET', 'POST'])
@login_required
def log_overtime():
    if request.method == 'POST':
        schedule_id = request.form.get('schedule_id')
        start_time = datetime.strptime(f"{request.form['date']} {request.form['start_time']}", '%Y-%m-%d %H:%M')
        end_time = datetime.strptime(f"{request.form['date']} {request.form['end_time']}", '%Y-%m-%d %H:%M')
        reason = request.form.get('reason', '')
        
        overtime = Overtime(
            schedule_id=schedule_id,
            staff_id=current_user.id,
            start_time=start_time,
            end_time=end_time,
            reason=reason
        )
        db.session.add(overtime)
        db.session.commit()
        
        flash('Overtime logged successfully', 'success')
        return redirect(url_for('availability.log_overtime'))
    
    schedules = Schedule.query.filter_by(staff_id=current_user.id).all()
    overtimes = Overtime.query.filter_by(staff_id=current_user.id).order_by(Overtime.created_at.desc()).all()
    return render_template('availability/overtime.html', schedules=schedules, overtimes=overtimes)

# Admin routes for managing requests
@availability_bp.route('/admin/time-off', methods=['GET'])
@login_required
def manage_time_off_requests():
    if not current_user.role == 'manager':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.index'))
    
    requests = TimeOffRequest.query.order_by(TimeOffRequest.created_at.desc()).all()
    return render_template('admin/time_off_requests.html', requests=requests)

@availability_bp.route('/admin/shift-trades', methods=['GET'])
@login_required
def manage_shift_trades():
    if not current_user.role == 'manager':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.index'))
    
    trades = ShiftTrade.query.order_by(ShiftTrade.created_at.desc()).all()
    return render_template('admin/shift_trades.html', trades=trades)

@availability_bp.route('/admin/overtime', methods=['GET'])
@login_required
def manage_overtime():
    if not current_user.role == 'manager':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.index'))
    
    overtimes = Overtime.query.order_by(Overtime.created_at.desc()).all()
    return render_template('admin/overtime.html', overtimes=overtimes)

# API endpoints for handling request status updates
@availability_bp.route('/api/time-off/<int:request_id>', methods=['PUT'])
@login_required
def update_time_off_status(request_id):
    if not current_user.role == 'manager':
        return jsonify({'error': 'Access denied'}), 403
    
    request = TimeOffRequest.query.get_or_404(request_id)
    data = request.json
    request.status = data.get('status')
    db.session.commit()
    return jsonify({'message': 'Status updated successfully'})

@availability_bp.route('/api/shift-trade/<int:trade_id>', methods=['PUT'])
@login_required
def update_shift_trade_status(trade_id):
    if not current_user.role == 'manager':
        return jsonify({'error': 'Access denied'}), 403
    
    trade = ShiftTrade.query.get_or_404(trade_id)
    data = request.json
    trade.status = data.get('status')
    db.session.commit()
    return jsonify({'message': 'Status updated successfully'})

@availability_bp.route('/api/overtime/<int:overtime_id>', methods=['PUT'])
@login_required
def update_overtime_status(overtime_id):
    if not current_user.role == 'manager':
        return jsonify({'error': 'Access denied'}), 403
    
    overtime = Overtime.query.get_or_404(overtime_id)
    data = request.json
    overtime.status = data.get('status')
    db.session.commit()
    return jsonify({'message': 'Status updated successfully'})
