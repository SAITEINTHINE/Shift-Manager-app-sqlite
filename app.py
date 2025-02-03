import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from datetime import datetime, time, timedelta
import logging

app = Flask(__name__)
app.config.from_object(Config)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

def get_db_connection():
    try:
        conn = sqlite3.connect(Config.DATABASE)
        conn.row_factory = sqlite3.Row  # Allows accessing columns by name
        return conn
    except sqlite3.Error as e:
        logging.error(f"Database connection error: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        else:
            return "Database connection error."
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            user = cursor.fetchone()
            conn.close()
            if user and check_password_hash(user["password"], password):
                session['user_id'] = user["id"]
                return redirect(url_for('dashboard'))
            return "Invalid credentials"
        else:
            return "Database connection error."
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, date, start_time, end_time, break_start_time, break_end_time, break_time, 
                   total_hours, hourly_wage_day, hourly_wage_night, total_pay, shift_type 
            FROM shifts WHERE user_id = ?
        """, (session['user_id'],))
        shifts = cursor.fetchall()
        conn.close()
        return render_template('dashboard.html', shifts=shifts)
    else:
        return "Database connection error."

def parse_time(time_str):
    try:
        return datetime.strptime(time_str, "%H:%M").time()
    except ValueError:
        return None

def calculate_wages(start_time_obj, end_time_obj, break_start_obj, break_end_obj, hourly_wage_day, hourly_wage_night):
    night_start = time(22, 0)
    night_end = time(5, 0)

    start_datetime = datetime.combine(datetime.today(), start_time_obj)
    end_datetime = datetime.combine(datetime.today(), end_time_obj)

    # If end time is before start time, assume the shift goes past midnight
    if end_datetime <= start_datetime:
        end_datetime += timedelta(days=1)

    break_time_minutes = 0
    break_start_datetime = None
    break_end_datetime = None
    if break_start_obj and break_end_obj:
        break_start_datetime = datetime.combine(datetime.today(), break_start_obj)
        break_end_datetime = datetime.combine(datetime.today(), break_end_obj)
        
        # If break end time is before break start time, assume the break goes past midnight
        if break_end_datetime <= break_start_datetime:
            break_end_datetime += timedelta(days=1)
        
        break_time_minutes = int((break_end_datetime - break_start_datetime).total_seconds() / 60)

    # Calculate total hours worked excluding break time
    total_hours = (end_datetime - start_datetime).total_seconds() / 3600
    total_hours_after_break = max(0, total_hours - (break_time_minutes / 60))

    total_hours_day = 0
    total_hours_night = 0

    current_time = start_datetime
    while current_time < end_datetime:
        # Skip break time
        if break_start_datetime and break_end_datetime and break_start_datetime <= current_time < break_end_datetime:
            current_time += timedelta(minutes=1)
            continue

        if night_start <= current_time.time() or current_time.time() < night_end:
            total_hours_night += 1 / 60
        else:
            total_hours_day += 1 / 60
        current_time += timedelta(minutes=1)

    total_pay = (total_hours_day * hourly_wage_day) + (total_hours_night * hourly_wage_night)
    return round(total_pay, 2), break_time_minutes, round(total_hours_after_break, 2)

@app.route('/add_shift', methods=['GET', 'POST'])
def add_shift():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        date = request.form['date']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        break_start_time = request.form.get('break_start_time', None)
        break_end_time = request.form.get('break_end_time', None)
        hourly_wage_day = float(request.form['hourly_wage_day'])
        hourly_wage_night = float(request.form['hourly_wage_night'])
        shift_type = request.form['shift_type']

        start_time_obj = parse_time(start_time)
        end_time_obj = parse_time(end_time)
        break_start_obj = parse_time(break_start_time) if break_start_time else None
        break_end_obj = parse_time(break_end_time) if break_end_time else None

        total_pay, break_time_minutes, total_hours = calculate_wages(
            start_time_obj, end_time_obj, break_start_obj, break_end_obj, hourly_wage_day, hourly_wage_night
        )

        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO shifts (user_id, date, start_time, end_time, break_start_time, break_end_time, break_time, total_hours, hourly_wage_day, hourly_wage_night, total_pay, shift_type) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (session['user_id'], date, start_time, end_time, break_start_time, break_end_time, break_time_minutes, total_hours, hourly_wage_day, hourly_wage_night, total_pay, shift_type))
            
            conn.commit()
            conn.close()
            return redirect(url_for('dashboard'))
        else:
            return "Database connection error."
    
    return render_template('add_shift.html')

@app.route('/edit_shift/<int:shift_id>', methods=['GET', 'POST'])
def edit_shift(shift_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()

        if request.method == 'POST':
            date = request.form['date']
            start_time = request.form['start_time']
            end_time = request.form['end_time']
            break_start_time = request.form.get('break_start_time', None)
            break_end_time = request.form.get('break_end_time', None)
            hourly_wage_day = float(request.form['hourly_wage_day'])
            hourly_wage_night = float(request.form['hourly_wage_night'])
            shift_type = request.form['shift_type']

            start_time_obj = parse_time(start_time)
            end_time_obj = parse_time(end_time)
            break_start_obj = parse_time(break_start_time) if break_start_time else None
            break_end_obj = parse_time(break_end_time) if break_end_time else None

            total_pay, break_time_minutes, total_hours = calculate_wages(
                start_time_obj, end_time_obj, break_start_obj, break_end_obj, hourly_wage_day, hourly_wage_night
            )

            cursor.execute("""
                UPDATE shifts 
                SET date = ?, start_time = ?, end_time = ?, break_start_time = ?, break_end_time = ?, 
                    break_time = ?, total_hours = ?, hourly_wage_day = ?, hourly_wage_night = ?, total_pay = ?, shift_type = ? 
                WHERE id = ? AND user_id = ?
            """, (date, start_time, end_time, break_start_time, break_end_time, break_time_minutes, total_hours, 
                  hourly_wage_day, hourly_wage_night, total_pay, shift_type, shift_id, session['user_id']))

            conn.commit()
            conn.close()
            return redirect(url_for('dashboard'))

        cursor.execute("SELECT * FROM shifts WHERE id = ? AND user_id = ?", (shift_id, session['user_id']))
        shift = cursor.fetchone()
        conn.close()

        if not shift:
            return "Shift not found."

        return render_template('edit_shift.html', shift=shift)
    else:
        return "Database connection error."

@app.route('/delete_shift/<int:shift_id>', methods=['POST'])
def delete_shift(shift_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM shifts WHERE id = ? AND user_id = ?", (shift_id, session['user_id']))
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))
    else:
        return "Database connection error."

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)