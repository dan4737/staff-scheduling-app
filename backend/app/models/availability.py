from app import db
from datetime import datetime

class Availability(db.Model):
    __tablename__ = 'availabilities'
    
    id = db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)  # 0-6 for Monday-Sunday
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    
    staff = db.relationship('User', backref='availabilities')

class TimeOffRequest(db.Model):
    __tablename__ = 'time_off_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    reason = db.Column(db.String(200))
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    staff = db.relationship('User', backref='time_off_requests')

class ShiftTrade(db.Model):
    __tablename__ = 'shift_trades'
    
    id = db.Column(db.Integer, primary_key=True)
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedules.id'), nullable=False)
    requesting_staff_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    target_staff_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    schedule = db.relationship('Schedule', backref='trade_requests')
    requesting_staff = db.relationship('User', foreign_keys=[requesting_staff_id], backref='requested_trades')
    target_staff = db.relationship('User', foreign_keys=[target_staff_id], backref='received_trades')

class Overtime(db.Model):
    __tablename__ = 'overtimes'
    
    id = db.Column(db.Integer, primary_key=True)
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedules.id'), nullable=False)
    staff_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    reason = db.Column(db.String(200))
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    schedule = db.relationship('Schedule', backref='overtimes')
    staff = db.relationship('User', backref='overtimes')
