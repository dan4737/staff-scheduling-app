from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models.schedule import Schedule
from datetime import datetime, timedelta

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'manager':
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')

@main_bp.route('/register')
def register_page():
    if current_user.is_authenticated:
        if current_user.role == 'manager':
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.register'))

@main_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'manager':
        return redirect(url_for('admin.dashboard'))
    
    # Get current week's schedules
    today = datetime.today()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=4)  # Friday
    
    schedules = Schedule.query.filter(
        Schedule.staff_id == current_user.id,
        Schedule.date >= week_start.date(),
        Schedule.date <= week_end.date()
    ).order_by(Schedule.date, Schedule.start_time).all()
    
    # Get upcoming schedules (next week)
    next_week_start = week_start + timedelta(days=7)
    next_week_end = next_week_start + timedelta(days=4)  # Friday
    
    upcoming_schedules = Schedule.query.filter(
        Schedule.staff_id == current_user.id,
        Schedule.date >= next_week_start.date(),
        Schedule.date <= next_week_end.date()
    ).order_by(Schedule.date, Schedule.start_time).all()
    
    return render_template('dashboard.html',
                         schedules=schedules,
                         upcoming_schedules=upcoming_schedules)
