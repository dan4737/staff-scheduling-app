from app import create_app, db
from app.models.user import User

def create_manager_account():
    app = create_app()
    with app.app_context():
        # Check if manager already exists
        manager = User.query.filter_by(username='admin').first()
        if not manager:
            manager = User(
                username='admin',
                email='admin@example.com',
                role='manager',
                is_active=True
            )
            manager.set_password('admin123')  # Default password
            db.session.add(manager)
            db.session.commit()
            print("Manager account created successfully!")
            print("Username: admin")
            print("Password: admin123")
        else:
            print("Manager account already exists!")

if __name__ == '__main__':
    create_manager_account()
