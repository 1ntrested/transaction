from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer as Serializer
import pyotp
from flask_login import LoginManager
from datetime import datetime


login_manager = LoginManager()
login_manager.login_view = 'login'

db = SQLAlchemy()
migrate = Migrate()



def create_app():
    app = Flask(__name__, template_folder='templates')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///p2p.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your_secret_key'

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)  # Initialize the LoginManager

    # Import your models and routes here
    # User Model
    class User(db.Model, UserMixin):
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(80), unique=True, nullable=False)
        password_hash = db.Column(db.String(120), nullable=False)
        otp_secret = db.Column(db.String(16), nullable=False)
        balance = db.Column(db.Float, default=0.0) 

        def set_password(self, password):
            self.password_hash = generate_password_hash(password)

        def check_password(self, password):
            return check_password_hash(self.password_hash, password)

        def generate_otp(self):
            totp = pyotp.TOTP(self.otp_secret)
            return totp.now()
    # expense model 
    class Expense(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
        category = db.Column(db.String(50), nullable=False)
        amount = db.Column(db.Float, nullable=False)
        timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Transaction Model
    class Transaction(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
        receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
        amount = db.Column(db.Float, nullable=False)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.route('/', methods=['GET', 'POST'])
    @login_required
    def home():
        if request.method == 'POST':
            receiver_username = request.form.get('receiver_username')
            amount = float(request.form.get('amount', 0))

            # Validate the receiver's username
            receiver = User.query.filter_by(username=receiver_username).first()

            if not receiver:
                flash('Invalid recipient username', 'error')
            elif current_user.balance < amount:
                flash('Insufficient funds', 'error')
            else:
                # Create a transaction
                transaction = Transaction(sender_id=current_user.id, receiver_id=receiver.id, amount=amount)
                db.session.add(transaction)
                # Add an expense record
                expense = Expense(user_id=current_user.id, category='groceries', amount=amount)
                db.session.add(expense)
                # Update account balances
                current_user.balance -= amount
                receiver.balance += amount

                db.session.commit()

                flash(f'Transaction successful! Sent {amount} to {receiver.username}', 'success')

        return render_template('home.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            user = User.query.filter_by(username=username).first()

            if user and user.check_password(password):
                login_user(user)
                flash('Login successful', 'success')
                return render_template('home.html')
            else:
                flash('Invalid username or password', 'error')

        return render_template('login.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('login'))

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            otp_secret = pyotp.random_base32()

            new_user = User(username=username, otp_secret=otp_secret)
            new_user.set_password(password)

            db.session.add(new_user)
            db.session.commit()

            flash('Registration successful', 'success')
            return redirect(url_for('login'))

        return render_template('register.html')
    @app.route('/deposit', methods=['GET', 'POST'])
    @login_required
    def deposit():
        if request.method == 'POST':
            amount = float(request.form.get('amount', 0))
            current_user.balance += amount
            db.session.commit()
            flash(f'Deposit successful! Added {amount} to your balance', 'success')
            return redirect(url_for('home'))  # Redirect to home after successful deposit

        return render_template('deposit.html')
    
    @app.route('/expenses/list', methods=['GET'])
    @login_required
    def expense_list():
            expenses = Expense.query.filter_by(user_id=current_user.id).all()
            return render_template('expense_list.html', expenses=expenses)  

    @app.route('/expenses/flowchart', methods=['GET'])
    @login_required
    def expense_flowchart():
         # Implement flow chart visualization logic
        # You might want to use a library like matplotlib or JavaScript charting libraries
            return render_template('expense_flowchart.html')

    
    return app

