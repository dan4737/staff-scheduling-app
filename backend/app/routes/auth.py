from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User
from app import db

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.role == 'manager':
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('main.dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        selected_role = request.form.get('role')  # Get the selected role
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            # Verify that the selected role matches the user's role
            if user.role == selected_role:
                login_user(user)
                flash('Logged in successfully!', 'success')
                if user.role == 'manager':
                    return redirect(url_for('admin.dashboard'))
                return redirect(url_for('main.dashboard'))
            else:
                flash('Invalid role selected for this user.', 'error')
                return redirect(url_for('auth.login'))
        
        flash('Invalid username or password', 'error')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/login.html')

@auth_bp.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('main.index'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')
        staff_id = request.form.get('staff_id')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return redirect(url_for('auth.register'))
            
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'error')
            return redirect(url_for('auth.register'))
            
        user = User(
            username=username,
            email=email,
            role=role,
            staff_id=staff_id
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')
