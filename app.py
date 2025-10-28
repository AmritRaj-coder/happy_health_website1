from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'change_this_for_prod')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(300), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, pw):
        self.password_hash = generate_password_hash(pw)
    def check_password(self, pw):
        return check_password_hash(self.password_hash, pw)

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    date = db.Column(db.String(120), nullable=False)
    issue = db.Column(db.Text, nullable=False)

# admin-only decorator
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please login first.", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please login first.", "warning")
            return redirect(url_for('login'))
        user = User.query.get(session['user_id'])
        if not user or not user.is_admin:
            flash("Admin access required.", "danger")
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/contact', methods=['GET','POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name','').strip()
        email = request.form.get('email','').strip()
        message = request.form.get('message','').strip()
        if not (name and email and message):
            flash("Please fill all fields.", "warning")
            return redirect(url_for('contact'))
        c = Contact(name=name, email=email, message=message)
        db.session.add(c)
        db.session.commit()
        flash("Thank you! Your message was sent.", "success")
        return redirect(url_for('contact'))
    return render_template('contact.html')

@app.route('/appointment', methods=['GET','POST'])
def appointment():
    if request.method == 'POST':
        name = request.form.get('name','').strip()
        date = request.form.get('date','').strip()
        issue = request.form.get('issue','').strip()
        if not (name and date and issue):
            flash("Please fill all fields.", "warning")
            return redirect(url_for('appointment'))
        a = Appointment(name=name, date=date, issue=issue)
        db.session.add(a)
        db.session.commit()
        flash("Your appointment request was received.", "success")
        return redirect(url_for('appointment'))
    return render_template('appointment.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username','').strip()
        password = request.form.get('password','')
        if not username or not password:
            flash("Provide username and password", "warning")
            return redirect(url_for('register'))
        if User.query.filter_by(username=username).first():
            flash("Username already exists", "danger")
            return redirect(url_for('register'))
        user = User(username=username)
        user.set_password(password)
        # First registered user becomes admin (optional)
        if User.query.count() == 0:
            user.is_admin = True
        db.session.add(user)
        db.session.commit()
        flash("Registration successful. Please login.", "success")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username','').strip()
        password = request.form.get('password','')
        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            flash("Invalid credentials", "danger")
            return redirect(url_for('login'))
        session['user_id'] = user.id
        flash("Logged in successfully", "success")
        return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out", "info")
    return redirect(url_for('home'))

# Admin panel
@app.route('/admin')
@admin_required
def admin_panel():
    contacts = Contact.query.order_by(Contact.id.desc()).all()
    appointments = Appointment.query.order_by(Appointment.id.desc()).all()
    users = User.query.all()
    return render_template('admin.html', contacts=contacts, appointments=appointments, users=users)

# Delete endpoints (admin)
@app.route('/admin/delete_contact/<int:id>')
@admin_required
def delete_contact(id):
    c = Contact.query.get_or_404(id)
    db.session.delete(c)
    db.session.commit()
    flash("Contact deleted", "info")
    return redirect(url_for('admin_panel'))

@app.route('/admin/delete_appointment/<int:id>')
@admin_required
def delete_appointment(id):
    a = Appointment.query.get_or_404(id)
    db.session.delete(a)
    db.session.commit()
    flash("Appointment deleted", "info")
    return redirect(url_for('admin_panel'))

if __name__ == '__main__':
    app.run(debug=True)
