from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from models.user_model import create_user_profile, get_user_by_id, update_user_profile
from config import Config
import requests
import json

auth_bp = Blueprint('auth', __name__)

SUPABASE_AUTH_URL = f"{Config.SUPABASE_URL}/auth/v1"
HEADERS = {
    "apikey": Config.SUPABASE_KEY,
    "Content-Type": "application/json"
}

def supabase_signup(email, password, name, phone):
    """Call Supabase Auth REST API to sign up"""
    try:
        url = f"{SUPABASE_AUTH_URL}/signup"
        payload = {
            "email": email,
            "password": password,
            "data": {"name": name, "phone": phone}
        }
        res = requests.post(url, json=payload, headers=HEADERS)
        data = res.json()
        if res.status_code in [200, 201] and data.get("id"):
            return {"success": True, "user": data}
        else:
            msg = data.get("msg") or data.get("message") or data.get("error_description") or str(data)
            return {"success": False, "error": msg}
    except Exception as e:
        return {"success": False, "error": str(e)}

def supabase_login(email, password):
    """Call Supabase Auth REST API to sign in"""
    try:
        url = f"{SUPABASE_AUTH_URL}/token?grant_type=password"
        payload = {"email": email, "password": password}
        res = requests.post(url, json=payload, headers=HEADERS)
        data = res.json()
        if res.status_code == 200 and data.get("access_token"):
            return {"success": True, "data": data}
        else:
            msg = data.get("error_description") or data.get("msg") or data.get("message") or "Invalid credentials"
            return {"success": False, "error": msg}
    except Exception as e:
        return {"success": False, "error": str(e)}

def supabase_reset_password(email):
    """Call Supabase Auth REST API to reset password"""
    try:
        url = f"{SUPABASE_AUTH_URL}/recover"
        payload = {"email": email}
        res = requests.post(url, json=payload, headers=HEADERS)
        return res.status_code in [200, 201]
    except Exception:
        return False


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('user_id'):
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Email and password are required.', 'error')
            return render_template('login.html')

        result = supabase_login(email, password)

        if result["success"]:
            data = result["data"]
            user_data = data.get("user", {})
            user_id = user_data.get("id")

            session['user_id'] = user_id
            session['user_email'] = email
            session['access_token'] = data.get("access_token", "")

            user_profile = get_user_by_id(user_id)
            if user_profile:
                session['user_name'] = user_profile.get('name', email.split('@')[0])
                session['is_admin'] = user_profile.get('is_admin', False)
            else:
                session['user_name'] = email.split('@')[0]
                session['is_admin'] = False

            flash(f'Welcome back, {session["user_name"]}!', 'success')
            next_url = request.args.get('next', url_for('main.home'))
            return redirect(next_url)
        else:
            flash('Invalid email or password. Please try again.', 'error')

    return render_template('login.html')


@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if session.get('user_id'):
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        phone = request.form.get('phone', '').strip()

        if not all([name, email, password]):
            flash('Name, email, and password are required.', 'error')
            return render_template('signup.html')

        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('signup.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'error')
            return render_template('signup.html')

        result = supabase_signup(email, password, name, phone)

        if result["success"]:
            user = result["user"]
            user_id = user.get("id")
            if user_id:
                create_user_profile(user_id, name, email, phone)
            flash('Account created successfully! Please check your email to confirm, then log in.', 'success')
            return redirect(url_for('auth.login'))
        else:
            err = result["error"]
            if 'already registered' in str(err).lower() or 'already exists' in str(err).lower():
                flash('Email already registered. Please login.', 'error')
            else:
                flash(f'Registration failed: {err}', 'error')

    return render_template('signup.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.home'))


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        if email:
            success = supabase_reset_password(email)
            if success:
                flash('Password reset email sent! Check your inbox.', 'success')
            else:
                flash('Could not send reset email. Please try again.', 'error')
        else:
            flash('Please enter your email address.', 'error')
    return render_template('forgot_password.html')


@auth_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    if not session.get('user_id'):
        return redirect(url_for('auth.login', next=request.url))

    user_id = session['user_id']
    user = get_user_by_id(user_id)

    if request.method == 'POST':
        data = {
            'name': request.form.get('name', '').strip(),
            'phone': request.form.get('phone', '').strip(),
            'address': request.form.get('address', '').strip(),
        }
        if data['name']:
            update_user_profile(user_id, data)
            session['user_name'] = data['name']
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('auth.profile'))
        else:
            flash('Name cannot be empty.', 'error')

    return render_template('profile.html', user=user)

